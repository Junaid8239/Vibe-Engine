# 🚀 VibeEngine: Warehouse-Native AI Agent

VibeEngine is a proof-of-concept AI marketing orchestration pipeline built to explore how enterprise-grade agentic workflows can be scaled safely. It simulates a "Human-in-the-Loop" architecture where an AI securely writes queries, targets specific user cohorts, and generates structured campaign configurations.

Inspired by the engineering challenges solved by modern AI automation platforms like Conversion AI.

## 🏗️ Core Architecture & Features

This project tackles three major engineering hurdles in enterprise AI:

1. **🔒 Zero-Data Exposure (Text-to-SQL)**
   * **Problem:** Sending raw database rows to an LLM (RAG) exposes sensitive PII and burns through token limits.
   * **Solution:** The LLM is only fed the database *schema*. It generates a secure SQLite `SELECT` query, and Python natively executes the query against the local database to fetch the target emails.

2. **⚙️ Deterministic Output (Pydantic & JSON Mode)**
   * **Problem:** LLMs naturally hallucinate conversational text, which breaks downstream API pipelines.
   * **Solution:** Enforced strict schema validation using Pydantic and Groq's JSON mode to guarantee the AI outputs a deterministic configuration artifact every time.

3. **🛡️ Fault Tolerance & Human-in-the-Loop Execution**
   * **Problem:** AI should never trigger external actions (like sending 10k emails) autonomously or crash during traffic spikes.
   * **Solution:** Implemented an exponential backoff loop for API rate limits. All generated artifacts are parked in a local SQLite `approval_queue` and await explicit human approval via the Streamlit UI before executing simulated background tasks.

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python 3
* **Database:** SQLite
* **AI Provider:** Groq API (Llama-3.3-70b-versatile)
* **Data Validation:** Pydantic

## 🚀 Quick Start Setup

**1. Clone the repository and install dependencies:**
```bash
git clone [https://github.com/yourusername/vibe-engine.git](https://github.com/yourusername/vibe-engine.git)
cd vibe-engine
pip install streamlit pydantic openai

**2. Set up your Groq API Key:
```bash
export GROQ_API_KEY="your_api_key_here"



**3. Initialize the Mock Database:
(Assuming you have a script named setup_db.py to create the initial tables and mock data)
```bash
python3 setup_db.py



**4. Run the Streamlit UI:
```bash
streamlit run ui.py


