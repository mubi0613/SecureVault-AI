import streamlit as st
from datetime import datetime
import vault_logic as vl
import time
import json
import os

# --- CONFIGURATION ---
AUTO_LOCK_SECONDS = 150  # 2 Minutes

st.set_page_config(page_title="AI Vault", layout="wide")

# --- 0. FIRST TIME SETUP ---
if not vl.is_vault_initialized():
    st.title("🔒 Initialize Your Secure Vault")
    
    # 1. Primary Action: The PIN Box
    st.info("👋 Welcome! To get started, please set your Master PIN below.")
    
    with st.form("setup_form"):
        new_pin = st.text_input("Create Master PIN", type="password", help="Minimum 4 digits")
        conf_pin = st.text_input("Confirm Master PIN", type="password")
        submit = st.form_submit_button("Setup Vault", type="primary")
    
    # 2. Professional Spacing
    st.write("")
    st.write("") 
    st.divider()
    
    # 3. Security & Recovery Information
    if 'generated_recovery' not in st.session_state:
        st.session_state.generated_recovery = vl.generate_recovery_key()

    st.warning("⚠️ **CRITICAL: Save Your Recovery Key**")
    st.caption("RECOVERY - KEY : This is the ONLY way to reset your vault access if you forget your PIN.")
    st.code(st.session_state.generated_recovery, language=None)
    
    # Important Security Note (Liability Waiver)
    st.markdown("""
        <div style="background-color: #ff4b4b11; padding: 20px; border-radius: 10px; border: 1px solid #ff4b4b;">
            <p style="color: #ff4b4b; font-weight: bold; margin-bottom: 5px;">🛑 Important Security Notice:</p>
            <p style="font-size: 0.9rem; margin-bottom: 10px;">
                This vault utilizes <b>Zero-Knowledge AES-Encryption</b>. Your PIN is never stored; it is only hashed. 
                While the Recovery Key can reset app access, it <b>cannot decrypt</b> existing secret data 
                locked with a different PIN.
            </p>
            <p style="font-size: 0.8rem; opacity: 0.8;">
                <i>The developer holds no responsibility for data loss resulting from forgotten credentials.</i>
            </p>
        </div>
    """, unsafe_allow_html=True)
            
    if submit:        
        if new_pin == conf_pin and len(new_pin) >= 4:
            vl.initialize_vault(new_pin, st.session_state.generated_recovery)
            st.success("Vault Securely Initialized! Refreshing...")
            time.sleep(1.5)
            st.rerun()
        else:
            st.error("PINs must match and be at least 4 digits.")
    st.stop()

# --- 1. SESSION STATE ---
if 'notes' not in st.session_state:
    st.session_state.notes = vl.load_notes()
if 'edit_note_id' not in st.session_state:
    st.session_state.edit_note_id = None
if 'vault_unlocked' not in st.session_state:
    st.session_state.vault_unlocked = False
if 'master_pin' not in st.session_state:
    st.session_state.master_pin = "" # We store the actual PIN in session only while unlocked
if 'temp_content' not in st.session_state:
    st.session_state.temp_content = ""
if 'form_iteration' not in st.session_state:
    st.session_state.form_iteration = 0
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = time.time()
if 'show_lock_alert' not in st.session_state:
    st.session_state.show_lock_alert = False

# --- 2. AUTO-LOCK ENGINE ---
def update_activity():
    st.session_state.last_activity = time.time()
    st.session_state.show_lock_alert = False 

if st.session_state.vault_unlocked:
    elapsed_time = time.time() - st.session_state.last_activity
    if elapsed_time > AUTO_LOCK_SECONDS:
        st.session_state.vault_unlocked = False
        st.session_state.edit_note_id = None
        st.session_state.temp_content = "" 
        st.session_state.show_lock_alert = True 
        st.rerun() 

