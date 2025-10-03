"""
Review API routes for spaced repetition learning system.
Handles fetching words for review and recording review results.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, validator
from datetime import datetime, date
from typing import Optional, List
from db_utils import get_db_cursor, logger
from auth_utils import get_current_user
from spaced_repetition import (
    calculate_next_review, 
    get_next_review_date, 
    determine_status,
    quality_from_user_response,
    calculate_accuracy
)
import mysql.connector

router = APIRouter(prefix="/review")


class ReviewSubmission(BaseModel):
    """Model for submitting a review result."""
    word_id: int
    correct: bool
    difficulty: str = "medium"  # "easy", "medium", or "hard"
    
    @validator('difficulty')
    def validate_difficulty(cls, v):
        if v not in ["easy", "medium", "hard"]:
            raise ValueError('Difficulty must be "easy", "medium", or "hard"')
        return v


class AddToLearningRequest(BaseModel):
    """Model for adding a word to user's learning queue."""
    word_id: int


@router.get("/due")
def get_due_words(
    limit: int = 20,
    user_data: dict = Depends(get_current_user)
):
    """
    Get words that are due for review based on spaced repetition schedule.
    
    Args:
        limit: Maximum number of words to return
        user_data: Authenticated user data from JWT token
        
    Returns:
        dict: List of words due for review with their details
    """
    user_id = user_data.get("id")
    
    try:
        with get_db_cursor(commit=False) as (db, cursor):
            # Get words due for review (where next_review is null or in the past)
            query = """
                SELECT 
                    up.id as progress_id,
                    up.word_id,
                    up.status,
                    up.ease_factor,
                    up.interval_days,
                    up.repetitions,
                    up.next_review,
                    w.word,
                    wt.wordtype as wordtype_name,
                    l.language as language_name,
                    w.language as language_id
                FROM user_progress up
                JOIN words w ON up.word_id = w.id
                LEFT JOIN word_types wt ON w.wordtype = wt.id
                LEFT JOIN languages l ON w.language = l.id
                WHERE up.user_id = %s 
                AND (up.next_review IS NULL OR up.next_review <= NOW())
                AND up.status != 'mastered'
                ORDER BY up.next_review ASC, up.created_at ASC
                LIMIT %s
            """
            
            cursor.execute(query, (user_id, limit))
            words = cursor.fetchall()
            
            # For each word, get its meanings
            for word in words:
                cursor.execute("""
                    SELECT m.id, m.definition, m.note, m.language_id,
                           l.language as language_name
                    FROM meanings m
                    LEFT JOIN languages l ON m.language_id = l.id
                    WHERE m.word_id = %s
                """, (word['word_id'],))
                
                word['meanings'] = cursor.fetchall()
            
            return {
                "words": words,
                "count": len(words),
                "user_id": user_id
            }
            
    except mysql.connector.Error as e:
        logger.error(f"Database error fetching due words: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.get("/new")
def get_new_words(
    language_id: Optional[int] = None,
    limit: int = 10,
    user_data: dict = Depends(get_current_user)
):
    """
    Get words that the user hasn't started learning yet.
    
    Args:
        language_id: Optional filter by language
        limit: Maximum number of words to return
        user_data: Authenticated user data from JWT token
        
    Returns:
        dict: List of new words not yet in user's learning queue
    """
    user_id = user_data.get("id")
    
    try:
        with get_db_cursor(commit=False) as (db, cursor):
            # Get words not in user's progress table
            if language_id:
                query = """
                    SELECT w.id, w.word, wt.wordtype as wordtype_name, 
                           l.language as language_name, w.language as language_id
                    FROM words w
                    LEFT JOIN word_types wt ON w.wordtype = wt.id
                    LEFT JOIN languages l ON w.language = l.id
                    WHERE w.id NOT IN (
                        SELECT word_id FROM user_progress WHERE user_id = %s
                    )
                    AND w.language = %s
                    ORDER BY w.created_at DESC
                    LIMIT %s
                """
                params = (user_id, language_id, limit)
            else:
                query = """
                    SELECT w.id, w.word, wt.wordtype as wordtype_name, 
                           l.language as language_name, w.language as language_id
                    FROM words w
                    LEFT JOIN word_types wt ON w.wordtype = wt.id
                    LEFT JOIN languages l ON w.language = l.id
                    WHERE w.id NOT IN (
                        SELECT word_id FROM user_progress WHERE user_id = %s
                    )
                    ORDER BY w.created_at DESC
                    LIMIT %s
                """
                params = (user_id, limit)
            
            cursor.execute(query, params)
            words = cursor.fetchall()
            
            # Get meanings for each word
            for word in words:
                cursor.execute("""
                    SELECT m.id, m.definition, m.note, m.language_id,
                           l.language as language_name
                    FROM meanings m
                    LEFT JOIN languages l ON m.language_id = l.id
                    WHERE m.word_id = %s
                """, (word['id'],))
                
                word['meanings'] = cursor.fetchall()
            
            return {
                "words": words,
                "count": len(words)
            }
            
    except mysql.connector.Error as e:
        logger.error(f"Database error fetching new words: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.post("/add-word")
def add_word_to_learning(
    data: AddToLearningRequest,
    user_data: dict = Depends(get_current_user)
):
    """
    Add a word to the user's learning queue.
    
    Args:
        data: Word ID to add
        user_data: Authenticated user data from JWT token
        
    Returns:
        dict: Success message
    """
    user_id = user_data.get("id")
    
    try:
        with get_db_cursor() as (db, cursor):
            # Check if word exists
            cursor.execute("SELECT id FROM words WHERE id = %s", (data.word_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Word not found")
            
            # Check if already in learning queue
            cursor.execute(
                "SELECT id FROM user_progress WHERE user_id = %s AND word_id = %s",
                (user_id, data.word_id)
            )
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Word already in learning queue")
            
            # Add to user_progress with default values
            cursor.execute("""
                INSERT INTO user_progress 
                (user_id, word_id, status, next_review)
                VALUES (%s, %s, 'new', NOW())
            """, (user_id, data.word_id))
            
            logger.info(f"User {user_id} added word {data.word_id} to learning queue")
            
            # Initialize user statistics if not exists
            cursor.execute("""
                INSERT INTO user_statistics (user_id, words_learned)
                VALUES (%s, 1)
                ON DUPLICATE KEY UPDATE words_learned = words_learned + 1
            """, (user_id,))
            
            return {"message": "Word added to learning queue successfully"}
            
    except HTTPException:
        raise
    except mysql.connector.Error as e:
        logger.error(f"Database error adding word to learning: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.post("/submit")
def submit_review(
    data: ReviewSubmission,
    user_data: dict = Depends(get_current_user)
):
    """
    Submit a review result and update spaced repetition schedule.
    
    Args:
        data: Review submission with word_id, correct, and difficulty
        user_data: Authenticated user data from JWT token
        
    Returns:
        dict: Updated progress information and next review date
    """
    user_id = user_data.get("id")
    
    try:
        with get_db_cursor() as (db, cursor):
            # Get current progress
            cursor.execute("""
                SELECT id, ease_factor, interval_days, repetitions, 
                       review_count, correct_count
                FROM user_progress
                WHERE user_id = %s AND word_id = %s
            """, (user_id, data.word_id))
            
            progress = cursor.fetchone()
            if not progress:
                raise HTTPException(status_code=404, detail="Word not found in learning queue")
            
            # Convert user response to quality rating
            quality = quality_from_user_response(data.correct, data.difficulty)
            
            # Calculate next review using SM-2 algorithm
            new_ease_factor, new_interval_days, new_repetitions = calculate_next_review(
                quality,
                progress['ease_factor'],
                progress['interval_days'],
                progress['repetitions']
            )
            
            # Calculate next review date
            next_review_date = get_next_review_date(new_interval_days)
            
            # Determine new status
            new_status = determine_status(new_interval_days, new_ease_factor, new_repetitions)
            
            # Update progress
            new_review_count = progress['review_count'] + 1
            new_correct_count = progress['correct_count'] + (1 if data.correct else 0)
            
            cursor.execute("""
                UPDATE user_progress
                SET ease_factor = %s,
                    interval_days = %s,
                    repetitions = %s,
                    review_count = %s,
                    correct_count = %s,
                    last_reviewed = NOW(),
                    next_review = %s,
                    status = %s
                WHERE id = %s
            """, (
                new_ease_factor, new_interval_days, new_repetitions,
                new_review_count, new_correct_count,
                next_review_date, new_status,
                progress['id']
            ))
            
            logger.info(f"User {user_id} reviewed word {data.word_id}: {data.correct}")
            
            # Update user statistics
            today = date.today()
            cursor.execute("""
                SELECT last_review_date, current_streak FROM user_statistics
                WHERE user_id = %s
            """, (user_id,))
            stats = cursor.fetchone()
            
            if stats:
                last_date = stats['last_review_date']
                current_streak = stats['current_streak']
                
                # Update streak
                if last_date == today:
                    # Already reviewed today, don't change streak
                    new_streak = current_streak
                elif last_date == today - timedelta(days=1):
                    # Reviewed yesterday, increment streak
                    new_streak = current_streak + 1
                else:
                    # Streak broken, reset to 1
                    new_streak = 1
                
                cursor.execute("""
                    UPDATE user_statistics
                    SET total_reviews = total_reviews + 1,
                        correct_reviews = correct_reviews + %s,
                        current_streak = %s,
                        longest_streak = GREATEST(longest_streak, %s),
                        last_review_date = %s,
                        words_mastered = (
                            SELECT COUNT(*) FROM user_progress 
                            WHERE user_id = %s AND status = 'mastered'
                        )
                    WHERE user_id = %s
                """, (
                    1 if data.correct else 0,
                    new_streak, new_streak, today,
                    user_id, user_id
                ))
            
            accuracy = calculate_accuracy(new_correct_count, new_review_count)
            
            return {
                "message": "Review submitted successfully",
                "next_review": next_review_date.isoformat(),
                "interval_days": new_interval_days,
                "status": new_status,
                "accuracy": round(accuracy, 1),
                "streak_info": {
                    "current_streak": new_streak if stats else 1
                }
            }
            
    except HTTPException:
        raise
    except mysql.connector.Error as e:
        logger.error(f"Database error submitting review: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.get("/stats")
def get_user_stats(user_data: dict = Depends(get_current_user)):
    """
    Get user's learning statistics.
    
    Args:
        user_data: Authenticated user data from JWT token
        
    Returns:
        dict: User statistics including progress, accuracy, and streaks
    """
    user_id = user_data.get("id")
    
    try:
        with get_db_cursor(commit=False) as (db, cursor):
            # Get aggregated statistics
            cursor.execute("""
                SELECT * FROM user_statistics WHERE user_id = %s
            """, (user_id,))
            stats = cursor.fetchone()
            
            if not stats:
                # Initialize statistics if not exists
                cursor.execute("""
                    INSERT INTO user_statistics (user_id) VALUES (%s)
                """, (user_id,))
                db.commit()
                stats = {
                    'words_learned': 0,
                    'words_mastered': 0,
                    'total_reviews': 0,
                    'correct_reviews': 0,
                    'current_streak': 0,
                    'longest_streak': 0
                }
            
            # Get status breakdown
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM user_progress
                WHERE user_id = %s
                GROUP BY status
            """, (user_id,))
            status_breakdown = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Calculate overall accuracy
            accuracy = calculate_accuracy(
                stats.get('correct_reviews', 0),
                stats.get('total_reviews', 0)
            )
            
            return {
                **stats,
                "accuracy": round(accuracy, 1),
                "status_breakdown": status_breakdown
            }
            
    except mysql.connector.Error as e:
        logger.error(f"Database error fetching user stats: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
