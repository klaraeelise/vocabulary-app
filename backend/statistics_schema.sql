-- Statistics Learning Module Schema Extension
-- This extends the vocabulary app to support statistics and other subjects

-- Create subjects table (to support multiple learning subjects)
CREATE TABLE IF NOT EXISTS subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create question_types table
CREATE TABLE IF NOT EXISTS question_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- Create questions table for statistics and other subjects
CREATE TABLE IF NOT EXISTS questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subject_id INT NOT NULL,
    question_type_id INT NOT NULL,
    question_text TEXT NOT NULL,
    question_latex TEXT,  -- For mathematical notation
    explanation TEXT,
    difficulty_level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'intermediate',
    image_url VARCHAR(500),  -- For graphs/diagrams
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (question_type_id) REFERENCES question_types(id),
    INDEX idx_subject_difficulty (subject_id, difficulty_level)
);

-- Create answer_options table for multiple choice questions
CREATE TABLE IF NOT EXISTS answer_options (
    id INT PRIMARY KEY AUTO_INCREMENT,
    question_id INT NOT NULL,
    option_text TEXT NOT NULL,
    option_latex TEXT,
    is_correct BOOLEAN DEFAULT FALSE,
    explanation TEXT,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    INDEX idx_question (question_id)
);

-- Create user_question_progress table (similar to user_progress but for questions)
CREATE TABLE IF NOT EXISTS user_question_progress (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    question_id INT NOT NULL,
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
    UNIQUE KEY unique_user_question (user_id, question_id),
    INDEX idx_next_review (user_id, next_review),
    INDEX idx_status (user_id, status),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Insert default subjects
INSERT IGNORE INTO subjects (name, code, description) VALUES 
    ('Statistics', 'STAT', 'Statistical concepts, methods, and analysis'),
    ('Language', 'LANG', 'Language vocabulary and grammar');

-- Insert default question types
INSERT IGNORE INTO question_types (type_name, description) VALUES 
    ('multiple_choice', 'Multiple choice with one correct answer'),
    ('true_false', 'True or false question'),
    ('fill_blank', 'Fill in the blank'),
    ('matching', 'Match items from two lists'),
    ('short_answer', 'Short text answer');
