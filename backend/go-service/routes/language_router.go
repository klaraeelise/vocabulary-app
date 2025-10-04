package routes

import (
	"fmt"
	"vocabulary-app/backend/go-service/models"
	"vocabulary-app/backend/go-service/scrapers/bokmal_scraper"
	"vocabulary-app/backend/go-service/scrapers/english_scraper"
	"vocabulary-app/backend/go-service/scrapers/german_scraper"
	"vocabulary-app/backend/go-service/scrapers/nynorsk_scraper"
	"vocabulary-app/backend/go-service/scrapers/spanish_scraper"
)

// LanguageRouter routes scraping requests to the appropriate language scraper
type LanguageRouter struct{}

// NewLanguageRouter creates a new language router instance
func NewLanguageRouter() *LanguageRouter {
	return &LanguageRouter{}
}

// ScrapeWordByLanguage routes the word to the appropriate scraper based on language code
func (lr *LanguageRouter) ScrapeWordByLanguage(word string, language string) (models.WordEntry, error) {
	fmt.Printf("📌 Routing scrape request: word='%s', language='%s'\n", word, language)
	
	switch language {
	case "no-bm", "nb", "no", "bokmal":
		fmt.Println("→ Using Norwegian Bokmål scraper")
		return bokmal_scraper.ScrapeWord(word)
		
	case "no-nn", "nn", "nynorsk":
		fmt.Println("→ Using Norwegian Nynorsk scraper")
		return nynorsk_scraper.ScrapeWord(word)
		
	case "en", "english":
		fmt.Println("→ Using English scraper (stub)")
		return english_scraper.ScrapeWord(word)
		
	case "es", "spanish":
		fmt.Println("→ Using Spanish scraper (stub)")
		return spanish_scraper.ScrapeWord(word)
		
	case "de", "german":
		fmt.Println("→ Using German scraper (stub)")
		return german_scraper.ScrapeWord(word)
		
	default:
		return models.WordEntry{}, fmt.Errorf("unsupported language: %s", language)
	}
}

// GetSupportedLanguages returns a list of supported language codes
func (lr *LanguageRouter) GetSupportedLanguages() []string {
	return []string{"no-bm", "no-nn", "en", "es", "de"}
}
