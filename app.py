import streamlit as st
import json
import requests
import os
from datetime import datetime

# Load GitHub token and Gist ID from Streamlit secrets
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GIST_ID = os.environ.get("GIST_ID")
GIST_FILENAME = "notes.json"

# Headers for GitHub API
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Load notes from GitHub Gist
def load_notes():
    if not GITHUB_TOKEN or not GIST_ID:
        st.error("GitHub token or Gist ID not found.")
        return []
    url = f"https://api.github.com/gists/{GIST_ID}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        try:
            content = response.json()["files"][GIST_FILENAME]["content"]
            return json.loads(content)
        except Exception as e:
            st.error("Failed to parse notes from Gist.")
            return []
    else:
        st.error("Failed to load notes from GitHub Gist.")
        return []

# Save all notes to GitHub Gist
def save_all_notes(notes):
    if not GITHUB_TOKEN or not GIST_ID:
        st.error("GitHub token or Gist ID not set.")
        return
    url = f"https://api.github.com/gists/{GIST_ID}"
    data = {
        "files": {
            GIST_FILENAME: {
                "content": json.dumps(notes, indent=2)
            }
        }
    }
    response = requests.patch(url, headers=HEADERS, json=data)
    if response.status_code != 200:
        st.error("Failed to save notes to GitHub Gist.")

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
st.title("📝 Notes App with GitHub Gist Storage")

# Note title input
title = st.text_input("Note Title")

# Note text input
note_text = st.text_area("Write your note here:")

# Category dropdown
category = st.selectbox("Select a category", ["Personal", "Work", "Study", "Shopping", "Ideas", "Other"])

# Save note
if st.button("Save Note"):
    if title.strip() and note_text.strip():
        add_note(title.strip(), note_text.strip(), category)
        st.success("Note saved!")
    else:
        st.warning("Please fill in both the title and note.")

# Search notes
search_term = st.text_input("Search notes:")

# Load and filter notes
all_notes = load_notes()
filtered_notes = [
    n for n in all_notes
    if search_term.lower() in n["text"].lower()
    or search_term.lower() in n["category"].lower()
    or search_term.lower() in n.get("title", "").lower()
]

# Display notes
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
