package client

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"

    "vocabulary-app/backend/go-service/models"
)

func SendToPython(entry models.WordEntry) error {
    jsonData, _ := json.Marshal(entry)
    resp, err := http.Post("http://python-service:8000/api/words", "application/json", bytes.NewBuffer(jsonData))
    if err != nil {
        return fmt.Errorf("error sending data to Python: %v", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("Python service returned %s", resp.Status)
    }
    return nil
}
