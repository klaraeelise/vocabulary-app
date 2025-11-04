"""
Question Review API routes for statistics and other subject learning.
Handles fetching questions for review and recording results.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, date, timedelta
from typing import Optional, List
from db_utils import get_db_cursor, logger
from auth_utils import get_current_user
from spaced_repetition import (
    calculate_next_review,
    get_next_review_date,
    determine_status,
    calculate_accuracy
)
import mysql.connector

router = APIRouter(prefix="/question-review")


class QuestionReviewSubmission(BaseModel):
    """Model for submitting a question review result."""
    question_id: int
    selected_option_id: int
    time_spent_seconds: Optional[int] = None


class AddQuestionToLearningRequest(BaseModel):
    """Model for adding a question to user's learning queue."""
    question_id: int


@router.get("/due")
def get_due_questions(
    subject_id: Optional[int] = None,
    limit: int = 20,
    user_data: dict = Depends(get_current_user)
):
    """
    Get questions that are due for review based on spaced repetition schedule.
    
    Args:
        subject_id: Optional filter by subject
        limit: Maximum number of questions to return
        user_data: Authenticated user data from JWT token
        
    Returns:
        dict: List of questions due for review with their details
    """
    user_id = user_data.get("id")
    
    try:
        with get_db_cursor(commit=False) as (db, cursor):
            # Get questions due for review
            query = """
                SELECT 
                    uqp.id as progress_id,
                    uqp.question_id,
                    uqp.status,
                    uqp.ease_factor,
                    uqp.interval_days,
                    uqp.repetitions,
                    uqp.next_review,
                    q.question_text,
                    q.question_latex,
                    q.difficulty_level,
                    q.image_url,
                    qt.type_name as question_type,
                    s.name as subject_name,
                    s.id as subject_id
                FROM user_question_progress uqp
                JOIN questions q ON uqp.question_id = q.id
                JOIN question_types qt ON q.question_type_id = qt.id
                JOIN subjects s ON q.subject_id = s.id
                WHERE uqp.user_id = %s 
                AND (uqp.next_review IS NULL OR uqp.next_review <= NOW())
                AND uqp.status != 'mastered'
            """
            params = [user_id]
            
            if subject_id:
                query += " AND q.subject_id = %s"
                params.append(subject_id)
            
            query += " ORDER BY uqp.next_review ASC, uqp.created_at ASC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, tuple(params))
            questions = cursor.fetchall()
            
            # For each question, get its answer options
            for question in questions:
                cursor.execute("""
                    SELECT id, option_text, option_latex
                    FROM answer_options
                    WHERE question_id = %s
                    ORDER BY id
                """, (question['question_id'],))
                question['options'] = cursor.fetchall()
            
            return {
                "questions": questions,
                "count": len(questions),
                "user_id": user_id
            }
            
    except mysql.connector.Error as e:
        logger.error(f"Database error fetching due questions: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.get("/new")
def get_new_questions(
    subject_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    limit: int = 10,
    user_data: dict = Depends(get_current_user)
):
    """
    Get questions that the user hasn't started learning yet.
    
    Args:
        subject_id: Optional filter by subject
        difficulty: Optional filter by difficulty
        limit: Maximum number of questions to return
        user_data: Authenticated user data from JWT token
        
    Returns:
        dict: List of new questions not yet in user's learning queue
    """
    user_id = user_data.get("id")
    
    try:
        with get_db_cursor(commit=False) as (db, cursor):
            # Get questions not in user's progress table
            query = """
                SELECT q.id, q.question_text, q.question_latex, q.difficulty_level,
                       q.image_url, qt.type_name as question_type,
                       s.name as subject_name, s.id as subject_id
                FROM questions q
                JOIN question_types qt ON q.question_type_id = qt.id
                JOIN subjects s ON q.subject_id = s.id
                WHERE q.id NOT IN (
                    SELECT question_id FROM user_question_progress WHERE user_id = %s
                )
            """
            params = [user_id]
            
            if subject_id:
                query += " AND q.subject_id = %s"
                params.append(subject_id)
            
            if difficulty:
                query += " AND q.difficulty_level = %s"
                params.append(difficulty)
            
            query += " ORDER BY RAND() LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, tuple(params))
            questions = cursor.fetchall()
            
            # Get answer options for each question
            for question in questions:
                cursor.execute("""
                    SELECT id, option_text, option_latex
                    FROM answer_options
                    WHERE question_id = %s
                    ORDER BY id
                """, (question['id'],))
                question['options'] = cursor.fetchall()
            
            return {
                "questions": questions,
                "count": len(questions)
            }
            
    except mysql.connector.Error as e:
        logger.error(f"Database error fetching new questions: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.post("/add-question")
def add_question_to_learning(
    data: AddQuestionToLearningRequest,
    user_data: dict = Depends(get_current_user)
):
    """
    Add a question to the user's learning queue.
    
    Args:
        data: Question ID to add
        user_data: Authenticated user data from JWT token
        
    Returns:
        dict: Success message
    """
    user_id = user_data.get("id")
    
    try:
        with get_db_cursor() as (db, cursor):
            # Check if question exists
            cursor.execute("SELECT id FROM questions WHERE id = %s", (data.question_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Question not found")
            
            # Check if already in learning queue
            cursor.execute(
                "SELECT id FROM user_question_progress WHERE user_id = %s AND question_id = %s",
                (user_id, data.question_id)
            )
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Question already in learning queue")
            
            # Add to user_question_progress with default values
            cursor.execute("""
                INSERT INTO user_question_progress 
                (user_id, question_id, status, next_review)
                VALUES (%s, %s, 'new', NOW())
            """, (user_id, data.question_id))
            
            logger.info(f"User {user_id} added question {data.question_id} to learning queue")
            
            return {"message": "Question added to learning queue successfully"}
            
    except HTTPException:
        raise
    except mysql.connector.Error as e:
        logger.error(f"Database error adding question to learning: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.post("/submit")
def submit_question_review(
    data: QuestionReviewSubmission,
    user_data: dict = Depends(get_current_user)
):
    """
    Submit a question review result and update spaced repetition schedule.
    
    Args:
        data: Review submission with question_id and selected_option_id
        user_data: Authenticated user data from JWT token
        
    Returns:
        dict: Updated progress information and feedback
    """
    user_id = user_data.get("id")
    
    try:
        with get_db_cursor() as (db, cursor):
            # Get current progress
            cursor.execute("""
                SELECT id, ease_factor, interval_days, repetitions, 
                       review_count, correct_count
                FROM user_question_progress
                WHERE user_id = %s AND question_id = %s
            """, (user_id, data.question_id))
            
            progress = cursor.fetchone()
            if not progress:
                raise HTTPException(status_code=404, detail="Question not found in learning queue")
            
            # Check if answer is correct
            cursor.execute("""
                SELECT is_correct, explanation, option_text
                FROM answer_options
                WHERE id = %s AND question_id = %s
            """, (data.selected_option_id, data.question_id))
            
            selected_option = cursor.fetchone()
            if not selected_option:
                raise HTTPException(status_code=400, detail="Invalid option selected")
            
            is_correct = selected_option['is_correct']
            
            # Get correct answer for feedback
            cursor.execute("""
                SELECT id, option_text, explanation
                FROM answer_options
                WHERE question_id = %s AND is_correct = TRUE
            """, (data.question_id,))
            correct_answer = cursor.fetchone()
            
            # Get question explanation
            cursor.execute("""
                SELECT explanation
                FROM questions
                WHERE id = %s
            """, (data.question_id,))
            question_data = cursor.fetchone()
            
            # Convert to quality rating (5 for correct, 1 for incorrect)
            quality = 5 if is_correct else 1
            
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
            new_correct_count = progress['correct_count'] + (1 if is_correct else 0)
            
            cursor.execute("""
                UPDATE user_question_progress
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
            
            logger.info(f"User {user_id} reviewed question {data.question_id}: {is_correct}")
            
            accuracy = calculate_accuracy(new_correct_count, new_review_count)
            
            return {
                "message": "Review submitted successfully",
                "correct": is_correct,
                "selected_option": selected_option['option_text'],
                "correct_answer": correct_answer['option_text'] if correct_answer else None,
                "correct_answer_id": correct_answer['id'] if correct_answer else None,
                "option_explanation": selected_option.get('explanation'),
                "question_explanation": question_data['explanation'] if question_data else None,
                "next_review": next_review_date.isoformat(),
                "interval_days": new_interval_days,
                "status": new_status,
                "accuracy": round(accuracy, 1)
            }
            
    except HTTPException:
        raise
    except mysql.connector.Error as e:
        logger.error(f"Database error submitting question review: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.get("/stats")
def get_question_stats(
    subject_id: Optional[int] = None,
    user_data: dict = Depends(get_current_user)
):
    """
    Get user's learning statistics for questions.
    
    Args:
        subject_id: Optional filter by subject
        user_data: Authenticated user data from JWT token
        
    Returns:
        dict: User statistics for question learning
    """
    user_id = user_data.get("id")
    
    try:
        with get_db_cursor(commit=False) as (db, cursor):
            # Base query
            query = """
                SELECT 
                    COUNT(*) as total_questions,
                    SUM(review_count) as total_reviews,
                    SUM(correct_count) as total_correct,
                    SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new_count,
                    SUM(CASE WHEN status = 'learning' THEN 1 ELSE 0 END) as learning_count,
                    SUM(CASE WHEN status = 'review' THEN 1 ELSE 0 END) as review_count,
                    SUM(CASE WHEN status = 'mastered' THEN 1 ELSE 0 END) as mastered_count
                FROM user_question_progress uqp
            """
            
            if subject_id:
                query += """
                    JOIN questions q ON uqp.question_id = q.id
                    WHERE uqp.user_id = %s AND q.subject_id = %s
                """
                params = (user_id, subject_id)
            else:
                query += " WHERE uqp.user_id = %s"
                params = (user_id,)
            
            cursor.execute(query, params)
            stats = cursor.fetchone()
            
            if not stats or stats['total_questions'] == 0:
                return {
                    "total_questions": 0,
                    "total_reviews": 0,
                    "accuracy": 0.0,
                    "status_breakdown": {
                        "new": 0,
                        "learning": 0,
                        "review": 0,
                        "mastered": 0
                    }
                }
            
            # Calculate overall accuracy
            accuracy = calculate_accuracy(
                stats['total_correct'] or 0,
                stats['total_reviews'] or 0
            )
            
            return {
                "total_questions": stats['total_questions'],
                "total_reviews": stats['total_reviews'],
                "total_correct": stats['total_correct'],
                "accuracy": round(accuracy, 1),
                "status_breakdown": {
                    "new": stats['new_count'],
                    "learning": stats['learning_count'],
                    "review": stats['review_count'],
                    "mastered": stats['mastered_count']
                }
            }
            
    except mysql.connector.Error as e:
        logger.error(f"Database error fetching question stats: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
