import streamlit as st
import sqlite3
import pandas as pd
import time
from app import run_ai_orchestrator 

st.title("🚀 VibeEngine: AI Marketing Agent (POC)")
st.write("A warehouse-native AI orchestration pipeline simulating Conversion AI's architecture.")

# 1. Initialize session state components
if "campaign_generated" not in st.session_state:
    st.session_state.campaign_generated = False
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# 2. Show the live database context
st.subheader("1. Live Data Context (SQLite)")
conn_context = sqlite3.connect("marketing.db")
df = pd.read_sql_query("SELECT * FROM crm_contacts", conn_context)
st.dataframe(df)
conn_context.close()

# 3. User Input
user_prompt = st.text_input("Enter Campaign Prompt:", "Re-engage  users inactive for 10 days.")

# --- THE FIX: STATE SYNCHRONIZATION ---
# If the text box changes, wipe out the old artifact flag so it disappears from the screen!
if user_prompt != st.session_state.last_prompt:
    st.session_state.campaign_generated = False

# 4. Execution Button
if st.button("Generate Campaign Artifact"):
    with st.spinner("Querying database, applying backoff, and generating strict JSON..."):
        
        success = run_ai_orchestrator(user_prompt)
        
        # --- THE FIX: We explicitly check for True now ---
        if success == True:
            st.session_state.campaign_generated = True 
            st.session_state.last_prompt = user_prompt 
            st.success("Pipeline executed successfully!")
            st.balloons()
            
        else:
            # --- THE FIX: We explicitly wipe the memory if it fails, hiding the old queue! ---
            st.session_state.campaign_generated = False
            st.error("API Error: Upstream AI server is overloaded. Exponential backoff reached max retries. Please try again later.")

# 5. Display Queue Only When Active and Synchronized
if st.session_state.campaign_generated:
    st.subheader("2. Human-in-the-Loop Approval Queue")
    conn_queue = sqlite3.connect("marketing.db")
    queue_df = pd.read_sql_query(
        "SELECT * FROM approval_queue ORDER BY id DESC LIMIT 1", 
        conn_queue
    )
    
    st.write("**Queue Metadata:**")
    display_columns = queue_df[['id', 'campaign_name', 'status', 'created_at']]
    st.dataframe(display_columns)
    
    st.write("**Generated Campaign Artifact (JSON):**")
    artifact_string = queue_df.iloc[0]['structured_json_artifact']
    st.json(artifact_string) 
    
    pending_id = int(queue_df.iloc[0]['id'])
    conn_queue.close()
    
    st.write("---")
    st.subheader("3. Execution Layer (Simulated Asynchronous Worker)")
    
    if st.button("Approve & Execute Campaign"):
        with st.status("Pushing task to background worker...", expanded=True) as status:
            st.write("Connecting to email API...")
            time.sleep(1)
            st.write(f"Executing payload for: {queue_df.iloc[0]['campaign_name']}")
            time.sleep(1.5)
            
            conn_update = sqlite3.connect("marketing.db")
            cursor = conn_update.cursor()
            cursor.execute(
                "UPDATE approval_queue SET status = 'Executed' WHERE id = ?", 
                (pending_id,)
            )
            conn_update.commit()
            conn_update.close()
            
            status.update(label="Campaign Executed Successfully!", state="complete", expanded=False)
        
        st.success("The AI campaign artifact was approved and executed safely!")