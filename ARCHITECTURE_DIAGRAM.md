# Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Proxy Manager (Optional)                      │
│                    https://vocabulary-app.local                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ HTTPS/HTTP
                             │
┌────────────────────────────┴────────────────────────────────────────┐
│                                                                       │
│                       Docker Compose Network                          │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │         vocabulary-app-frontend (Next.js)                    │   │
│  │                Port: 3000                                     │   │
│  │  ┌────────────────────────────────────────────────────────┐ │   │
│  │  │ - React Components                                      │ │   │
│  │  │ - Server-Side Rendering                                 │ │   │
│  │  │ - API Routes (/api/scrape, /api/save)                  │ │   │
│  │  │ - Environment: NEXT_PUBLIC_API_URL                      │ │   │
│  │  └────────────────────────────────────────────────────────┘ │   │
│  └───────────────────┬─────────────────────┬───────────────────┘   │
│                      │                     │                         │
│                      │ HTTP                │ HTTP                    │
│                      ▼                     ▼                         │
│  ┌──────────────────────────┐  ┌──────────────────────────┐        │
│  │ vocabulary-app-python    │  │ vocabulary-app-go        │        │
│  │ (FastAPI)                │  │ (Scraper Service)        │        │
│  │ Port: 8000               │  │ Port: 8080               │        │
│  │ ┌──────────────────────┐ │  │ ┌────────────────────┐  │        │
│  │ │ Authentication       │ │  │ │ Language Router    │  │        │
│  │ │ - JWT (24h)          │ │  │ │ - Route by lang    │  │        │
│  │ │ - User management    │ │  │ └────────────────────┘  │        │
│  │ └──────────────────────┘ │  │                          │        │
│  │ ┌──────────────────────┐ │  │ ┌────────────────────┐  │        │
│  │ │ Word Management      │ │  │ │ Scrapers           │  │        │
│  │ │ - CRUD operations    │ │  │ │ ├─ bokmal          │  │        │
│  │ │ - Database queries   │ │  │ │ ├─ nynorsk         │  │        │
│  │ └──────────────────────┘ │  │ │ ├─ english (stub)  │  │        │
│  │ ┌──────────────────────┐ │  │ │ ├─ spanish (stub)  │  │        │
│  │ │ Spaced Repetition    │ │  │ │ └─ german (stub)   │  │        │
│  │ │ - SM-2 algorithm     │ │  │ └────────────────────┘  │        │
│  │ │ - Review scheduling  │ │  │ ┌────────────────────┐  │        │
│  │ └──────────────────────┘ │  │ │ Technologies       │  │        │
│  │ ┌──────────────────────┐ │  │ │ - Colly (static)   │  │        │
│  │ │ Dictionary Fetchers  │ │  │ │ - Chromedp (JS)    │  │        │
│  │ │ - Norwegian (→ Go)   │◄─┼──┤ │ - Goquery (parse)  │  │        │
│  │ │ - English (stub)     │ │  │ └────────────────────┘  │        │
│  │ │ - German (stub)      │ │  └──────────────────────────┘        │
│  │ └──────────────────────┘ │                                       │
│  └────────────┬──────────────┘                                      │
│               │                                                      │
│               │ MySQL                                                │
│               ▼                                                      │
│  ┌──────────────────────────┐                                       │
│  │ MySQL Database           │                                       │
│  │ (External/Container)     │                                       │
│  │ - Users                  │                                       │
│  │ - Words                  │                                       │
│  │ - Meanings               │                                       │
│  │ - Learning progress      │                                       │
│  └──────────────────────────┘                                       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## API Flow

### Word Fetching Flow

```
User Browser
    │
    │ 1. Select language + Enter word
    ▼
Frontend (fetch page)
    │
    │ 2. POST /api/scrape?word=X&language=Y
    ▼
Next.js API Route
    │
    │ 3. HTTP GET to Go service
    ▼
Go Service (vocabulary-app-go-service:8080)
    │
    │ 4. Route to appropriate scraper
    ▼
Language Router
    │
    ├─► bokmal_scraper.ScrapeWord()    → ordbokene.no/bm
    ├─► nynorsk_scraper.ScrapeWord()   → ordbokene.no/nn
    ├─► english_scraper.ScrapeWord()   → (stub)
    ├─► spanish_scraper.ScrapeWord()   → (stub)
    └─► german_scraper.ScrapeWord()    → (stub)
    │
    │ 5. Return WordEntry JSON
    ▼
Frontend (display results)
    │
    │ 6. User clicks "Save"
    ▼
Frontend → Next.js API (/api/save)
    │
    │ 7. POST to Python service
    ▼
Python Service (vocabulary-app-python-service:8000)
    │
    │ 8. Save to database
    ▼
MySQL Database
```

