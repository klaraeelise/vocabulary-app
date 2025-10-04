package nynorsk_scraper

import (
	"context"
	"fmt"
	"strings"
	"time"

	"vocabulary-app/backend/go-service/models"

	"github.com/PuerkitoBio/goquery"
	"github.com/chromedp/chromedp"
)

// ScrapeInflection handles chromedp logic per sense for Nynorsk.
func ScrapeInflection(url, senseID string) ([]models.WordFormEntry, error) {
	fmt.Println("🚀 [Nynorsk] Inflection scrape for sense:", senseID)

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

	err := chromedp.Run(ctx,
		chromedp.Navigate(url),
		chromedp.Sleep(2*time.Second),
		chromedp.ActionFunc(func(ctx context.Context) error {
			chromedp.ScrollIntoView(btnXPath, chromedp.BySearch).Do(ctx)
			return chromedp.Click(btnXPath, chromedp.BySearch).Do(ctx)
		}),
		chromedp.Sleep(2*time.Second),
		chromedp.OuterHTML(fmt.Sprintf(`div#%s div[id$='_inflection']`, senseID), &inflectionHTML, chromedp.BySearch),
	)

	if err != nil {
		return nil, fmt.Errorf("chromedp failed: %w", err)
	}

	doc, _ := goquery.NewDocumentFromReader(strings.NewReader(inflectionHTML))
	var forms []models.WordFormEntry
	var currentGroup string

	doc.Find("table[class*='infl-table'] tr").Each(func(rowIdx int, row *goquery.Selection) {
		if row.Find("th.infl-group").Length() > 0 {
			currentGroup = strings.TrimSpace(row.Find("th.infl-group").Text())
			return
		}

		label := strings.TrimSpace(row.Find("th.infl-label").Text())
		var fullLabel string
		if label != "" && currentGroup != "" {
			fullLabel = currentGroup + " / " + label
		} else if label != "" {
			fullLabel = label
		} else if currentGroup != "" {
			fullLabel = currentGroup
		} else {
			return
		}

		var formList []string
		row.Find("td span.comma").Each(func(j int, span *goquery.Selection) {
			form := strings.TrimSpace(span.Text())
			if form != "" {
				parts := strings.Fields(form)
				formList = append(formList, parts...)
			}
		})

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
		}
	})

	return forms, nil
}

func parseWordFormMetadata(label string) (number, definiteness, gender, degree, tense string) {
	l := strings.ToLower(label)
	if strings.Contains(l, "entall") {
		number = "singular"
	}
	if strings.Contains(l, "flertall") {
		number = "plural"
	}
	if strings.Contains(l, "ubestemt") {
		definiteness = "indefinite"
	}
	if strings.Contains(l, "bestemt") {
		definiteness = "definite"
	}
	if strings.Contains(l, "hankjønn") {
		gender = "masculine"
	}
	if strings.Contains(l, "hunkjønn") {
		gender = "feminine"
	}
	if strings.Contains(l, "intetkjønn") {
		gender = "neuter"
	}
	if strings.Contains(l, "komparativ") {
		degree = "comparative"
	}
	if strings.Contains(l, "superlativ") {
		degree = "superlative"
	}
	if strings.Contains(l, "presens") {
		tense = "present"
	}
	if strings.Contains(l, "preteritum") {
		tense = "past"
	}
	if strings.Contains(l, "perfektum") {
		tense = "perfect"
	}
	return
}
