CREATE TABLE IF NOT EXISTS public.moderation_results (
    task_id SERIAL PRIMARY KEY,
    item_id INTEGER UNIQUE, -- C REFERENCES advertisements(id) не запускается
    status VARCHAR(20) NOT NULL,
    is_violation BOOLEAN,
    probability FLOAT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);