-- Vocabulary App Database Schema
-- Run this script to create or update the database structure

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

-- Create user_progress table for spaced repetition
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

-- Insert default languages if they don't exist
INSERT IGNORE INTO languages (language, code) VALUES 
    ('Norwegian', 'no'),
    ('English', 'en'),
    ('German', 'de');

-- Insert default word types if they don't exist
INSERT IGNORE INTO word_types (wordtype) VALUES 
    ('noun'),
    ('verb'),
    ('adjective'),
    ('adverb'),
    ('pronoun'),
    ('preposition'),
    ('conjunction'),
    ('interjection');
