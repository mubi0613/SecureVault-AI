# 🛡️ SecureVault AI: Privacy-First RAG Knowledge Base

A production-grade, secure note-taking application that integrates **Retrieval-Augmented Generation (RAG)** with **Zero-Knowledge Encryption**. Built for users who need AI-powered insights without sacrificing data privacy.

## 🚀 Key Engineering Features
* **Hybrid Security Model:** Uses **PBKDF2** key derivation and **AES-256 (Fernet)** encryption. Data is only decrypted in-memory during an active session.
* **Local RAG Engine:** Utilizes **FAISS** (Facebook AI Similarity Search) and `all-MiniLM-L6-v2` embeddings for lightning-fast, local semantic search—no private data ever leaves your machine.
* **AI Observability:** Integrated **Token & Cost Tracker** and a **Feedback Loop** (Correct/Wrong logging) to audit retrieval accuracy and identify gaps in the knowledge base.
* **Fail-Safe Recovery:** Implements a hashed **Recovery Key** system for account resets while maintaining the mathematical integrity of encrypted data.
* **Smart Exports:** Unicode-compliant PDF and DOCX generation with specialized font embedding for multi-language support.

## 🛠️ Technical Stack
* **Frontend:** Streamlit (Custom CSS & Session Management)
* **AI/NLP:** Sentence-Transformers, TextBlob, FAISS
* **Cryptography:** Python `cryptography` library (SHA-256 & PBKDF2)
* **Data:** JSON-based persistent storage

---

## 🔐 Security Architecture
1. **PIN Hashing:** The Master PIN is never stored; only its **SHA-256** hash is kept for authentication.
2. **Zero-Knowledge:** The PIN is used to derive the encryption key. If the PIN is lost, "Secret" notes remain mathematically inaccessible.
3. **Auto-Lock Engine:** A session-based activity monitor automatically wipes the memory and locks the vault after 150 seconds of inactivity.



---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/mubi0613/SecureVault-AI.git](https://github.com/mubi0613/SecureVault-AI.git)
cd SecureVault-AI

2. Install Dependencies
Ensure you have Python 3.9+ installed, then run:
```bash
pip install -r requirements.txt

3. Run the Application
```bash
streamlit run main.py

📖 Usage Guide
Initialize: Set your Master PIN and save your Recovery Key.

Create Notes: Use the sidebar to add notes. Toggle "Mark as Secret" to apply AES-256 encryption.

AI Search: Open the "Ask Your Vault" expander to query your notes using natural language.

Manage: Edit or delete notes, and export them as PDF/DOCX for offline use.

Monitor: Check the "AI Resources" section in the sidebar to view estimated token usage and costs.

📂 Project Structure
Plaintext
SecureVault-AI/
├── main.py            # Streamlit UI & Session Management
├── vault_logic.py     # Cryptography, RAG, & File IO Logic
├── requirements.txt   # Project Dependencies
├── .gitignore         
├── fonts/             # Custom fonts for PDF Unicode support
└── README.md          # Documentation
⚠️ Important Note on Security
This application is designed with a Zero-Knowledge philosophy. The developers cannot recover your notes if you lose both your Master PIN and your Recovery Key. Data integrity is the sole responsibility of the user.

📜 License
Distributed under the MIT License. See LICENSE for more information.