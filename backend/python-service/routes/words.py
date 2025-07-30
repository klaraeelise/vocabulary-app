from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_connection

router = APIRouter(prefix="/words")

class Meaning(BaseModel):
    language_id: int
    definition: str
    note: str | None = None

class AddWordRequest(BaseModel):
    word: str
    wordtype_id: int
    language_id: int
    meanings: list[Meaning]

@router.post("/add")
def add_word(data: AddWordRequest):
    db = get_connection()
    cursor = db.cursor()

    # Insert word
    cursor.execute(
        "INSERT INTO words (word, wordtype, language) VALUES (%s, %s, %s)",
        (data.word, data.wordtype_id, data.language_id),
    )
    word_id = cursor.lastrowid

    # Insert meanings
    for meaning in data.meanings:
        cursor.execute(
            "INSERT INTO meanings (word_id, language_id, definition, note) VALUES (%s, %s, %s, %s)",
            (word_id, meaning.language_id, meaning.definition, meaning.note),
        )

    db.commit()
    cursor.close()
    db.close()

    return {"message": "Word added successfully", "word_id": word_id}