# --- 3. CSS & ALERTS ---
st.markdown("""
    <style>
        .block-container {padding-top: 2rem !important;}
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

if st.session_state.show_lock_alert:
    st.error("🚨 **THE VAULT IS AUTO LOCKED**")

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("➕ Add/Edit Note")
    
    c_title, c_content, c_secret = "", "", False
    if st.session_state.edit_note_id:
        n = next((x for x in st.session_state.notes if x['id'] == st.session_state.edit_note_id), None)
        if n: 
            c_title = n['title']
            c_content = vl.decrypt_data(n['content'], st.session_state.master_pin) if (n.get('secret') and st.session_state.vault_unlocked) else n['content']
            c_secret = n.get('secret', False)

    default_content = st.session_state.temp_content if st.session_state.temp_content else c_content

    with st.form(key=f"note_form_{st.session_state.form_iteration}", clear_on_submit=False):
        new_t = st.text_input("Title", value=c_title)
        new_c = st.text_area("Content", value=default_content, height=150)
        m_secret = st.checkbox("🤫 Mark as Secret", value=c_secret) if st.session_state.vault_unlocked else False
        
        if st.form_submit_button("✨ AI Summarize"):
            update_activity()
            if new_c:
                summary_result = vl.ai_summarize_text(new_c)
                st.session_state.temp_content = summary_result
                st.rerun() 
        
        if st.form_submit_button("Save", type="primary", use_container_width=True):
            update_activity()
            if new_t or new_c:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                final_content = vl.encrypt_data(new_c, st.session_state.master_pin) if m_secret else new_c
                if st.session_state.edit_note_id:
                    for n in st.session_state.notes:
                        if n['id'] == st.session_state.edit_note_id:
                            n.update({"title": new_t, "content": final_content, "timestamp": ts, "secret": m_secret})
                    st.session_state.edit_note_id = None
                else:
                    st.session_state.notes.insert(0, {"id": int(datetime.now().timestamp()), "title": new_t, "content": final_content, "timestamp": ts, "secret": m_secret})
                
                vl.save_notes(st.session_state.notes)
                st.session_state.temp_content = "" 
                st.session_state.form_iteration += 1 
                st.rerun()

    st.divider()
    st.write("### 🔐 Vault Security")
    if not st.session_state.vault_unlocked:
        pin_input = st.text_input("Enter Stealth PIN", type="password", key="pin_entry")
        if pin_input:
            if vl.verify_pin(pin_input):
                update_activity()
                st.session_state.vault_unlocked = True
                st.session_state.master_pin = pin_input
                st.rerun()
            else: st.error("Incorrect PIN")

        # NEW: Recovery Logic
        with st.expander("Forgot PIN?"):
            recovery_in = st.text_input("Enter Recovery Key")
            if st.button("Reset Vault PIN"):
                # Logic: If recovery key matches, delete config so they can start over
                # Note: Old encrypted notes stay encrypted (this is the cost of security!)
                if vl.verify_recovery_key(recovery_in): # You'll add this to vault_logic
                    os.remove("vault_config.json")
                    st.warning("Vault Identity Reset. Please refresh to set a new PIN.")
                    st.rerun()

    else:
        st.success("🔓 Vault is Open")
        time_left = int(AUTO_LOCK_SECONDS - (time.time() - st.session_state.last_activity))
        st.caption(f"Auto-locking in {max(0, time_left)}s")
        if st.button("🔒 Close Vault", use_container_width=True):
            st.session_state.vault_unlocked = False
            st.session_state.master_pin = ""
            st.rerun()

    st.divider()
    st.subheader("📊 AI Resources")
    if os.path.exists("usage_stats.json"):
        with open("usage_stats.json", "r") as f:
            stats = json.load(f)
        col1, col2 = st.columns(2)
        col1.metric("Tokens", f"{int(stats['total_tokens'])}")
        col2.metric("Cost", f"${stats['total_cost']:.5f}")
    else:
        st.info("No AI usage data yet.")

# --- 5. MAIN PAGE ---
st.title(vl.get_page_heading(st.session_state.vault_unlocked))

# --- 6. RAG CHAT INTERFACE ---
if st.session_state.vault_unlocked:
    with st.expander("💬 Ask Your Vault (AI Search)", expanded=False):
        user_query = st.text_input("Ask a question about your notes:", placeholder="e.g., What are my goals for 2026?")
        
        if user_query:
            update_activity()
            # 1. Prepare Decrypted Context
            decrypted_texts = []
            for n in st.session_state.notes:
                content = vl.decrypt_data(n['content'], st.session_state.master_pin) if n.get('secret') else n['content']
                decrypted_texts.append(content)
            
            # 2. RAG Logic
            index, text_data = vl.create_vector_index([{"content": t} for t in decrypted_texts])
            context_chunks = vl.query_vault(user_query, index, text_data)
            
            # 3. AI Answer
            context_str = "\n".join(context_chunks)
            prompt = f"Using ONLY these notes:\n{context_str}\n\nAnswer this question: {user_query}"
            
            with st.spinner("Searching Vault..."):
                answer = vl.get_gemini_response(user_query, context_str)
                st.info(f"**AI Answer:**\n{answer}")

                # 4. Feedback System ---
                st.write("---")
                st.write("Was this answer helpful?")
                f_col1, f_col2 = st.columns([1, 5])
                
                if f_col1.button("✅ Yes", key="fb_yes"):
                    vl.log_feedback(user_query, answer, context_str, "Correct")
                    st.success("Thanks for the feedback!")
                    
                if f_col2.button("❌ No / Wrong", key="fb_no"):
                    vl.log_feedback(user_query, answer, context_str, "Wrong")
                    st.warning("Logged as a failure.")

st.divider()
search = st.text_input("🔍 Search...", placeholder="Filter notes...")

# --- 7. Display Grid ---
cols = st.columns(3)
filtered = vl.get_filtered_notes(st.session_state.notes, st.session_state.vault_unlocked, search)

for idx, note in enumerate(filtered):
    with cols[idx % 3]: 
        with st.container(border=True):
            display_content = vl.decrypt_data(note['content'], st.session_state.master_pin) if (note.get('secret') and st.session_state.vault_unlocked) else note['content']
            
            st.subheader(f"🔒 {note['title']}" if note.get('secret') else note['title'])
            st.write(display_content[:200] + "..." if len(display_content) > 200 else display_content)
            st.caption(f"🕒 {note['timestamp']}")
            
            eb, db = st.columns(2)
            with eb:
                if st.button("✏️ Edit", key=f"e_{note['id']}"):
                    update_activity()
                    st.session_state.edit_note_id = note['id']
                    st.rerun()
            with db:
                if st.button("🗑️ Delete", key=f"d_{note['id']}"):
                    st.session_state.notes = [x for x in st.session_state.notes if x['id'] != note['id']]
                    vl.save_notes(st.session_state.notes)
                    st.rerun()

            st.divider()
            p_col, d_col = st.columns(2)
            with p_col:
                pdf_bytes = vl.create_pdf(note['title'], display_content)
    
                # Better error checking
                if isinstance(pdf_bytes, bytes):
                    # Check if it's a valid PDF (starts with %PDF) and not an error message
                    if pdf_bytes.startswith(b'%PDF'):
                        st.download_button(
                            "📄 Download PDF", 
                            data=pdf_bytes, 
                            file_name=f"{note['title']}.pdf", 
                            key=f"pdf_{note['id']}", 
                            use_container_width=True, 
                            mime="application/pdf"
                        )
                    elif pdf_bytes.startswith(b'PDF_ERROR'):
                        # Show the actual error message
                        error_text = pdf_bytes.decode('utf-8').replace('PDF_ERROR:', '').strip()
                        st.error(f"PDF failed: {error_text}")
                    else:
                        # Unknown bytes response
                        st.error("PDF generation failed - invalid format")
                else:
                    st.error("PDF generation failed - unexpected response")

        
            with d_col:
                docx_bytes = vl.create_docx(note['title'], display_content)
                st.download_button("📝 Download DOCX", data=docx_bytes, file_name=f"{note['title']}.docx", key=f"docx_{note['id']}", use_container_width=True)
