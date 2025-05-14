import streamlit as st
import json
import requests
from datetime import datetime

# Load secrets
GITHUB_TOKEN = st.secrets["github"]["token"]
GIST_ID = st.secrets["github"]["gist_id"]
FILENAME = st.secrets["github"]["filename"]

# Headers for GitHub API
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Load notes from GitHub Gist
def load_notes():
    url = f"https://api.github.com/gists/{GIST_ID}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        files = res.json().get("files", {})
        if FILENAME in files:
            content = files[FILENAME].get("content", "[]")
            return json.loads(content)
    return []

# Save all notes to GitHub Gist
def save_all_notes(notes):
    url = f"https://api.github.com/gists/{GIST_ID}"
    payload = {
        "files": {
            FILENAME: {
                "content": json.dumps(notes, indent=2)
            }
        }
    }
    res = requests.patch(url, headers=HEADERS, data=json.dumps(payload))
    if res.status_code not in [200, 201]:
        st.error("Failed to save notes to GitHub Gist")

# Add a new note
def add_note(title, text, category):
    notes = load_notes()
    new_note = {
        "title": title,
        "text": text,
        "category": category,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    notes.append(new_note)
    save_all_notes(notes)

# Delete a note by index
def delete_note(index):
    notes = load_notes()
    if 0 <= index < len(notes):
        notes.pop(index)
        save_all_notes(notes)

# ---- Streamlit UI ----
st.title("📝 Notes App with Titles, Categories, Search & Delete")

title = st.text_input("Note Title")
note_text = st.text_area("Write your note here:")
category = st.selectbox("Select a category", ["Personal", "Work", "Study", "Shopping", "Ideas", "Other"])

if st.button("Save Note"):
    if title.strip() and note_text.strip():
        add_note(title.strip(), note_text.strip(), category)
        st.success("Note saved!")
    else:
        st.warning("Please fill in both the title and note.")

search_term = st.text_input("Search notes:")

all_notes = load_notes()
filtered_notes = [
    n for n in all_notes
    if search_term.lower() in n["text"].lower()
    or search_term.lower() in n["category"].lower()
    or search_term.lower() in n.get("title", "").lower()
]

st.subheader("📋 Your Notes")

if filtered_notes:
    for i, note in enumerate(reversed(filtered_notes)):
        index = len(all_notes) - 1 - i
        st.markdown(f"""
        ### 📌 {note.get('title', 'Untitled')}
        **Note:** {note['text']}  
        🏷 **Category:** `{note.get('category', 'none')}`  
        ⏰ **Saved on:** {note.get('timestamp', 'Unknown')}
        """)
        if st.button(f"Delete Note {index + 1}", key=f"delete_{index}"):
            delete_note(index)
            st.rerun()
else:
    st.info("No notes to show.")
