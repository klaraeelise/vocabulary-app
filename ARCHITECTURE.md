# Architecture Documentation

## System Overview

The Vocabulary App is a multi-language learning platform designed with a microservices architecture to support vocabulary acquisition using spaced repetition techniques.

## Technology Stack

### Backend Services

**Python Service (FastAPI)**
- **Primary API Server**: Handles authentication, word management, and learning progress
- **Port**: 8000
- **Key Features**:
  - JWT-based authentication with 24-hour token expiry
  - RESTful API design
  - Database operations with transaction management
  - Spaced repetition algorithm (SM-2)
  - Multi-language dictionary fetchers

**Go Service**
- **Dictionary Scraper**: Specialized service for Norwegian dictionary (ordbokene.no)
- **Port**: 8080
- **Key Features**:
  - High-performance web scraping
  - Chromedp for dynamic content
  - JSON API for word data

### Frontend

**Next.js 15 (React)**
- **Modern SPA**: Server-side rendering with client-side navigation
- **Port**: 3000
- **Key Features**:
  - TypeScript for type safety
  - Tailwind CSS for styling
  - Client-side token management
  - Automatic session expiry

### Database

**MySQL**
- **Relational Database**: Stores users, words, meanings, and progress
- **Key Tables**:
  - `users`: User accounts and authentication
  - `words`: Vocabulary entries
  - `meanings`: Word definitions and translations
  - `user_progress`: Spaced repetition tracking
  - `user_statistics`: Aggregated learning metrics

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Auth    │  │  Study   │  │  Fetch   │  │Dashboard │   │
│  │  Pages   │  │  Pages   │  │  Pages   │  │  Pages   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│         │              │              │              │       │
│         └──────────────┴──────────────┴──────────────┘       │
│                        │                                     │
│                   [JWT Token]                                │
└────────────────────────┼────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼                         ▼
┌─────────────────────┐   ┌─────────────────────┐
│  Python Service     │   │   Go Service        │
│  (FastAPI)          │   │   (Scraper)         │
│  :8000              │   │   :8080             │
│                     │   │                     │
│  ┌───────────────┐ │   │  ┌───────────────┐ │
│  │ Auth Routes   │ │   │  │ Scrape        │ │
│  │ - /auth/*     │ │   │  │ - /api/scrape │ │
│  └───────────────┘ │   │  └───────────────┘ │
│                     │   │                     │
│  ┌───────────────┐ │   │  Norwegian only     │
│  │ Word Routes   │ │   │  (ordbokene.no)     │
│  │ - /words/*    │ │   │                     │
│  └───────────────┘ │   └─────────────────────┘
│                     │
│  ┌───────────────┐ │
│  │ Review Routes │ │
│  │ - /review/*   │ │
│  └───────────────┘ │
│                     │
│  ┌───────────────┐ │
│  │ Fetch Routes  │ │
│  │ - /fetch/*    │ │
│  └───────────────┘ │
│         │           │
│    [Fetcher         │
│     Registry]       │
│  ┌──────┬─────┬───┐│
│  │ NO   │ EN  │DE ││
│  └──────┴─────┴───┘│
└──────────┼──────────┘
           │
           ▼
    ┌──────────────┐
    │    MySQL     │
    │   Database   │
    │              │
    │  ┌────────┐  │
    │  │ users  │  │
    │  └────────┘  │
    │  ┌────────┐  │
    │  │ words  │  │
    │  └────────┘  │
    │  ┌────────┐  │
    │  │meanings│  │
    │  └────────┘  │
    │  ┌────────┐  │
    │  │progress│  │
    │  └────────┘  │
    └──────────────┘
```

---

## Module Structure

### Backend Python Service

```
backend/python-service/
├── main.py                 # FastAPI application entry point
├── database.py             # Database connection
├── db_utils.py            # Database utilities (context managers, etc.)
├── auth_utils.py          # JWT authentication utilities
├── spaced_repetition.py   # SM-2 algorithm implementation
│
├── routes/                # API route handlers
│   ├── auth.py           # Authentication endpoints
│   ├── words.py          # Word management endpoints
│   ├── review.py         # Spaced repetition endpoints
│   ├── fetch.py          # Dictionary fetch endpoints
│   ├── languages.py      # Language listing
│   └── word_types.py     # Word type listing
│
└── fetchers/             # Dictionary fetcher modules
    ├── __init__.py       # Fetcher registry and initialization
    ├── base.py           # Abstract base classes and data models
    ├── norwegian.py      # Norwegian fetcher (via Go service)
    ├── english.py        # English fetcher (Free Dictionary API)
    └── german.py         # German fetcher (Wiktionary API)
```

### Backend Go Service

```
backend/go-service/
├── main.go               # HTTP server entry point
│
├── handlers/             # HTTP request handlers
│   └── scrape.go        # Scrape endpoint handler
│
├── services/            # Business logic
│   ├── scraper.go       # Main scraping orchestration
│   ├── sense_parser.go  # HTML parsing for word senses
│   ├── inflection.go    # Word form scraping
│   └── utils.go         # Utility functions
│
├── models/              # Data models
│   └── word.go         # Word entry structures
│
└── client/             # External service clients
    └── python.go       # (Optional) Python service client
```

### Frontend

```
frontend/src/
├── app/                  # Next.js app directory
│   ├── auth/            # Authentication pages
│   │   ├── login/
│   │   └── register/
│   ├── homepage/        # Main application pages
│   │   ├── add-word/
│   │   ├── fetch/
│   │   ├── study/
│   │   └── dashboard/
│   └── api/             # API routes (proxy to backend)
│       └── scrape/
│
├── components/          # React components
│   ├── Navbar.tsx
│   ├── SenseCard.tsx
│   └── VocabListCard.tsx
│
└── lib/                # Utility libraries
    ├── api.ts          # API client functions
    └── auth.ts         # Authentication utilities
```

---

## Key Design Patterns

### 1. Microservices Architecture
- **Separation of Concerns**: Python for API/business logic, Go for web scraping
- **Independent Scaling**: Services can scale independently based on load
- **Technology Specialization**: Use the best tool for each job

### 2. Repository Pattern
- Database operations abstracted into utility functions
- Context managers for automatic transaction handling
- Consistent error handling across all database operations

### 3. Strategy Pattern (Dictionary Fetchers)
- Abstract base class `BaseFetcher` defines interface
- Concrete implementations for each language/source
- Registry pattern for dynamic fetcher selection

### 4. Facade Pattern (API Layer)
- FastAPI routes provide simple interface to complex operations
- Hide implementation details from frontend
- Consistent error responses across all endpoints

### 5. Middleware Pattern
- CORS middleware for cross-origin requests
- JWT authentication middleware for protected routes
- Transaction management middleware for database operations

---

## Data Flow Examples

### User Login Flow
```
1. User enters credentials in frontend
2. Frontend sends POST to /auth/login
3. Backend verifies credentials with database
4. Backend generates JWT token (24h expiry)
5. Backend returns token + expiry time
6. Frontend stores token in localStorage
7. Frontend sets up auto-logout timer
8. Frontend includes token in all subsequent requests
```

### Word Fetch Flow
```
1. User searches for word in frontend
2. Frontend sends GET to /fetch/word?word=X&language=Y
3. Backend looks up appropriate fetcher in registry
4. Fetcher makes request to dictionary source
5. Dictionary source returns raw data
6. Fetcher parses and normalizes data
7. Backend returns structured WordEntry
8. Frontend displays word information
9. User can save word to database via /words/add
```

### Review Flow (Spaced Repetition)
```
1. User clicks "Study" in frontend
2. Frontend sends GET to /review/due
3. Backend queries user_progress for due words
4. Backend returns words with next_review <= NOW()
5. Frontend displays flashcard interface
6. User submits answer (correct/incorrect, difficulty)
7. Frontend sends POST to /review/submit
8. Backend applies SM-2 algorithm
9. Backend updates ease_factor, interval, next_review
10. Backend updates user_statistics
11. Backend returns new review schedule
12. Frontend shows next card or completion message
```

---

## Security Considerations

### Authentication
- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens with 24-hour expiry
- Tokens validated on every protected request
- Automatic logout on expiry

### Database
- Parameterized queries prevent SQL injection
- Foreign key constraints ensure data integrity
- Transaction management prevents partial updates
- Input validation with Pydantic models

### API
- CORS configured for specific origins
- Rate limiting recommended for production
- Error messages don't leak sensitive information

---

## Scalability Considerations

### Current Limitations
- Single database instance (no replication)
- No caching layer
- Dictionary fetchers make real-time requests
- No queue for background jobs

### Future Improvements

**Database**
- Add read replicas for scalability
- Implement connection pooling
- Consider sharding by user_id for large scale

**Caching**
- Redis for dictionary fetch results
- Cache user_progress for active users
- Cache language/word_type lookups

**Background Jobs**
- Queue system (Celery/RQ) for:
  - Bulk word imports
  - Statistics aggregation
  - Email notifications

**Load Balancing**
- Multiple Python service instances
- Multiple Go service instances
- Nginx for load distribution

---

## Extension Points

### Adding New Languages

1. Create new fetcher class inheriting from `BaseFetcher`
2. Implement `fetch_word()` and `is_available()` methods
3. Register in `fetchers/__init__.py`
4. Add language to database `languages` table
5. No frontend changes needed (dynamic language list)

Example:
```python
# fetchers/spanish.py
class SpanishFetcher(BaseFetcher):
    def __init__(self):
        super().__init__("es", "RAE")
    
    def fetch_word(self, word: str) -> Optional[WordEntry]:
        # Implementation for Spanish dictionary
        pass
    
    def is_available(self) -> bool:
        # Check if RAE is accessible
        pass

# Register in fetchers/__init__.py
spanish = SpanishFetcher()
fetcher_registry.register(spanish)
```

### Adding New Subjects (Math, Statistics, etc.)

1. Add `subjects` table to database:
```sql
CREATE TABLE subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT
);
```

2. Add `subject_id` to `words` table:
```sql
ALTER TABLE words ADD COLUMN subject_id INT DEFAULT 1;
ALTER TABLE words ADD FOREIGN KEY (subject_id) REFERENCES subjects(id);
```

3. Create subject-specific fetchers/data sources
4. Update frontend to filter by subject
5. Adapt review system for different learning patterns

### Adding Collaborative Features

**Proposed Schema:**
```sql
CREATE TABLE word_lists (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE word_list_items (
    list_id INT NOT NULL,
    word_id INT NOT NULL,
    FOREIGN KEY (list_id) REFERENCES word_lists(id),
    FOREIGN KEY (word_id) REFERENCES words(id)
);

CREATE TABLE shared_lists (
    list_id INT NOT NULL,
    shared_with_user_id INT NOT NULL,
    FOREIGN KEY (list_id) REFERENCES word_lists(id),
    FOREIGN KEY (shared_with_user_id) REFERENCES users(id)
);
```

---

## Testing Strategy

### Unit Tests
- Test individual functions (SM-2 algorithm, validators)
- Mock database connections
- Test error handling paths

### Integration Tests
- Test API endpoints with test database
- Test fetcher implementations
- Test authentication flow

### End-to-End Tests
- Selenium/Playwright for frontend testing
- Test complete user journeys
- Test across different browsers

---

## Deployment

### Docker Compose (Current)
```yaml
services:
  - go-service (port 8080)
  - python-service (port 8000)
  - frontend (port 3000)
```

### Production Recommendations
- Use managed database (AWS RDS, Google Cloud SQL)
- Container orchestration (Kubernetes)
- CDN for frontend assets
- Environment-specific configurations
- Automated backups
- Monitoring and logging (Prometheus, ELK stack)

---

## Maintenance

### Regular Tasks
- Database backups (daily)
- Monitor dictionary source availability
- Review and update dependencies
- Check for security vulnerabilities
- Analyze user learning patterns

### Monitoring Metrics
- API response times
- Database query performance
- User registration/login rates
- Word fetch success rates
- Review completion rates
- User retention and streak statistics
