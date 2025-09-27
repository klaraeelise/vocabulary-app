package services

import (
	"fmt"
	"vocabulary-app/backend/go-service/models"
)

// ScrapeWord orchestrates the entire scraping process: static + dynamic per sense.
// funcrion is not inherently tied to wordentry but rather just creating it out if the wird itself. it is a function not a method
func ScrapeWord(word string) (models.WordEntry, error) {
	url := fmt.Sprintf("https://ordbokene.no/nob/bm/%s", word) // Construct the URL for scraping
	entry := models.WordEntry{Word: word}                      //instantiate a new WordEntry

	// Step 1: Extract all sense IDs
	senseIDs, err := ExtractSenseIDs(url)
	if err != nil {
		return entry, fmt.Errorf("failed to extract sense IDs: %w", err)
	}
	fmt.Println("✅ Found sense IDs:", senseIDs)

	// Step 2: Loop over each sense ID
	for _, senseID := range senseIDs {
		sense, err := ScrapeSense(url, senseID)
		if err != nil {
			fmt.Printf("⚠️ Failed to scrape static data for sense %s: %v\n", senseID, err)
			continue
		}

		// Step 3: Inflection (dynamic)
		forms, err := ScrapeInflection(url, senseID)
		if err != nil {
			fmt.Printf("⚠️ Inflection scrape failed for sense %s: %v\n", senseID, err)
		} else {
			sense.WordForms = forms
		}

		entry.Senses = append(entry.Senses, sense)
	}

	return entry, nil
}