### Authentication Flow

```
User Browser
    │
    │ 1. Enter email + password
    ▼
Frontend (login page)
    │
    │ 2. POST /auth/login
    ▼
Python Service
    │
    │ 3. Verify credentials (bcrypt)
    │ 4. Generate JWT token (24h expiry)
    ▼
Frontend
    │
    │ 5. Store token in localStorage
    │ 6. Setup auto-logout timer
    │ 7. Update Navbar state
    ▼
User sees logged-in UI
```

## Environment Configuration

### Development (Local)

```
Frontend:
  NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

Backend Services:
  - Python: localhost:8000
  - Go: localhost:8080
  - MySQL: localhost:3306
```

### Docker Compose

```
Frontend:
  NEXT_PUBLIC_API_URL=http://vocabulary-app-python-service:8000
  (or use default, which is this value)

Services communicate via Docker DNS:
  - vocabulary-app-python-service
  - vocabulary-app-go-service
  - vocabulary-app-frontend
```

### Production (Proxy Manager)

```
Frontend:
  NEXT_PUBLIC_API_URL=https://vocabulary-app.local/api

Proxy configuration:
  - Frontend: / → localhost:3000
  - API: /api/ → localhost:8000
  - Scraper: /scraper/ → localhost:8080
```

## Technology Stack

```
┌─────────────────────────────────────────────────┐
│                  Frontend                        │
│  Next.js 15 | React | TypeScript | Tailwind     │
└─────────────────────────────────────────────────┘
                        │
                        │ REST API
                        │
┌─────────────────────────────────────────────────┐
│                  Backend                         │
│  ┌────────────────┐     ┌──────────────────┐   │
│  │ Python Service │     │   Go Service     │   │
│  │ - FastAPI      │     │ - net/http       │   │
│  │ - JWT auth     │     │ - Colly          │   │
│  │ - MySQL        │     │ - Chromedp       │   │
│  │ - SM-2 algo    │     │ - Goquery        │   │
│  └────────────────┘     └──────────────────┘   │
└─────────────────────────────────────────────────┘
                        │
                        │ MySQL
                        │
┌─────────────────────────────────────────────────┐
│                  Database                        │
│  MySQL 8.0 | Schema: vocabulary_app              │
└─────────────────────────────────────────────────┘
```

## Scraper Module Architecture

```
backend/go-service/
├── main.go
│   └── Registers HTTP handlers
│
├── handlers/
│   └── scrape.go
│       ├── ScrapeHandler() - Main entry point
│       └── LanguagesHandler() - List supported languages
│
├── routes/
│   └── language_router.go
│       ├── ScrapeWordByLanguage() - Route by language code
│       └── GetSupportedLanguages() - Return language list
│
└── scrapers/
    ├── bokmal_scraper/
    │   ├── scraper.go - Orchestration
    │   ├── sense_parser.go - Static HTML parsing
    │   ├── inflection.go - Dynamic content (Chromedp)
    │   └── utils.go - Helper functions
    │
    ├── nynorsk_scraper/
    │   ├── scraper.go
    │   ├── sense_parser.go
    │   └── inflection.go
    │
    ├── english_scraper/
    │   └── scraper.go (stub)
    │
    ├── spanish_scraper/
    │   └── scraper.go (stub)
    │
    └── german_scraper/
        └── scraper.go (stub)
```

## Data Flow

```
┌──────────┐
│  Word    │
│  Input   │
└────┬─────┘
     │
     ▼
┌──────────────────┐
│ Language Router  │
└────┬─────────────┘
     │
     ├─► no-bm ──► Bokmal Scraper ──┐
     ├─► no-nn ──► Nynorsk Scraper ─┤
     ├─► en ─────► English Scraper ─┤
     ├─► es ─────► Spanish Scraper ─┤
     └─► de ─────► German Scraper ──┤
                                     │
                                     ▼
                              ┌─────────────┐
                              │ WordEntry   │
                              │ ├─ Word     │
                              │ └─ Senses[] │
                              │    ├─ ID    │
                              │    ├─ Cat   │
                              │    ├─ Means │
                              │    └─ Forms │
                              └─────────────┘
```

## Key Improvements Summary

### Before Refactoring
- Monolithic scraper in services/
- Single language (Norwegian Bokmål)
- Generic Docker service names
- Hardcoded localhost URLs
- Static login/logout button

### After Refactoring
- Modular scrapers by language
- 5 language support (2 implemented, 3 stubs)
- Descriptive Docker service names
- Environment-based configuration
- Dynamic authentication state
- Comprehensive documentation
