package main

import (
    "fmt"
    "log"
    "net/http"
    
    "vocabulary-app/backend/go-service/handlers"
)

func main() {
    
    fmt.Println("Go server running")

    http.HandleFunc("/api/scrape", handlers.ScrapeHandler)
    http.HandleFunc("/api/languages", handlers.LanguagesHandler)

    log.Fatal(http.ListenAndServe(":8080", nil))
}
