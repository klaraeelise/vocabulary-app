/*
ScrapeInflection(url, senseID string) ([]WordFormEntry, error): Handles chromedp logic per sense.
*/

package services

import (
	"context"
	"fmt"
	"strings"
	"time"

	"vocabulary-app/backend/go-service/models"

	"github.com/PuerkitoBio/goquery"
	"github.com/chromedp/chromedp"
)

func ScrapeInflection(url, senseID string) ([]models.WordFormEntry, error) {
	fmt.Println("🚀 Inflection scrape for sense:", senseID)

	// Setup Chrome
	opts := append(chromedp.DefaultExecAllocatorOptions[:],
		chromedp.Flag("headless", true),
		chromedp.Flag("disable-gpu", true),
		chromedp.Flag("disable-infobars", true),
	)
	allocCtx, cancel := chromedp.NewExecAllocator(context.Background(), opts...)
	defer cancel()

	ctx, cancel := context.WithTimeout(allocCtx, 40*time.Second)
	defer cancel()
	ctx, _ = chromedp.NewContext(ctx)

	var inflectionHTML string
	btnXPath := fmt.Sprintf(`//div[@id='%s']//button[contains(@class, 'btn-primary')]`, senseID)

	// Run scraping sequence
	err := chromedp.Run(ctx,
		chromedp.Navigate(url),
		chromedp.Sleep(2*time.Second),
		chromedp.ActionFunc(func(ctx context.Context) error {
			fmt.Printf("Clicking bøyning button for sense %s...\n", senseID)
			chromedp.ScrollIntoView(btnXPath, chromedp.BySearch).Do(ctx)
			return chromedp.Click(btnXPath, chromedp.BySearch).Do(ctx)
		}),
		chromedp.Sleep(2*time.Second),
		chromedp.OuterHTML(fmt.Sprintf(`div#%s div[id$='_inflection']`, senseID), &inflectionHTML, chromedp.BySearch),
	)

	if err != nil {
		return nil, fmt.Errorf("chromedp failed: %w", err)
	}
	fmt.Println("✅ Inflection HTML length:", len(inflectionHTML))

	// Parse inflection table inline
	doc, _ := goquery.NewDocumentFromReader(strings.NewReader(inflectionHTML))
	var forms []models.WordFormEntry
	var currentGroup string

	doc.Find("table[class*='infl-table'] tr").Each(func(rowIdx int, row *goquery.Selection) {
		// Detect group headers
		if row.Find("th.infl-group").Length() > 0 {
			currentGroup = strings.TrimSpace(row.Find("th.infl-group").Text())
			fmt.Println("🔹 Group detected:", currentGroup)
			return
		}

		// Extract label
		label := strings.TrimSpace(row.Find("th.infl-label").Text())
		var fullLabel string
		if label != "" && currentGroup != "" {
			fullLabel = currentGroup + " / " + label
		} else if label != "" {
			fullLabel = label
		} else if currentGroup != "" {
			fullLabel = currentGroup
		} else {
			fmt.Println("⚠️ Skipping row: no label/group")
			return
		}

		// Extract forms
		var formList []string
		row.Find("td span.comma").Each(func(j int, span *goquery.Selection) {
			form := strings.TrimSpace(span.Text())
			if form != "" {
				parts := strings.Fields(form)
				formList = append(formList, parts...)
			}
		})

		// Only append valid rows
		if len(formList) > 0 {
			num, def, gen, deg, tense := parseWordFormMetadata(fullLabel)
			forms = append(forms, models.WordFormEntry{
				Label:        fullLabel,
				Forms:        formList,
				Number:       num,
				Definiteness: def,
				Gender:       gen,
				Degree:       deg,
				Tense:        tense,
			})
			fmt.Printf("✅ Parsed: %s → %v\n", fullLabel, formList)
		}
	})

	fmt.Println("✅ Total word form rows parsed:", len(forms))
	return forms, nil
}
