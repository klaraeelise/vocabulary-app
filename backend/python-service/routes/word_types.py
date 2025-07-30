from fastapi import APIRouter
from database import get_connection

router = APIRouter(prefix="/word_types")

@router.get("")
def get_word_types():
    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM word_types")
    types = cursor.fetchall()

    cursor.close()
    db.close()

    return types
