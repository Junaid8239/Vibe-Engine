import sqlite3

def init_database():
    # This automatically creates a file named 'marketing.db' in your folder
    connection = sqlite3.connect("marketing.db")
    cursor = connection.cursor()

    print("Creating local database tables...")

    # 1. Create Contacts Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crm_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            company TEXT,
            account_tier TEXT DEFAULT 'Free',
            last_login_days INTEGER DEFAULT 0
        )
    """)

    # 2. Create a table to hold the AI-generated campaigns waiting for human approval
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS approval_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_name TEXT,
            status TEXT DEFAULT 'Pending Approval',
            structured_json_artifact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Insert some mock data to play with
    mock_contacts = [
        ('alex@enterprise.com', 'Alex Rivera', 'Acme Corp', 'Enterprise', 45),
        ('sam@startup.io', 'Sam Chen', 'ByteSize', 'Growth', 12),
        ('taylor@global.com', 'Taylor Swift', 'Global Tech', 'Enterprise', 32),
        ('jordan@free.dev', 'Jordan Lee', 'Freelance', 'Free', 2)
    ]

    try:
        cursor.executemany("""
            INSERT OR IGNORE INTO crm_contacts (email, full_name, company, account_tier, last_login_days)
            VALUES (?, ?, ?, ?, ?)
        """, mock_contacts)
        connection.commit()
        print("Database initialized successfully! 'marketing.db' created.")
    except Exception as e:
        print(f"Error populating data: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    init_database()