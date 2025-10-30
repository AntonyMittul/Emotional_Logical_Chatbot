/*
  # Create Chat History Tables

  1. New Tables
    - `chats`
      - `id` (uuid, primary key) - Unique identifier for each chat session
      - `name` (text) - Name/title of the chat session
      - `created_at` (timestamptz) - When the chat was created
      - `updated_at` (timestamptz) - Last modification time
    
    - `messages`
      - `id` (uuid, primary key) - Unique identifier for each message
      - `chat_id` (uuid, foreign key) - Reference to the chat session
      - `role` (text) - Either 'user' or 'assistant'
      - `content` (text) - The message content
      - `message_type` (text) - Either 'emotional' or 'logical'
      - `created_at` (timestamptz) - When the message was sent

  2. Security
    - Enable RLS on both tables
    - Public access for demo purposes (can be restricted later with auth)

  3. Indexes
    - Index on chat_id for efficient message retrieval
    - Index on created_at for chronological ordering
*/

-- Create chats table
CREATE TABLE IF NOT EXISTS chats (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  chat_id uuid NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
  role text NOT NULL CHECK (role IN ('user', 'assistant')),
  content text NOT NULL,
  message_type text CHECK (message_type IN ('emotional', 'logical')),
  created_at timestamptz DEFAULT now()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_chats_updated_at ON chats(updated_at DESC);

-- Enable Row Level Security
ALTER TABLE chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (for demo purposes)
CREATE POLICY "Allow public read access to chats"
  ON chats FOR SELECT
  USING (true);

CREATE POLICY "Allow public insert to chats"
  ON chats FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public update to chats"
  ON chats FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete from chats"
  ON chats FOR DELETE
  USING (true);

CREATE POLICY "Allow public read access to messages"
  ON messages FOR SELECT
  USING (true);

CREATE POLICY "Allow public insert to messages"
  ON messages FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public update to messages"
  ON messages FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete from messages"
  ON messages FOR DELETE
  USING (true);
