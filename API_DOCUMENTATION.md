# API Documentation

## Base URL
- **Python Service**: `http://localhost:8000`
- **Go Service**: `http://localhost:8080`

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

Tokens expire after 24 hours. When a token expires, the user must log in again.

---

## Authentication Endpoints

### POST `/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "type": "basic"
}
```

**Response:**
```json
{
  "message": "User registered successfully"
}
```

### POST `/auth/login`
Log in and receive a JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2024-12-10T15:30:00"
}
```

### GET `/auth/verify`
Verify if current token is still valid. **Requires authentication.**

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "valid": true,
  "user_id": 1,
  "email": "user@example.com",
  "type": "basic"
}
```

---

## Word Management Endpoints

### POST `/words/add`
Add a new word with meanings to the database.

**Request Body:**
```json
{
  "word": "hello",
  "wordtype_id": 1,
  "language_id": 2,
  "meanings": [
    {
      "language_id": 1,
      "definition": "hei, hallo",
      "note": "Informal greeting"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Word added successfully",
  "word_id": 42,
  "meanings_count": 1
}
```

### GET `/words/{word_id}`
Retrieve a word and its meanings by ID.

**Response:**
```json
{
  "id": 42,
  "word": "hello",
  "wordtype": 1,
  "wordtype_name": "noun",
  "language": 2,
  "language_name": "English",
  "meanings": [
    {
      "id": 100,
      "definition": "hei, hallo",
      "note": "Informal greeting",
      "language_id": 1,
      "language_name": "Norwegian"
    }
  ]
}
```

### GET `/words/`
List words with optional filtering and pagination.

**Query Parameters:**
- `language_id` (optional): Filter by language
- `limit` (default: 50): Maximum words to return
- `offset` (default: 0): Number of words to skip

**Response:**
```json
{
  "words": [
    {
      "id": 1,
      "word": "hello",
      "wordtype_name": "noun",
      "language_name": "English"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

---

## Dictionary Fetch Endpoints

### GET `/fetch/languages`
Get list of languages that support dictionary fetching.

**Response:**
```json
{
  "languages": [
    {"code": "no", "name": "Norwegian"},
    {"code": "en", "name": "English"},
    {"code": "de", "name": "German"}
  ]
}
```

### GET `/fetch/word`
Fetch a word from dictionary sources.

**Query Parameters:**
- `word` (required): The word to fetch
- `language` (required): Language code (no, en, de)

**Example:** `/fetch/word?word=hello&language=en`

**Response:**
```json
{
  "word": "hello",
  "language": "English",
  "source": "Free Dictionary API",
  "data": {
    "word": "hello",
    "language": "English",
    "source": "Free Dictionary API",
    "senses": [
      {
        "id": "0_noun",
        "category": "noun",
        "meanings": [
          {
            "description": "A greeting",
            "examples": ["Hello, how are you?"]
          }
        ]
      }
    ]
  }
}
```

### GET `/fetch/preview`
Preview word data without saving it.

**Query Parameters:**
- `word` (required): The word to preview
- `language` (required): Language code

**Response:**
```json
{
  "word": "hello",
  "language": "English",
  "source": "Free Dictionary API",
  "senses": [
    {
      "category": "noun",
      "meanings": ["A greeting"],
      "example_count": 1
    }
  ]
}
```

### GET `/fetch/check-availability`
Check if dictionary sources are available.

**Response:**
```json
{
  "fetchers": {
    "no": {
      "available": true,
      "source": "ordbokene.no"
    },
    "en": {
      "available": true,
      "source": "Free Dictionary API"
    },
    "de": {
      "available": true,
      "source": "Wiktionary (German)"
    }
  }
}
```

---

## Review/Spaced Repetition Endpoints

All review endpoints require authentication.

### GET `/review/due`
Get words that are due for review. **Requires authentication.**

**Query Parameters:**
- `limit` (default: 20): Maximum words to return

**Response:**
```json
{
  "words": [
    {
      "progress_id": 1,
      "word_id": 42,
      "word": "hello",
      "status": "learning",
      "ease_factor": 2.5,
      "interval_days": 1,
      "repetitions": 2,
      "next_review": "2024-12-09T10:00:00",
      "wordtype_name": "noun",
      "language_name": "English",
      "meanings": [...]
    }
  ],
  "count": 5,
  "user_id": 1
}
```

### GET `/review/new`
Get words not yet in learning queue. **Requires authentication.**

**Query Parameters:**
- `language_id` (optional): Filter by language
- `limit` (default: 10): Maximum words to return

**Response:**
```json
{
  "words": [
    {
      "id": 50,
      "word": "goodbye",
      "wordtype_name": "noun",
      "language_name": "English",
      "meanings": [...]
    }
  ],
  "count": 10
}
```

### POST `/review/add-word`
Add a word to learning queue. **Requires authentication.**

**Request Body:**
```json
{
  "word_id": 50
}
```

**Response:**
```json
{
  "message": "Word added to learning queue successfully"
}
```

### POST `/review/submit`
Submit a review result. **Requires authentication.**

**Request Body:**
```json
{
  "word_id": 42,
  "correct": true,
  "difficulty": "medium"
}
```

**Difficulty options:** `"easy"`, `"medium"`, `"hard"`

**Response:**
```json
{
  "message": "Review submitted successfully",
  "next_review": "2024-12-15T10:00:00",
  "interval_days": 6,
  "status": "learning",
  "accuracy": 85.5,
  "streak_info": {
    "current_streak": 5
  }
}
```

### GET `/review/stats`
Get user learning statistics. **Requires authentication.**

**Response:**
```json
{
  "user_id": 1,
  "words_learned": 150,
  "words_mastered": 45,
  "total_reviews": 500,
  "correct_reviews": 425,
  "accuracy": 85.0,
  "current_streak": 7,
  "longest_streak": 14,
  "last_review_date": "2024-12-09",
  "status_breakdown": {
    "new": 20,
    "learning": 50,
    "review": 55,
    "mastered": 25
  }
}
```

---

## Language & Word Type Endpoints

### GET `/languages`
Get all available languages.

**Response:**
```json
[
  {"id": 1, "language": "Norwegian", "code": "no"},
  {"id": 2, "language": "English", "code": "en"},
  {"id": 3, "language": "German", "code": "de"}
]
```

### GET `/word_types`
Get all word types (parts of speech).

**Response:**
```json
[
  {"id": 1, "wordtype": "noun"},
  {"id": 2, "wordtype": "verb"},
  {"id": 3, "wordtype": "adjective"}
]
```

---

## Error Responses

All endpoints may return error responses:

**400 Bad Request:**
```json
{
  "detail": "Error description"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Token has expired"
}
```

**404 Not Found:**
```json
{
  "detail": "Word not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Database error occurred"
}
```

---

## Spaced Repetition Algorithm

The system uses the SM-2 (SuperMemo 2) algorithm for spaced repetition:

1. **Quality Rating** (0-5):
   - 5: Perfect response
   - 4: Correct after hesitation
   - 3: Correct with difficulty
   - 2: Incorrect but familiar
   - 1: Incorrect but recognized
   - 0: Complete blackout

2. **Intervals**:
   - First review: 1 day
   - Second review: 6 days
   - Subsequent: interval × ease_factor

3. **Status Progression**:
   - `new`: Just added to queue
   - `learning`: Interval < 7 days
   - `review`: Interval 7-30 days
   - `mastered`: Interval > 30 days, ease_factor > 2.5

4. **User Response Mapping**:
   - `correct=true, difficulty="easy"`: Quality 5
   - `correct=true, difficulty="medium"`: Quality 4
   - `correct=true, difficulty="hard"`: Quality 3
   - `correct=false`: Quality 1

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider:
- 100 requests/minute for authenticated users
- 20 requests/minute for anonymous endpoints
- 10 fetches/minute per language to respect dictionary sources

---

## Notes

- All timestamps are in ISO 8601 format
- All endpoints return JSON
- JWT tokens must be included in Authorization header for protected endpoints
- Dictionary fetchers may have different response structures depending on the source
