import os
import sqlite3
import json
import time
from openai import OpenAI
from pydantic import BaseModel

# 1. The New Blueprint: We ask the AI for a SQL query, NOT for user emails!
class AgentResponse(BaseModel):
    sql_query: str
    campaign_title: str
    subject_line: str
    action_type: str

# For Groq:
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# 2. ENTERPRISE SECURITY: Only send the Schema, never the data.
def get_database_schema():
    """Returns ONLY the table structure. Zero PII (Personally Identifiable Information) is exposed."""
    return (
        "Table Name: crm_contacts\n"
        "Columns:\n"
        "- email (TEXT)\n"
        "- full_name (TEXT)\n"
        "- company (TEXT)\n"
        "- account_tier (TEXT) -- Allowed Values: 'Enterprise', 'Growth', 'Free'\n"
        "- last_login_days (INTEGER) -- Number of days since last login\n"
    )

# 3. The Enterprise Orchestrator
def run_ai_orchestrator(user_instruction):
    print("\nStep 1: Fetching Database Schema (Zero user data exposed)...")
    db_schema = get_database_schema()

    print("Step 2: Asking AI to write a SQL query based on the prompt...")
    
    # We tell the AI to act as a data engineer writing SQL
    full_prompt = (
        f"You are an enterprise AI data engineer.\n"
        f"Database Schema:\n{db_schema}\n\n"
        f"User Instruction: {user_instruction}\n\n"
        f"TASK:\n"
        f"1. Write a valid SQLite 'SELECT email FROM crm_contacts WHERE...' query to find the exact users requested.\n"
        f"2. Generate a catchy campaign_title and subject_line based on the instruction.\n"
        f"3. action_type should always be 'email'.\n"
        f"SECURITY RULE: ONLY output SELECT queries. Never UPDATE or DELETE.\n\n"
        f"IMPORTANT: You must output ONLY valid JSON matching this exact schema:\n"
        f"{json.dumps(AgentResponse.model_json_schema(), indent=2)}"
    )

    max_retries = 4
    base_delay = 3

    for attempt in range(max_retries):
        try:
            # We call the Groq API endpoint using the OpenAI SDK format
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "user", "content": full_prompt}],
                response_format={"type": "json_object"}
            )
            
            # Extract the raw JSON string and parse it safely into our Pydantic model
            raw_json = response.choices[0].message.content
            ai_output = AgentResponse.model_validate_json(raw_json)
            
            print(f"\nStep 3: AI Generated SQL securely! -> {ai_output.sql_query}")
            
            # --- ENTERPRISE STEP 4: Execute SQL Securely in Python ---
            print("Step 4: Python executing SQL against local database...")
            connection = sqlite3.connect("marketing.db")
            cursor = connection.cursor()
            
            # Basic security check to prevent rogue AI commands
            if not ai_output.sql_query.strip().upper().startswith("SELECT"):
                print("[Security Error] AI generated a non-SELECT query. Aborting pipeline.")
                return False
                
            cursor.execute(ai_output.sql_query)
            rows = cursor.fetchall()
            connection.close()
            
            # Extract just the emails from the database results
            target_emails = [row[0] for row in rows]
            print(f"-> Python securely fetched {len(target_emails)} emails: {target_emails}")
            
            # --- ENTERPRISE STEP 5: Assemble the final JSON Artifact ---
            final_artifact = {
                "campaign_title": ai_output.campaign_title,
                "target_emails": target_emails,
                "action_type": ai_output.action_type,
                "subject_line": ai_output.subject_line
            }
            
            json_string = json.dumps(final_artifact)
            save_to_approval_queue(ai_output.campaign_title, json_string)
            
            return True 

        except Exception as e:
            error_message = str(e)
            if "503" in error_message or "429" in error_message:
                if attempt == max_retries - 1:
                    print("\n[Error] Max retries reached. The Groq API is temporarily overloaded.")
                    return False 
                
                wait_time = base_delay * (2 ** attempt)
                print(f"[Warning] API Overloaded. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"\n[Error] An unexpected error occurred: {e}")
                return False

def save_to_approval_queue(title, json_artifact):
    print("Step 6: Writing the assembled artifact into the 'approval_queue' table...")
    connection = sqlite3.connect("marketing.db")
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO approval_queue (campaign_name, structured_json_artifact)
        VALUES (?, ?)
    """, (title, json_artifact))
    connection.commit()
    connection.close()
    print("Successfully saved! Pipeline complete.")

if __name__ == "__main__":
    prompt = "Target all Growth users for a new campaign."
    run_ai_orchestrator(prompt)