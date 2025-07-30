from fastapi import APIRouter
from database import get_connection

router = APIRouter(prefix="/languages")

@router.get("")
def get_languages():
    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM languages")
    languages = cursor.fetchall()

    cursor.close()
    db.close()

    return languages
