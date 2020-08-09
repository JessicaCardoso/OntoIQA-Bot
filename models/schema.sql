CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    first_name TEXT
);

CREATE TABLE IF NOT EXISTS user_history (
    id SERIAL PRIMARY KEY,
    bot_id INTEGER NOT NULL,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS turns(
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL,
    history_id INTEGER REFERENCES user_history(id),
    user_text TEXT NOT NULL,
    bot_text TEXT NOT NULL,
    bot_answer_score INTEGER,
    created_at TIMESTAMP 
);

CREATE TABLE IF NOT EXISTS suggestions(
    id SERIAL PRIMARY KEY,
    turn_id INTEGER REFERENCES turns(id),
    suggestion_text TEXT 
);