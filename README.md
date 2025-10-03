# Vocabulary App

A modern multi-language vocabulary learning application with spaced repetition, powered by Python (FastAPI), Go, and Next.js.

## Features

### 🔐 Authentication
- Secure JWT-based authentication
- 24-hour session expiry with automatic logout
- Password hashing with bcrypt

### 📚 Vocabulary Management
- Add words with multiple meanings and translations
- Support for multiple languages (Norwegian, English, German)
- Comprehensive word data including:
  - Definitions and examples
  - Word forms and inflections
  - Grammatical information
  - Expressions and idioms

### 🧠 Spaced Repetition Learning
- SM-2 algorithm for optimal review scheduling
- Track learning progress for each word
- Four learning stages: new, learning, review, mastered
- Adjustable difficulty levels
- Statistics and progress tracking

### 🌍 Multi-Language Dictionary Integration
- **Norwegian**: ordbokene.no (via Go scraper)
- **English**: Free Dictionary API
- **German**: Wiktionary API
- Modular fetcher system for easy language expansion

### 📊 Progress Tracking
- Review history and accuracy
- Daily review streaks
- Words learned and mastered counts
- Detailed statistics dashboard

---

## Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- OR manually install:
  - Python 3.11+
  - Go 1.21+
  - Node.js 18+
  - MySQL 8.0+

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/klaraeelise/vocabulary-app.git
cd vocabulary-app

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up

# The app will be available at:
# - Frontend: http://localhost:3000
# - Python API: http://localhost:8000
# - Go Scraper: http://localhost:8080
```

### Option 2: Manual Setup

#### 1. Database Setup

```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE vocabulary_app;
USE vocabulary_app;

# Run schema creation
mysql -u root -p vocabulary_app < backend/schema.sql
```

#### 2. Python Service

```bash
cd backend/python-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=vocabulary_app
DB_PORT=3306
SECRET_KEY=your-secret-key-here
EOF

# Run the service
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Go Service

```bash
cd backend/go-service

# Install dependencies
go mod download

# Run the service
go run main.go
# Service will run on port 8080
```

#### 4. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
# Frontend will run on port 3000
```

---

## Environment Variables

### Python Service (.env)

```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=vocabulary_app
DB_PORT=3306

# JWT Secret Key (generate a secure random string)
SECRET_KEY=your-secret-key-here-min-32-chars
```

### Go Service (.env)

```env
# Optional configuration for Go service
# Currently uses default settings
```

---

## Usage

### 1. Register an Account

Navigate to `http://localhost:3000/auth/register` and create an account.

### 2. Add Vocabulary

- **Manual Entry**: Go to "Add Flashcard" and enter word details
- **Dictionary Fetch**: Go to "Fetch Vocabulary" to look up words from dictionaries

### 3. Start Learning

- Click "Study" to review due words
- Rate your recall difficulty: easy, medium, or hard
- The system automatically schedules next reviews using spaced repetition

### 4. Track Progress

- View your statistics in the "Dashboard"
- Monitor your learning streak
- Check accuracy and words mastered

---

## API Documentation

Complete API documentation is available in [API_DOCUMENTATION.md](./API_DOCUMENTATION.md).

### Key Endpoints

