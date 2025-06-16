-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Digital Twins Table
CREATE TABLE digital_twins (
    twin_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    personality_traits JSONB DEFAULT '[]',
    conversational_style JSONB DEFAULT '{}',
    background TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Stories Table
CREATE TABLE stories (
    story_id VARCHAR(255) PRIMARY KEY,
    twin_id VARCHAR(255) REFERENCES digital_twins(twin_id) ON DELETE CASCADE,
    title VARCHAR(500),
    full_content TEXT,
    themes TEXT[],
    emotional_tone VARCHAR(100),
    adaptability_level FLOAT DEFAULT 0.5,
    key_facts JSONB DEFAULT '[]',
    conversation_triggers TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Story Segments Table
CREATE TABLE story_segments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    story_id VARCHAR(255) REFERENCES stories(story_id) ON DELETE CASCADE,
    segment_order INTEGER,
    segment_type VARCHAR(100),
    content TEXT,
    transition_hook TEXT,
    interaction_points JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW()
);

-- User Memory Table (using chat_id as user_id)
-- Note: profile is shared across all twins, but conversation_history tracks twin_id
CREATE TABLE user_memory (
    chat_id BIGINT PRIMARY KEY,
    profile JSONB DEFAULT '{}',
    conversation_history JSONB DEFAULT '[]',
    shared_topics TEXT[],
    emotional_reactions JSONB DEFAULT '{}',
    last_interaction TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- User Story Progress Table (now includes twin_id for isolation)
CREATE TABLE user_story_progress (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    chat_id BIGINT REFERENCES user_memory(chat_id) ON DELETE CASCADE,
    story_id VARCHAR(255) REFERENCES stories(story_id) ON DELETE CASCADE,
    twin_id VARCHAR(255) REFERENCES digital_twins(twin_id) ON DELETE CASCADE,
    current_segment INTEGER DEFAULT 1,
    segments_completed INTEGER[],
    completion_status VARCHAR(50) DEFAULT 'in_progress',
    last_interaction TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(chat_id, story_id, twin_id)  -- Each user-story-twin combination is unique
);

-- Conversation Sessions Table (now twin-specific)
CREATE TABLE conversation_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    chat_id BIGINT REFERENCES user_memory(chat_id) ON DELETE CASCADE,
    twin_id VARCHAR(255) REFERENCES digital_twins(twin_id) ON DELETE CASCADE,
    current_story_id VARCHAR(255),
    session_state VARCHAR(100) DEFAULT 'active',
    context_data JSONB DEFAULT '{}',
    started_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX idx_user_memory_chat_id ON user_memory(chat_id);
CREATE INDEX idx_story_segments_story_id ON story_segments(story_id, segment_order);
CREATE INDEX idx_user_story_progress_chat_twin ON user_story_progress(chat_id, twin_id);
CREATE INDEX idx_conversation_sessions_chat_twin ON conversation_sessions(chat_id, twin_id);
CREATE INDEX idx_stories_twin_id ON stories(twin_id);
CREATE INDEX idx_story_segments_story_order ON story_segments(story_id, segment_order);

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for digital_twins
CREATE TRIGGER update_digital_twins_updated_at 
    BEFORE UPDATE ON digital_twins 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();