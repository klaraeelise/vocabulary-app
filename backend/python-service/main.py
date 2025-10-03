import os
import mysql.connector
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import get_connection
from routes import auth, words, root, languages, word_types, review, fetch
import fetchers

# Load env variables first
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()

# CORS middleware (MUST come before routers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("CORS middleware added ✅")

# Initialize dictionary fetchers
fetchers.initialize_fetchers()
print("Dictionary fetchers initialized ✅")

# Routers
app.include_router(root.router)
app.include_router(words.router)
app.include_router(auth.router)
app.include_router(languages.router)      
app.include_router(word_types.router)
app.include_router(review.router)
app.include_router(fetch.router)

@app.get("/test-db")
def test_db_connection():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "success", "result": result}
    except mysql.connector.Error as e:
        return {"status": "error", "message": str(e)}