**Authentication**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/verify` - Verify token validity

**Words**
- `POST /words/add` - Add new word
- `GET /words/{id}` - Get word details
- `GET /words/` - List words

**Dictionary Fetch**
- `GET /fetch/word?word=X&language=Y` - Fetch word from dictionary
- `GET /fetch/languages` - List supported languages

**Review (Requires Authentication)**
- `GET /review/due` - Get words due for review
- `GET /review/new` - Get new words to learn
- `POST /review/add-word` - Add word to learning queue
- `POST /review/submit` - Submit review result
- `GET /review/stats` - Get learning statistics

---

## Database Schema

The database schema is documented in [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md).

### Core Tables

- `users` - User accounts
- `languages` - Available languages
- `word_types` - Parts of speech
- `words` - Vocabulary entries
- `meanings` - Word definitions/translations
- `user_progress` - Spaced repetition tracking
- `user_statistics` - Aggregated learning metrics

---

## Architecture

The application follows a microservices architecture:

- **Python Service (FastAPI)**: Main API, authentication, learning logic
- **Go Service**: High-performance dictionary scraping
- **Frontend (Next.js)**: Modern React-based UI
- **MySQL**: Relational database

For detailed architecture information, see [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## Spaced Repetition Algorithm

The app uses the SuperMemo 2 (SM-2) algorithm:

1. **Initial Review**: 1 day
2. **Second Review**: 6 days
3. **Subsequent Reviews**: Previous interval × ease factor

The ease factor adjusts based on recall difficulty:
- Easy: Increases interval significantly
- Medium: Maintains current progression
- Hard: Resets to learning phase

Status progression:
- **New**: Just added
- **Learning**: Interval < 7 days
- **Review**: Interval 7-30 days  
- **Mastered**: Interval > 30 days, ease factor > 2.5

---

## Development

### Project Structure

```
vocabulary-app/
├── backend/
│   ├── python-service/      # FastAPI application
│   │   ├── routes/          # API endpoints
│   │   ├── fetchers/        # Dictionary fetchers
│   │   ├── main.py          # Application entry
│   │   └── requirements.txt
│   ├── go-service/          # Go scraper
│   │   ├── handlers/
│   │   ├── services/
│   │   └── main.go
│   └── schema.sql           # Database schema
├── frontend/                # Next.js application
│   ├── src/
│   │   ├── app/            # Pages
│   │   ├── components/     # React components
│   │   └── lib/            # Utilities
│   └── package.json
├── API_DOCUMENTATION.md    # API reference
├── DATABASE_SCHEMA.md      # Database documentation
├── ARCHITECTURE.md         # Architecture guide
├── ROADMAP.md             # Future plans
└── docker-compose.yml
```

### Adding a New Language

1. Create a new fetcher in `backend/python-service/fetchers/`
2. Inherit from `BaseFetcher` and implement required methods
3. Register in `fetchers/__init__.py`
4. Add language to database `languages` table

Example:
```python
from .base import BaseFetcher, WordEntry

class SpanishFetcher(BaseFetcher):
    def __init__(self):
        super().__init__("es", "RAE Dictionary")
    
    def fetch_word(self, word: str) -> Optional[WordEntry]:
        # Implement dictionary fetching
        pass
    
    def is_available(self) -> bool:
        # Check if source is accessible
        pass
```

### Running Tests

```bash
# Python tests (when implemented)
cd backend/python-service
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

---

## Roadmap

See [ROADMAP.md](./ROADMAP.md) for planned features including:

- Frontend review interface with flashcards
- Dashboard with charts and statistics
- Additional languages (Spanish, French, Italian)
- Custom word lists
- Gamification (XP, achievements, leaderboards)
- Mobile apps (PWA/native)
- Multi-subject expansion (math, science, etc.)
- AI-powered features

---

## Contributing

Contributions are welcome! Areas where help is needed:

1. **Dictionary Fetchers**: Implement scrapers for new languages
2. **Frontend**: Build review interface and dashboard
3. **Testing**: Add unit and integration tests
4. **Documentation**: Improve guides and tutorials
5. **Translations**: Translate UI to different languages

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run linters and tests
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## Troubleshooting

### Database Connection Issues

```bash
# Check if MySQL is running
mysql -u root -p -e "SELECT 1"

# Verify database exists
mysql -u root -p -e "SHOW DATABASES LIKE 'vocabulary_app'"

# Check user permissions
mysql -u root -p -e "SHOW GRANTS FOR 'your_user'@'localhost'"
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # or :3000, :8080

# Kill process
kill -9 <PID>
```

### Go Service Not Fetching Words

The Go service uses chromedp for dynamic content. Ensure:
- Chrome/Chromium is installed
- Sufficient memory (minimum 2GB recommended)
- Network access to ordbokene.no

---

## License

This project is licensed under the MIT License - see LICENSE file for details.

---

## Acknowledgments

- [SuperMemo 2 Algorithm](https://www.supermemo.com/en/archives1990-2015/english/ol/sm2)
- [ordbokene.no](https://ordbokene.no) - Norwegian dictionaries
- [Free Dictionary API](https://dictionaryapi.dev/) - English dictionary
- [Wiktionary](https://www.wiktionary.org/) - Multi-language dictionary data

---

## Support

- **Issues**: [GitHub Issues](https://github.com/klaraeelise/vocabulary-app/issues)
- **Documentation**: See docs in repository
- **Email**: support@vocabapp.example

---

## Screenshots

(Add screenshots here when frontend is complete)

---

*Made with ❤️ for language learners everywhere*
