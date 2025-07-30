package handlers

import (
    "encoding/json"
    "net/http"

    "vocabulary-app/backend/go-service/services"
)

func ScrapeHandler(w http.ResponseWriter, r *http.Request) {
    word := r.URL.Query().Get("word")
    if word == "" {
        http.Error(w, "Missing word parameter", http.StatusBadRequest)
        return
    }

    entry, err := services.ScrapeWord(word)
    if err != nil {
        http.Error(w, "Failed to scrape word: "+err.Error(), http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(entry) // ✅ Directly return scraped data to frontend
}
