# Statistics Learning Module - Setup Guide

## Overview

This guide explains how to set up and use the new Statistics learning module in the Vocabulary App. The app now supports not just language vocabulary, but also interactive statistics questions using spaced repetition!

## Database Setup

### Step 1: Run the Statistics Schema

First, apply the statistics schema extension to add the necessary tables:

```bash
# Connect to your MySQL database
mysql -u root -p vocabulary_app

# Run the schema extension
source backend/statistics_schema.sql;
```

This creates the following new tables:
- `subjects` - Different learning subjects (Statistics, Language, etc.)
- `question_types` - Types of questions (multiple choice, true/false, etc.)
- `questions` - The actual questions
- `answer_options` - Answer choices for each question
- `user_question_progress` - Tracks learning progress for questions

### Step 2: Import Statistics Questions

Next, import the comprehensive set of statistics questions:

```bash
# Still in MySQL
source backend/import_statistics_questions.sql;
```

This imports 25+ statistics questions covering:
- **P-values** - Understanding hypothesis testing
- **Residuals** - Regression analysis concepts
- **Linear Models** - R², coefficients, assumptions
- **ANOVA** - Analysis of variance
- **ANCOVA** - Analysis of covariance
- **Core Concepts** - Central Limit Theorem, confidence intervals, Type I/II errors, etc.

Each question includes:
- Multiple answer options
- Detailed explanations
- LaTeX mathematical notation support
- Difficulty levels (beginner, intermediate, advanced)

## Backend Setup

The backend now includes two new route modules:

### 1. Subjects Routes (`/subjects`)
- `GET /subjects/` - List all subjects
- `GET /subjects/{id}` - Get subject details
- `GET /subjects/{id}/questions` - Get questions for a subject

### 2. Question Review Routes (`/question-review`)
- `GET /question-review/due` - Get due questions for review
- `GET /question-review/new` - Get new questions to learn
- `POST /question-review/add-question` - Add question to learning queue
- `POST /question-review/submit` - Submit answer and get feedback
- `GET /question-review/stats` - Get learning statistics

These routes are automatically registered in `main.py`.

## Features

### Interactive Question Types
- **Multiple Choice** - Select the best answer
- **True/False** - Simple boolean questions
- **LaTeX Support** - Mathematical equations rendered beautifully

### Spaced Repetition
Questions use the same SM-2 algorithm as vocabulary:
- Questions are scheduled for optimal review intervals
- Correct answers increase intervals
- Incorrect answers reset to learning phase
- Progress tracked: new → learning → review → mastered

### Instant Feedback
After answering:
- See if you're correct immediately
- View the correct answer
- Read detailed explanations
- Understand why answers are right or wrong

### Progress Tracking
- Track accuracy per subject
- Monitor questions in each learning stage
- See total reviews and mastery progress

## Testing the API

### 1. Get Available Subjects
```bash
curl http://localhost:8000/subjects/
```

### 2. Get Statistics Questions
```bash
curl "http://localhost:8000/subjects/1/questions?difficulty=beginner&limit=5"
```

### 3. Get New Questions to Learn (Requires Auth)
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/question-review/new?subject_id=1&limit=10"
```

### 4. Add Question to Learning Queue (Requires Auth)
```bash
curl -X POST http://localhost:8000/question-review/add-question \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"question_id": 1}'
```

### 5. Submit Answer (Requires Auth)
```bash
curl -X POST http://localhost:8000/question-review/submit \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"question_id": 1, "selected_option_id": 2}'
```

### 6. Get Learning Stats (Requires Auth)
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/question-review/stats?subject_id=1"
```

## Question Format

Questions in the database follow this structure:

```sql
questions:
  - id
  - subject_id (foreign key to subjects)
  - question_type_id (foreign key to question_types)
  - question_text (plain text question)
  - question_latex (optional LaTeX for math)
  - explanation (detailed explanation of the concept)
  - difficulty_level (beginner/intermediate/advanced)
  - image_url (optional graph/diagram)

answer_options:
  - id
  - question_id
  - option_text (the answer choice)
  - option_latex (optional LaTeX for math)
  - is_correct (boolean)
  - explanation (why this option is right/wrong)
```

## Adding More Questions

To add more statistics questions or questions for other subjects:

1. Create a new SQL file following the pattern in `import_statistics_questions.sql`
2. Define your subject (or use existing)
3. Insert questions with their answer options
4. Each question should have 2-4 answer options
5. Mark the correct answer with `is_correct = TRUE`

Example:
```sql
SET @stat_id = (SELECT id FROM subjects WHERE code = 'STAT');
SET @mc_id = (SELECT id FROM question_types WHERE type_name = 'multiple_choice');

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level)
VALUES (@stat_id, @mc_id, 
    'What is the median?',
    'The median is the middle value when data is ordered.',
    'beginner');
SET @q_id = LAST_INSERT_ID();

INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@q_id, 'The middle value in ordered data', TRUE),
    (@q_id, 'The most frequent value', FALSE),
    (@q_id, 'The average value', FALSE);
```

## Bug Fixed

Fixed missing `timedelta` import in `routes/review.py` that would have caused errors when calculating streak information.

## Next Steps

Frontend development is recommended to create user interfaces for:
1. Browsing available subjects
2. Selecting statistics topics to study
3. Interactive question interface with LaTeX rendering
4. Progress dashboard showing statistics learning progress
5. Combined view showing both vocabulary and statistics progress

The backend is fully functional and ready to support these frontend features!
