package models

// MeaningEntry: A single meaning, optionally with examples.
type MeaningEntry struct {
    Description string   `json:"description"`
    Examples    []string `json:"examples,omitempty"` // Flattened for simplicity
}

// ExpressionEntry: Idioms/fixed expressions for a sense.
type ExpressionEntry struct {
    Phrase      string `json:"phrase"`
    Explanation string `json:"explanation"`
}

// WordFormEntry: One row of inflection data.
type WordFormEntry struct {
    Label        string   `json:"label"`
    Forms        []string `json:"forms"`
    Number       string   `json:"number,omitempty"`
    Definiteness string   `json:"definiteness,omitempty"`
    Gender       string   `json:"gender,omitempty"`
    Degree       string   `json:"degree,omitempty"`
    Tense        string   `json:"tense,omitempty"`
}

// SenseEntry: A single dictionary sense (noun, verb, etc.)
type SenseEntry struct {
    ID          string            `json:"id"`
    Category    string            `json:"category"`
    Gender      string            `json:"gender,omitempty"`
    Article     string            `json:"article,omitempty"`
    Meanings    []MeaningEntry     `json:"meanings"`
    Expressions []ExpressionEntry  `json:"expressions,omitempty"`
    WordForms   []WordFormEntry    `json:"word_forms,omitempty"`
}

// WordEntry: The top-level word container (multi-sense support).
type WordEntry struct {
    Word    string       `json:"word"`
    Senses  []SenseEntry `json:"senses"`
}