package models

// ExampleEntry represents a single example sentence tied to a meaning.
type ExampleEntry struct {
    Sentence string `json:"sentence"`
}

// MeaningEntry represents a single meaning of a word, with optional examples.
type MeaningEntry struct {
    Description string         `json:"description"`
    Examples    []ExampleEntry  `json:"examples,omitempty"`
}

// ExpressionEntry represents "Faste uttrykk" idioms with their explanations.
type ExpressionEntry struct {
    Phrase      string `json:"phrase"`
    Explanation string `json:"explanation"`
}
// WordFormEntry represents a single row in the bøyning table.
type WordFormEntry struct {
    Label        string   `json:"label"`
    Forms        []string `json:"forms"`
    Number       string   `json:"number,omitempty"`
    Definiteness string   `json:"definiteness,omitempty"`
    Gender       string   `json:"gender,omitempty"`
    Degree       string   `json:"degree,omitempty"`
    Tense        string   `json:"tense,omitempty"`
}


// WordEntry remains focused on core word data.
type WordEntry struct {
    Word         string            `json:"word"`
    Category     string            `json:"category"`
    Gender       string            `json:"gender,omitempty"`
    Article      string            `json:"article,omitempty"`
    Meanings     []MeaningEntry     `json:"meanings"`
    Expressions  []ExpressionEntry  `json:"expressions,omitempty"`
    WordForms    []WordFormEntry    `json:"word_forms,omitempty"` // ✅ Still nested but cleanly typed
}
