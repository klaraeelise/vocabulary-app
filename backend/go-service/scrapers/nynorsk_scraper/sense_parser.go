package nynorsk_scraper

import (
	"fmt"
	"strings"
	"vocabulary-app/backend/go-service/models"

	"github.com/gocolly/colly"
)

// ExtractSenseIDs scans the page and returns a list of sense IDs (Nynorsk variant).
func ExtractSenseIDs(url string) ([]string, error) {
	var ids []string
	c := colly.NewCollector()

	c.OnHTML("div.article.flex.flex-col", func(e *colly.HTMLElement) {
		id := e.ChildAttr("div.flex.flex-col.grow", "id")
		if id != "" {
			fmt.Println("[Nynorsk] Found sense ID:", id)
			ids = append(ids, id)
		}
	})

	if err := c.Visit(url); err != nil {
		return nil, err
	}

	return ids, nil
}

// ScrapeSense scrapes one sense block for Nynorsk.
func ScrapeSense(url, senseID string) (models.SenseEntry, error) {
	var sense models.SenseEntry
	sense.ID = senseID

	c := colly.NewCollector()
	selector := fmt.Sprintf("div#%s", senseID)
	c.OnHTML(selector, func(e *colly.HTMLElement) {
		sense.ID = senseID
		sense.Category = strings.TrimSpace(e.ChildText(".subheader .header-group-list"))
		sense.Gender = strings.TrimSpace(e.ChildText(".subheader em"))

		e.ForEach("section.definitions .definition.level1", func(_ int, def *colly.HTMLElement) {
			def.ForEach(".explanation", func(_ int, exp *colly.HTMLElement) {
				desc := strings.TrimSpace(exp.Text)
				if desc != "" {
					meaning := models.MeaningEntry{Description: desc}

					def.ForEach("ul.examples li", func(_ int, ex *colly.HTMLElement) {
						exText := strings.TrimSpace(ex.Text)
						if exText != "" {
							meaning.Examples = append(meaning.Examples, exText)
						}
					})

					sense.Meanings = append(sense.Meanings, meaning)
				}
			})

			def.ForEach("ol.sub_definitions li.definition.level2", func(_ int, subDef *colly.HTMLElement) {
				subDef.ForEach(".explanation", func(_ int, exp *colly.HTMLElement) {
					desc := strings.TrimSpace(exp.Text)
					if desc != "" {
						meaning := models.MeaningEntry{Description: desc}

						subDef.ForEach("ul.examples li", func(_ int, ex *colly.HTMLElement) {
							exText := strings.TrimSpace(ex.Text)
							if exText != "" {
								meaning.Examples = append(meaning.Examples, exText)
							}
						})

						sense.Meanings = append(sense.Meanings, meaning)
					}
				})
			})
		})

		e.ForEach("section.expressions li", func(_ int, expr *colly.HTMLElement) {
			phrase := strings.TrimSpace(expr.ChildText("strong"))
			explanation := strings.TrimSpace(expr.ChildText(".explanation"))
			if phrase != "" {
				sense.Expressions = append(sense.Expressions, models.ExpressionEntry{
					Phrase: phrase, Explanation: explanation,
				})
			}
		})
	})

	if err := c.Visit(url); err != nil {
		return sense, err
	}
	return sense, nil
}
