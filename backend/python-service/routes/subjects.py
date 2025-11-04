"""
Statistics and Subject API routes.
Handles fetching subjects, questions, and learning operations.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from db_utils import get_db_cursor, logger
from auth_utils import get_current_user
import mysql.connector

router = APIRouter(prefix="/subjects")


@router.get("/")
def get_subjects():
    """
    Get all available subjects.
    
    Returns:
        dict: List of subjects with their details
    """
    try:
        with get_db_cursor(commit=False) as (db, cursor):
            cursor.execute("""
                SELECT id, name, code, description, created_at
                FROM subjects
                ORDER BY name
            """)
            subjects = cursor.fetchall()
            
            # Get question count for each subject
            for subject in subjects:
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM questions
                    WHERE subject_id = %s
                """, (subject['id'],))
                result = cursor.fetchone()
                subject['question_count'] = result['count'] if result else 0
            
            return {
                "subjects": subjects,
                "count": len(subjects)
            }
            
    except mysql.connector.Error as e:
        logger.error(f"Database error fetching subjects: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.get("/{subject_id}")
def get_subject_details(subject_id: int):
    """
    Get details about a specific subject.
    
    Args:
        subject_id: Subject ID
        
    Returns:
        dict: Subject details with statistics
    """
    try:
        with get_db_cursor(commit=False) as (db, cursor):
            cursor.execute("""
                SELECT id, name, code, description, created_at
                FROM subjects
                WHERE id = %s
            """, (subject_id,))
            
            subject = cursor.fetchone()
            if not subject:
                raise HTTPException(status_code=404, detail="Subject not found")
            
            # Get question statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN difficulty_level = 'beginner' THEN 1 ELSE 0 END) as beginner,
                    SUM(CASE WHEN difficulty_level = 'intermediate' THEN 1 ELSE 0 END) as intermediate,
                    SUM(CASE WHEN difficulty_level = 'advanced' THEN 1 ELSE 0 END) as advanced
                FROM questions
                WHERE subject_id = %s
            """, (subject_id,))
            
            stats = cursor.fetchone()
            subject['statistics'] = stats
            
            return subject
            
    except HTTPException:
        raise
    except mysql.connector.Error as e:
        logger.error(f"Database error fetching subject details: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.get("/{subject_id}/questions")
def get_subject_questions(
    subject_id: int,
    difficulty: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    """
    Get questions for a subject with optional filtering.
    
    Args:
        subject_id: Subject ID
        difficulty: Optional difficulty filter (beginner/intermediate/advanced)
        limit: Maximum number of questions to return
        offset: Number of questions to skip
        
    Returns:
        dict: List of questions with answer options
    """
    try:
        with get_db_cursor(commit=False) as (db, cursor):
            # Verify subject exists
            cursor.execute("SELECT id FROM subjects WHERE id = %s", (subject_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Subject not found")
            
            # Build query
            query = """
                SELECT q.id, q.question_text, q.question_latex, q.explanation,
                       q.difficulty_level, q.image_url, qt.type_name as question_type
                FROM questions q
                JOIN question_types qt ON q.question_type_id = qt.id
                WHERE q.subject_id = %s
            """
            params = [subject_id]
            
            if difficulty:
                query += " AND q.difficulty_level = %s"
                params.append(difficulty)
            
            query += " ORDER BY RAND() LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, tuple(params))
            questions = cursor.fetchall()
            
            # Get answer options for each question
            for question in questions:
                cursor.execute("""
                    SELECT id, option_text, option_latex, is_correct, explanation
                    FROM answer_options
                    WHERE question_id = %s
                    ORDER BY id
                """, (question['id'],))
                question['options'] = cursor.fetchall()
                
                # For client-side, remove is_correct flag (they shouldn't see the answer yet)
                for option in question['options']:
                    option['is_correct_hidden'] = option.pop('is_correct')
            
            return {
                "questions": questions,
                "count": len(questions)
            }
            
    except HTTPException:
        raise
    except mysql.connector.Error as e:
        logger.error(f"Database error fetching questions: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
