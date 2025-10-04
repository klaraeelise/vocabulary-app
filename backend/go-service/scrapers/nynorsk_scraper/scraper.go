package nynorsk_scraper

import (
	"fmt"
	"vocabulary-app/backend/go-service/models"
)

// ScrapeWord orchestrates the entire scraping process for Norwegian Nynorsk.
// This is a stub implementation that adapts the Bokmål scraper for Nynorsk variant.
func ScrapeWord(word string) (models.WordEntry, error) {
	// Nynorsk uses /nn/ instead of /bm/ in the URL
	url := fmt.Sprintf("https://ordbokene.no/nob/nn/%s", word)
	entry := models.WordEntry{Word: word}

	// Step 1: Extract all sense IDs
	senseIDs, err := ExtractSenseIDs(url)
	if err != nil {
		return entry, fmt.Errorf("failed to extract sense IDs: %w", err)
	}
	fmt.Println("✅ [Nynorsk] Found sense IDs:", senseIDs)

	// Step 2: Loop over each sense ID
	for _, senseID := range senseIDs {
		sense, err := ScrapeSense(url, senseID)
		if err != nil {
			fmt.Printf("⚠️ [Nynorsk] Failed to scrape static data for sense %s: %v\n", senseID, err)
			continue
		}

		// Step 3: Inflection (dynamic)
		forms, err := ScrapeInflection(url, senseID)
		if err != nil {
			fmt.Printf("⚠️ [Nynorsk] Inflection scrape failed for sense %s: %v\n", senseID, err)
		} else {
			sense.WordForms = forms
		}

		entry.Senses = append(entry.Senses, sense)
	}

	return entry, nil
}
