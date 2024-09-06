CREATE TABLE IF NOT EXISTS Messages
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    conversation_id INT NOT NULL,
    conversation_order INT NOT NULL,
    role TEXT NOT NULL
);