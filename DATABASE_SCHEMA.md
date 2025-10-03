# Database Schema Documentation

This document describes the database structure for the Vocabulary App.

## Overview

The database is designed to support:
- Multi-language vocabulary storage
- User authentication and management
- Word meanings and translations
- User progress tracking for spaced repetition
- Future expansion to other subjects (math, statistics, etc.)

## Core Tables

### `users`
Stores user account information.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT PRIMARY KEY AUTO_INCREMENT | Unique user identifier |
| `email` | VARCHAR(255) UNIQUE NOT NULL | User's email address |
| `password_hash` | VARCHAR(255) NOT NULL | Bcrypt hashed password |
| `type` | VARCHAR(50) DEFAULT 'basic' | User type (basic, premium, admin) |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Account creation time |

### `languages`
Stores available languages for vocabulary.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT PRIMARY KEY AUTO_INCREMENT | Language identifier |
| `language` | VARCHAR(100) UNIQUE NOT NULL | Language name (e.g., "Norwegian", "English") |
| `code` | VARCHAR(10) UNIQUE | ISO language code (e.g., "no", "en") |

### `word_types`
Stores word categories (noun, verb, adjective, etc.).

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT PRIMARY KEY AUTO_INCREMENT | Word type identifier |
| `wordtype` | VARCHAR(50) UNIQUE NOT NULL | Word type name (e.g., "noun", "verb") |

### `words`
Stores vocabulary words.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT PRIMARY KEY AUTO_INCREMENT | Word identifier |
| `word` | VARCHAR(255) NOT NULL | The actual word |
| `wordtype` | INT | Foreign key to `word_types.id` |
| `language` | INT | Foreign key to `languages.id` |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | When word was added |

**Indexes:**
- `INDEX idx_word_language (word, language)` - For quick lookups
- `UNIQUE KEY unique_word_language (word, language)` - Prevent duplicates

### `meanings`
Stores definitions and translations for words.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT PRIMARY KEY AUTO_INCREMENT | Meaning identifier |
| `word_id` | INT NOT NULL | Foreign key to `words.id` |
| `language_id` | INT NOT NULL | Language of this meaning/translation |
| `definition` | TEXT NOT NULL | The definition or translation |
| `note` | TEXT | Additional notes or context |

**Indexes:**
- `INDEX idx_word_id (word_id)` - For efficient joins

### `user_progress`
Tracks user learning progress for spaced repetition.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT PRIMARY KEY AUTO_INCREMENT | Progress record identifier |
| `user_id` | INT NOT NULL | Foreign key to `users.id` |
| `word_id` | INT NOT NULL | Foreign key to `words.id` |
| `ease_factor` | FLOAT DEFAULT 2.5 | SM-2 algorithm ease factor (2.5 is default) |
| `interval_days` | INT DEFAULT 0 | Days until next review |
| `repetitions` | INT DEFAULT 0 | Number of successful reviews |
| `review_count` | INT DEFAULT 0 | Total number of reviews |
| `correct_count` | INT DEFAULT 0 | Number of correct reviews |
| `last_reviewed` | TIMESTAMP | Date/time of last review |
| `next_review` | TIMESTAMP | Date/time of next scheduled review |
| `status` | ENUM('new', 'learning', 'review', 'mastered') DEFAULT 'new' | Learning status |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | When user first encountered word |
| `updated_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Last update time |

**Indexes:**
- `UNIQUE KEY unique_user_word (user_id, word_id)` - One progress record per user per word
- `INDEX idx_next_review (user_id, next_review)` - For efficient review queries
- `INDEX idx_status (user_id, status)` - Filter by learning status

**Constraints:**
- `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`
- `FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE`

### `user_statistics`
Aggregated user statistics for dashboard display.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT PRIMARY KEY AUTO_INCREMENT | Statistics identifier |
| `user_id` | INT UNIQUE NOT NULL | Foreign key to `users.id` |
| `words_learned` | INT DEFAULT 0 | Total words learned |
| `words_mastered` | INT DEFAULT 0 | Words marked as mastered |
| `total_reviews` | INT DEFAULT 0 | Total number of reviews performed |
| `correct_reviews` | INT DEFAULT 0 | Number of correct reviews |
| `current_streak` | INT DEFAULT 0 | Current daily review streak |
| `longest_streak` | INT DEFAULT 0 | Longest daily review streak |
| `last_review_date` | DATE | Last date user reviewed |
| `updated_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Last update time |

