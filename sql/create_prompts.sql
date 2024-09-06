CREATE TABLE IF NOT EXISTS Prompts
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    author TEXT NOT NULL,
    name TEXT,
    evaluation TEXT,
    describe TEXT
);