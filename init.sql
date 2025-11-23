-- Database initialization script for FINALSERVER
-- This script runs automatically when PostgreSQL container starts for the first time

-- Enable extension for better JSON support (optional)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    tokens INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create model_metadata table
CREATE TABLE IF NOT EXISTS model_metadata (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255) UNIQUE NOT NULL,
    model_type VARCHAR(255) NOT NULL,
    features JSON NOT NULL,
    label VARCHAR(255) NOT NULL,
    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(255) NOT NULL,
    metrics JSON
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_tokens ON users(tokens);
CREATE INDEX IF NOT EXISTS idx_model_metadata_name ON model_metadata(model_name);
CREATE INDEX IF NOT EXISTS idx_model_metadata_type ON model_metadata(model_type);
CREATE INDEX IF NOT EXISTS idx_model_metadata_trained_at ON model_metadata(trained_at);

-- Insert a welcome message (optional - for testing)
DO $$
BEGIN
    RAISE NOTICE 'Database tables created successfully!';
    RAISE NOTICE 'Tables: users, model_metadata';
    RAISE NOTICE 'Indexes created for optimal performance';
END $$;
