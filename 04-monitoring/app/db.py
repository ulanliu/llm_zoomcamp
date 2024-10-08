import psycopg2
from psycopg2 import sql
import uuid
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class PostgresDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST')
        )
        self.create_tables()

    def conn_close(self):
        self.conn.close()
        print("connection closed")

    def create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id UUID PRIMARY KEY,
                    question TEXT,
                    answer TEXT,
                    course TEXT NOT NULL,
                    model_used TEXT NOT NULL,
                    response_time FLOAT NOT NULL,
                    relevance TEXT NOT NULL,
                    relevance_explanation TEXT NOT NULL,
                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    eval_prompt_tokens INTEGER NOT NULL,
                    eval_completion_tokens INTEGER NOT NULL,
                    eval_total_tokens INTEGER NOT NULL,
                    openai_cost FLOAT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id UUID REFERENCES conversations(id),
                    feedback INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        self.conn.commit()

    def generate_conversation_id(self):
        return uuid.uuid4()

    def save_conversation(self, conversation_id, question, answer):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO conversations (id, question, answer) VALUES (%s, %s, %s)",
                (conversation_id, question, answer)
            )
        self.conn.commit()

    def save_feedback(self, conversation_id, feedback):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO feedback (conversation_id, feedback) VALUES (%s, %s)",
                (conversation_id, feedback)
            )
        self.conn.commit()
        
