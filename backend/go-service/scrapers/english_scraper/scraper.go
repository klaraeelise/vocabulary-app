package english_scraper

import (
	"fmt"
	"vocabulary-app/backend/go-service/models"
)

// ScrapeWord is a stub implementation for English dictionary scraping.
// TODO: Implement actual scraping from an English dictionary source (e.g., Free Dictionary API, Wiktionary)
func ScrapeWord(word string) (models.WordEntry, error) {
	fmt.Println("🔷 [English] Stub scraper called for word:", word)
	
	// Return a stub entry with placeholder data
	entry := models.WordEntry{
		Word: word,
		Senses: []models.SenseEntry{
			{
				ID:       "en_stub_1",
				Category: "stub",
				Meanings: []models.MeaningEntry{
					{
						Description: "English dictionary scraping not yet implemented",
						Examples:    []string{"This is a placeholder entry"},
					},
				},
			},
		},
	}
	
	return entry, nil
}
