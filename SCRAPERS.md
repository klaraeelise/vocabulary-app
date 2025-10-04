# Scraper Architecture Documentation

## Overview

The Go service implements a modular, language-based scraping architecture. Each language has its own dedicated scraper module, making it easy to add, modify, or remove language support.

## Directory Structure

```
backend/go-service/
├── scrapers/
│   ├── bokmal_scraper/      # Norwegian Bokmål (fully implemented)
│   │   ├── scraper.go       # Main scraping orchestration
│   │   ├── sense_parser.go  # Static HTML parsing
│   │   ├── inflection.go    # Dynamic inflection table scraping
│   │   └── utils.go         # Helper functions
│   ├── nynorsk_scraper/     # Norwegian Nynorsk (fully implemented)
│   │   ├── scraper.go
│   │   ├── sense_parser.go
│   │   └── inflection.go
│   ├── english_scraper/     # English (stub implementation)
│   │   └── scraper.go
│   ├── spanish_scraper/     # Spanish (stub implementation)
│   │   └── scraper.go
│   └── german_scraper/      # German (stub implementation)
│       └── scraper.go
├── routes/
│   └── language_router.go   # Central routing logic
├── handlers/
│   └── scrape.go            # HTTP handlers
└── models/
    └── word.go              # Shared data models
```

## Language Router

The `routes/language_router.go` file provides a central routing mechanism that dispatches scraping requests to the appropriate language scraper based on the language code.

### Supported Language Codes

| Language | Codes | Status |
|----------|-------|--------|
| Norwegian Bokmål | `no-bm`, `nb`, `no`, `bokmal` | ✅ Fully implemented |
| Norwegian Nynorsk | `no-nn`, `nn`, `nynorsk` | ✅ Fully implemented |
| English | `en`, `english` | ⚠️ Stub (needs implementation) |
| Spanish | `es`, `spanish` | ⚠️ Stub (needs implementation) |
| German | `de`, `german` | ⚠️ Stub (needs implementation) |

### Usage

```go
router := routes.NewLanguageRouter()
entry, err := router.ScrapeWordByLanguage("hello", "en")
```

## API Endpoints

### Scrape Word

```
GET /api/scrape?word={word}&language={language}
```

**Parameters:**
- `word` (required): The word to scrape
- `language` (optional): Language code (defaults to `no-bm` for backwards compatibility)

**Example:**
```bash
curl "http://localhost:8080/api/scrape?word=hus&language=no-bm"
```

### Get Supported Languages

```
GET /api/languages
```

**Response:**
```json
{
  "languages": ["no-bm", "no-nn", "en", "es", "de"]
}
```

## Norwegian Implementation (Bokmål & Nynorsk)

### Data Source

Both Norwegian scrapers use [ordbokene.no](https://ordbokene.no), the official dictionary service from the Language Council of Norway.

- **Bokmål**: `https://ordbokene.no/nob/bm/{word}`
- **Nynorsk**: `https://ordbokene.no/nob/nn/{word}`

### Scraping Process

1. **Extract Sense IDs**: Parse the page to find all word senses
2. **Scrape Static Data**: Extract definitions, examples, and expressions for each sense
3. **Scrape Inflection Forms**: Use headless Chrome to click the inflection button and extract word forms

### Technologies Used

- **Colly**: For static HTML scraping
- **Chromedp**: For dynamic content (inflection tables)
- **Goquery**: For parsing HTML tables

## Stub Implementations

The English, Spanish, and German scrapers are currently stubs that return placeholder data. These need to be implemented with actual scraping logic.

### Implementing a New Language

1. **Create the scraper package** in `scrapers/{language}_scraper/`
2. **Implement the `ScrapeWord` function** that returns a `models.WordEntry`
3. **Add the language to the router** in `routes/language_router.go`
4. **Update the supported languages list** in the router's `GetSupportedLanguages()` method

Example stub:

```go
package english_scraper

import (
    "vocabulary-app/backend/go-service/models"
)

func ScrapeWord(word string) (models.WordEntry, error) {
    // TODO: Implement actual scraping logic
    // Possible sources: Free Dictionary API, Wiktionary, etc.
    
    entry := models.WordEntry{
        Word: word,
        Senses: []models.SenseEntry{
            // ... populate with real data
        },
    }
    return entry, nil
}
```

## Recommended Dictionary Sources

For implementing stub scrapers:

- **English**: 
  - [Free Dictionary API](https://dictionaryapi.dev/)
  - [Merriam-Webster API](https://dictionaryapi.com/)
  - [Oxford Dictionaries API](https://developer.oxforddictionaries.com/)
  
- **Spanish**:
  - [RAE (Real Academia Española)](https://dle.rae.es/)
  - [WordReference](https://www.wordreference.com/)
  
- **German**:
  - [Duden](https://www.duden.de/)
  - [DWDS](https://www.dwds.de/)
  - [Wiktionary](https://de.wiktionary.org/)

## Testing

To test a scraper:

```bash
cd backend/go-service
go run main.go

# In another terminal:
curl "http://localhost:8080/api/scrape?word=test&language=en"
```

## Performance Considerations

- **Caching**: Consider implementing caching for frequently requested words
- **Rate Limiting**: Add rate limiting to avoid overwhelming dictionary sources
- **Concurrent Requests**: The current implementation handles one word at a time
- **Timeout Handling**: All scraping operations have reasonable timeouts

## Future Improvements

1. Implement actual scrapers for English, Spanish, and German
2. Add caching layer (Redis or in-memory)
3. Implement rate limiting
4. Add error recovery and retry logic
5. Support batch word scraping
6. Add scraper health checks and monitoring
