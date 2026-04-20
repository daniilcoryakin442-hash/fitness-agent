-- SQL для создания таблиц в Supabase
-- Выполни этот скрипт в разделе SQL Editor в Supabase

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    name TEXT,
    age INT,
    weight FLOAT,
    height FLOAT,
    goal TEXT,
    restrictions TEXT,
    records JSONB DEFAULT '{}',
    sleep_target FLOAT DEFAULT 8,
    custom_schedule JSONB,
    training_mode TEXT DEFAULT 'зал',
    sport_type TEXT DEFAULT 'фитнес',
    target_reps INT DEFAULT 8,
    custom_exercises JSONB DEFAULT '{}',
    last_active TIMESTAMP
);

CREATE TABLE IF NOT EXISTS measurements (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    weight FLOAT,
    date DATE
);

CREATE TABLE IF NOT EXISTS sleep (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    hours FLOAT,
    date DATE
);

CREATE TABLE IF NOT EXISTS exercises_catalog (
    id SERIAL PRIMARY KEY,
    name TEXT,
    muscle_group TEXT,
    training_mode TEXT
);

CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    name TEXT,
    cuisine TEXT,
    category TEXT,
    ingredients TEXT,
    instructions TEXT,
    image_url TEXT
);