**Constraints:**
- `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`

## SQL Schema Creation

```sql
-- Create languages table
CREATE TABLE IF NOT EXISTS languages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    language VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(10) UNIQUE
);

-- Create word_types table
CREATE TABLE IF NOT EXISTS word_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    wordtype VARCHAR(50) UNIQUE NOT NULL
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    type VARCHAR(50) DEFAULT 'basic',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create words table
CREATE TABLE IF NOT EXISTS words (
    id INT PRIMARY KEY AUTO_INCREMENT,
    word VARCHAR(255) NOT NULL,
    wordtype INT,
    language INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (wordtype) REFERENCES word_types(id),
    FOREIGN KEY (language) REFERENCES languages(id),
    UNIQUE KEY unique_word_language (word, language),
    INDEX idx_word_language (word, language)
);

-- Create meanings table
CREATE TABLE IF NOT EXISTS meanings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    word_id INT NOT NULL,
    language_id INT NOT NULL,
    definition TEXT NOT NULL,
    note TEXT,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
    FOREIGN KEY (language_id) REFERENCES languages(id),
    INDEX idx_word_id (word_id)
);

-- Create user_progress table
CREATE TABLE IF NOT EXISTS user_progress (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    word_id INT NOT NULL,
    ease_factor FLOAT DEFAULT 2.5,
    interval_days INT DEFAULT 0,
    repetitions INT DEFAULT 0,
    review_count INT DEFAULT 0,
    correct_count INT DEFAULT 0,
    last_reviewed TIMESTAMP NULL,
    next_review TIMESTAMP NULL,
    status ENUM('new', 'learning', 'review', 'mastered') DEFAULT 'new',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_word (user_id, word_id),
    INDEX idx_next_review (user_id, next_review),
    INDEX idx_status (user_id, status),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

-- Create user_statistics table
CREATE TABLE IF NOT EXISTS user_statistics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL,
    words_learned INT DEFAULT 0,
    words_mastered INT DEFAULT 0,
    total_reviews INT DEFAULT 0,
    correct_reviews INT DEFAULT 0,
    current_streak INT DEFAULT 0,
    longest_streak INT DEFAULT 0,
    last_review_date DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## Spaced Repetition Algorithm (SM-2)

The `user_progress` table implements the SuperMemo 2 (SM-2) algorithm for spaced repetition:

1. **ease_factor**: Quality of recall (default 2.5)
   - Increases when answer is correct
   - Decreases when answer is incorrect
   - Minimum value: 1.3

2. **interval_days**: Days until next review
   - Starts at 0 (new word)
   - First successful review: 1 day
   - Second successful review: 6 days
   - Subsequent: interval = previous_interval × ease_factor

3. **repetitions**: Number of consecutive successful reviews

4. **status**: Current learning stage
   - `new`: Word just added, never reviewed
   - `learning`: Currently learning (interval < 7 days)
   - `review`: In review mode (interval >= 7 days)
   - `mastered`: Fully learned (interval > 30 days, ease_factor > 2.5)

## Future Extensions

### Subject Categories
To expand beyond vocabulary to other subjects (math, statistics):

```sql
CREATE TABLE subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- Add subject_id to existing tables
ALTER TABLE words ADD COLUMN subject_id INT DEFAULT 1; -- 1 = vocabulary
ALTER TABLE words ADD FOREIGN KEY (subject_id) REFERENCES subjects(id);
```

### Custom Word Lists
Allow users to organize words into custom lists:

```sql
CREATE TABLE word_lists (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE word_list_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    list_id INT NOT NULL,
    word_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (list_id) REFERENCES word_lists(id) ON DELETE CASCADE,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
    UNIQUE KEY unique_list_word (list_id, word_id)
);
```

## Migration Guide

To update an existing database with the new tables:

1. Back up your database
2. Run the SQL schema creation commands above
3. Existing data will be preserved
4. New tables will be created if they don't exist
