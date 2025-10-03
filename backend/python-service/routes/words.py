from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from database import get_connection
from db_utils import get_db_cursor, validate_required_fields, check_duplicate, logger
import mysql.connector

router = APIRouter(prefix="/words")

class Meaning(BaseModel):
    language_id: int
    definition: str
    note: str | None = None
    
    @validator('definition')
    def definition_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Definition cannot be empty')
        return v.strip()

class AddWordRequest(BaseModel):
    word: str
    wordtype_id: int
    language_id: int
    meanings: list[Meaning]
    
    @validator('word')
    def word_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Word cannot be empty')
        return v.strip()
    
    @validator('meanings')
    def meanings_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one meaning is required')
        return v

@router.post("/add")
def add_word(data: AddWordRequest):
    """
    Add a new word with meanings to the database.
    Uses transaction management to ensure all-or-nothing insertion.
    
    Args:
        data: AddWordRequest with word, wordtype_id, language_id, and meanings
        
    Returns:
        dict: Success message with word_id
        
    Raises:
        HTTPException: If validation fails or database error occurs
    """
    try:
        # Use context manager for automatic transaction management
        with get_db_cursor() as (db, cursor):
            # Check if word already exists for this language
            cursor.execute(
                "SELECT id FROM words WHERE word = %s AND language = %s",
                (data.word, data.language_id)
            )
            existing_word = cursor.fetchone()
            
            if existing_word:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Word '{data.word}' already exists in this language. Use update endpoint to modify."
                )
            
            # Verify that language exists
            cursor.execute("SELECT id FROM languages WHERE id = %s", (data.language_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail=f"Language ID {data.language_id} does not exist")
            
            # Verify that word type exists
            cursor.execute("SELECT id FROM word_types WHERE id = %s", (data.wordtype_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail=f"Word type ID {data.wordtype_id} does not exist")
            
            # Insert word
            cursor.execute(
                "INSERT INTO words (word, wordtype, language) VALUES (%s, %s, %s)",
                (data.word, data.wordtype_id, data.language_id),
            )
            word_id = cursor.lastrowid
            logger.info(f"Inserted word '{data.word}' with ID {word_id}")
            
            # Insert meanings
            for idx, meaning in enumerate(data.meanings):
                # Verify meaning language exists
                cursor.execute("SELECT id FROM languages WHERE id = %s", (meaning.language_id,))
                if not cursor.fetchone():
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Language ID {meaning.language_id} for meaning {idx+1} does not exist"
                    )
                
                cursor.execute(
                    "INSERT INTO meanings (word_id, language_id, definition, note) VALUES (%s, %s, %s, %s)",
                    (word_id, meaning.language_id, meaning.definition, meaning.note),
                )
                logger.info(f"Inserted meaning {idx+1} for word ID {word_id}")
            
            # Transaction is automatically committed by the context manager
            return {
                "message": "Word added successfully", 
                "word_id": word_id,
                "meanings_count": len(data.meanings)
            }
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except mysql.connector.IntegrityError as e:
        logger.error(f"Integrity error adding word: {e}")
        raise HTTPException(status_code=400, detail="Database integrity error. Check your data.")
    except mysql.connector.Error as e:
        logger.error(f"Database error adding word: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error adding word: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/{word_id}")
def get_word(word_id: int):
    """
    Retrieve a word and its meanings by ID.
    
    Args:
        word_id: ID of the word to retrieve
        
    Returns:
        dict: Word information with meanings
    """
    try:
        with get_db_cursor(commit=False) as (db, cursor):
            # Get word details
            cursor.execute("""
                SELECT w.id, w.word, w.wordtype, w.language,
                       wt.wordtype as wordtype_name,
                       l.language as language_name
                FROM words w
                LEFT JOIN word_types wt ON w.wordtype = wt.id
                LEFT JOIN languages l ON w.language = l.id
                WHERE w.id = %s
            """, (word_id,))
            
            word = cursor.fetchone()
            if not word:
                raise HTTPException(status_code=404, detail="Word not found")
            
            # Get meanings
            cursor.execute("""
                SELECT m.id, m.definition, m.note, m.language_id,
                       l.language as language_name
                FROM meanings m
                LEFT JOIN languages l ON m.language_id = l.id
                WHERE m.word_id = %s
            """, (word_id,))
            
            meanings = cursor.fetchall()
            
            return {
                **word,
                "meanings": meanings
            }
            
    except HTTPException:
        raise
    except mysql.connector.Error as e:
        logger.error(f"Database error retrieving word {word_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.get("/")
def list_words(language_id: int = None, limit: int = 50, offset: int = 0):
    """
    List all words, optionally filtered by language.
    
    Args:
        language_id: Optional language ID to filter by
        limit: Maximum number of words to return (default 50)
        offset: Number of words to skip (for pagination)
        
    Returns:
        dict: List of words with pagination info
    """
    try:
        with get_db_cursor(commit=False) as (db, cursor):
            # Build query
            if language_id:
                query = """
                    SELECT w.id, w.word, wt.wordtype as wordtype_name, l.language as language_name
                    FROM words w
                    LEFT JOIN word_types wt ON w.wordtype = wt.id
                    LEFT JOIN languages l ON w.language = l.id
                    WHERE w.language = %s
                    ORDER BY w.word
                    LIMIT %s OFFSET %s
                """
                params = (language_id, limit, offset)
                
                # Get total count
                cursor.execute("SELECT COUNT(*) as count FROM words WHERE language = %s", (language_id,))
            else:
                query = """
                    SELECT w.id, w.word, wt.wordtype as wordtype_name, l.language as language_name
                    FROM words w
                    LEFT JOIN word_types wt ON w.wordtype = wt.id
                    LEFT JOIN languages l ON w.language = l.id
                    ORDER BY w.word
                    LIMIT %s OFFSET %s
                """
                params = (limit, offset)
                
                # Get total count
                cursor.execute("SELECT COUNT(*) as count FROM words")
            
            total_result = cursor.fetchone()
            total = total_result['count'] if total_result else 0
            
            # Get words
            cursor.execute(query, params)
            words = cursor.fetchall()
            
            return {
                "words": words,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
            
    except mysql.connector.Error as e:
        logger.error(f"Database error listing words: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
