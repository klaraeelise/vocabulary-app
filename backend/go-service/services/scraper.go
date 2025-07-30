package services

import (
    "fmt"
    "strings"
    "context"
    "time"

    "github.com/gocolly/colly"
    "vocabulary-app/backend/go-service/models"
    "github.com/chromedp/chromedp"
    "github.com/PuerkitoBio/goquery"
)


func ScrapeWord(word string) (models.WordEntry, error) {
    url := fmt.Sprintf("https://ordbokene.no/nob/bm/%s", word)
    entry := models.WordEntry{Word: word}

    c := colly.NewCollector()

    // Extract category (e.g., adjektiv, substantiv, verb)
    c.OnHTML("span.header-group-list", func(e *colly.HTMLElement) {
        entry.Category = strings.TrimSpace(e.Text)
        //fmt.Println("Category found:", entry.Category) // Debug log
    })

    // Extract article (e.g., "en", "ei", "et")
    c.OnHTML("div[id$='_inflection'] em.context", func(e *colly.HTMLElement) {
        article := strings.TrimSpace(e.Text)
        if article != "" {
            entry.Article = article
            //fmt.Println("Article found:", entry.Article)
        }
    })

    // Extract gender (e.g., hankjønn, hunkjønn, intetkjønn)
    c.OnHTML("div.subheader em", func(e *colly.HTMLElement) {
        entry.Gender = strings.TrimSpace(e.Text)
        //fmt.Println("Gender found:", entry.Gender)
    })


   // Extract meanings only from main level2 definitions
    c.OnHTML("li.definition.level2", func(e *colly.HTMLElement) {
        // Collect all explanation spans inside this li
        meaningParts := []string{}
        e.ForEach(".explanation", func(_ int, el *colly.HTMLElement) {
            part := strings.TrimSpace(el.Text)
            if part != "" {
                meaningParts = append(meaningParts, part)
            }
        })

        // Create a MeaningEntry
        if len(meaningParts) > 0 {
            meaning := models.MeaningEntry{
                Description: strings.Join(meaningParts, " "),
        }

        // Collect examples related to this meaning (if any)
        e.ForEach("ul.examples li", func(_ int, ex *colly.HTMLElement) {
            exampleText := strings.TrimSpace(ex.Text)
            if exampleText != "" {
                meaning.Examples = append(meaning.Examples, models.ExampleEntry{
                    Sentence: exampleText,
                })
            }
        })

        entry.Meanings = append(entry.Meanings, meaning)
        //fmt.Println("Meaning found:", meaning.Description)
            }
        })

    // Extract Faste uttrykk (expressions + explanations)
    c.OnHTML("section.expressions ul li", func(e *colly.HTMLElement) {
        phrase := strings.TrimSpace(e.ChildText("strong")) // idiom text
        explanation := strings.TrimSpace(e.ChildText(".definition .explanation .plain")) // meaning
        
        if phrase != "" {
            entry.Expressions = append(entry.Expressions, models.ExpressionEntry{
                Phrase:      phrase,
                Explanation: explanation,
            })
            fmt.Printf("Expression found: %s → %s\n", phrase, explanation)
        }
    })


    // ✅ Step 1: Visit page (static scrape)
    if err := c.Visit(url); err != nil {
        return models.WordEntry{}, err
    }

    // ✅ Step 2: Dynamic scrape for word forms
    fmt.Println("Starting dynamic inflection scrape...")
    wordForms, err := ScrapeInflection(word)
    if err != nil {
        fmt.Println("⚠️ Inflection scrape failed:", err)
    } else if len(wordForms) > 0 {
        entry.WordForms = wordForms
        fmt.Printf("✅ Extracted %d word form rows\n", len(wordForms))
    } else {
        fmt.Println("⚠️ Inflection scrape returned no forms.")
    }
    return entry, nil
}

func ScrapeInflection(word string) ([]models.WordFormEntry, error) {
    fmt.Println("🚀 Starting dynamic inflection scrape...")

    // Chrome setup
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
    url := fmt.Sprintf("https://ordbokene.no/nob/bm/%s", word)
    fmt.Println("Navigating to:", url)

    var inflectionHTML string
    err := chromedp.Run(ctx,
        chromedp.Navigate(url),
        chromedp.Sleep(2*time.Second),
        chromedp.ActionFunc(func(ctx context.Context) error {
            fmt.Println("Clicking 'Vis bøyning' button...")
            chromedp.ScrollIntoView(`//button[contains(., 'bøyning')]`, chromedp.BySearch).Do(ctx)
            return chromedp.Click(`//button[contains(., 'bøyning')]`, chromedp.BySearch).Do(ctx)
        }),
        chromedp.Sleep(2*time.Second),
        chromedp.OuterHTML(`div[id$='_inflection']`, &inflectionHTML, chromedp.ByQuery),
    )
    if err != nil {
        return nil, fmt.Errorf("chromedp failed: %w", err)
    }

    fmt.Println("✅ Inflection HTML length:", len(inflectionHTML))

    doc, _ := goquery.NewDocumentFromReader(strings.NewReader(inflectionHTML))
    var forms []models.WordFormEntry
    var currentGroup string

    // Iterate over rows
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
                parts := strings.Fields(form) // split if needed
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
            fmt.Printf("✅ Parsed: %s → %v\n", fullLabel, formList)
        }
    })

    fmt.Println("✅ Total word form rows parsed:", len(forms))
    return forms, nil
}




// scraper.go
func parseWordFormMetadata(label string) (number, definiteness, gender, degree, tense string) {
    l := strings.ToLower(label)
    if strings.Contains(l, "entall") { number = "singular" }
    if strings.Contains(l, "flertall") { number = "plural" }
    if strings.Contains(l, "ubestemt") { definiteness = "indefinite" }
    if strings.Contains(l, "bestemt") { definiteness = "definite" }
    if strings.Contains(l, "hankjønn") { gender = "masculine" }
    if strings.Contains(l, "hunkjønn") { gender = "feminine" }
    if strings.Contains(l, "intetkjønn") { gender = "neuter" }
    if strings.Contains(l, "komparativ") { degree = "comparative" }
    if strings.Contains(l, "superlativ") { degree = "superlative" }
    if strings.Contains(l, "presens") { tense = "present" }
    if strings.Contains(l, "preteritum") { tense = "past" }
    if strings.Contains(l, "perfektum") { tense = "perfect" }
    return
}

