"""
Spaced Repetition System using SuperMemo 2 (SM-2) Algorithm.

The SM-2 algorithm calculates optimal review intervals based on:
- Quality of recall (0-5, where 3+ is successful)
- Current ease factor
- Number of successful repetitions

References:
- https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
"""
from datetime import datetime, timedelta
from typing import Tuple
import math


def calculate_next_review(
    quality: int,
    ease_factor: float,
    interval_days: int,
    repetitions: int
) -> Tuple[float, int, int]:
    """
    Calculate the next review parameters using SM-2 algorithm.
    
    Args:
        quality: Quality of recall (0-5)
            5: Perfect response
            4: Correct response after hesitation
            3: Correct response with difficulty
            2: Incorrect, but easy to recall
            1: Incorrect, but familiar
            0: Complete blackout
        ease_factor: Current ease factor (minimum 1.3)
        interval_days: Current interval in days
        repetitions: Number of consecutive successful repetitions
        
    Returns:
        Tuple[float, int, int]: (new_ease_factor, new_interval_days, new_repetitions)
    """
    # Validate quality
    quality = max(0, min(5, quality))
    
    # Calculate new ease factor
    new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    
    # Ensure ease factor doesn't go below 1.3
    new_ease_factor = max(1.3, new_ease_factor)
    
    # If quality < 3, reset repetitions (incorrect answer)
    if quality < 3:
        new_repetitions = 0
        new_interval_days = 1  # Review again tomorrow
    else:
        # Correct answer
        new_repetitions = repetitions + 1
        
        if new_repetitions == 1:
            new_interval_days = 1
        elif new_repetitions == 2:
            new_interval_days = 6
        else:
            new_interval_days = math.ceil(interval_days * new_ease_factor)
    
    return new_ease_factor, new_interval_days, new_repetitions


def get_next_review_date(interval_days: int) -> datetime:
    """
    Calculate the next review date based on interval.
    
    Args:
        interval_days: Number of days until next review
        
    Returns:
        datetime: Next review date/time
    """
    return datetime.now() + timedelta(days=interval_days)


def determine_status(interval_days: int, ease_factor: float, repetitions: int) -> str:
    """
    Determine the learning status based on progress metrics.
    
    Args:
        interval_days: Current interval in days
        ease_factor: Current ease factor
        repetitions: Number of successful repetitions
        
    Returns:
        str: Status ('new', 'learning', 'review', or 'mastered')
    """
    if repetitions == 0:
        return 'new'
    elif interval_days < 7:
        return 'learning'
    elif interval_days > 30 and ease_factor > 2.5 and repetitions >= 5:
        return 'mastered'
    else:
        return 'review'


def calculate_accuracy(correct_count: int, review_count: int) -> float:
    """
    Calculate review accuracy percentage.
    
    Args:
        correct_count: Number of correct reviews
        review_count: Total number of reviews
        
    Returns:
        float: Accuracy percentage (0-100)
    """
    if review_count == 0:
        return 0.0
    return (correct_count / review_count) * 100


def quality_from_user_response(correct: bool, difficulty: str = "medium") -> int:
    """
    Convert user response to SM-2 quality rating.
    
    Args:
        correct: Whether the answer was correct
        difficulty: Difficulty level ("easy", "medium", "hard")
        
    Returns:
        int: Quality rating (0-5)
    """
    if not correct:
        return 1  # Incorrect but familiar
    
    # Map difficulty to quality for correct answers
    difficulty_map = {
        "easy": 5,      # Perfect response
        "medium": 4,    # Correct after hesitation
        "hard": 3       # Correct with difficulty
    }
    
    return difficulty_map.get(difficulty, 4)
