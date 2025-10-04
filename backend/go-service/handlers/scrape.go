package handlers

import (
    "encoding/json"
    "net/http"

    "vocabulary-app/backend/go-service/routes"
)

var languageRouter = routes.NewLanguageRouter()

func ScrapeHandler(w http.ResponseWriter, r *http.Request) {
    word := r.URL.Query().Get("word")
    if word == "" {
        http.Error(w, "Missing word parameter", http.StatusBadRequest)
        return
    }

    // Get language parameter (defaults to Norwegian Bokmål if not specified)
    language := r.URL.Query().Get("language")
    if language == "" {
        language = "no-bm" // default to Norwegian Bokmål for backwards compatibility
    }

    entry, err := languageRouter.ScrapeWordByLanguage(word, language)
    if err != nil {
        http.Error(w, "Failed to scrape word: "+err.Error(), http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(entry)
}

// LanguagesHandler returns supported languages
func LanguagesHandler(w http.ResponseWriter, r *http.Request) {
    languages := languageRouter.GetSupportedLanguages()
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]interface{}{
        "languages": languages,
    })
}
