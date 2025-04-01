# Story Email with WordNet Vocabulary

This project automatically sends daily emails containing an English story, its Turkish translation, a dynamically generated vocabulary list with English definitions and Turkish translations, and an audio narration of the story in English.

## Features
- Fetches an English story from a text file (`alican.txt`).
- Translates the story into Turkish using `googletrans`.
- Generates an audio narration of the English story using `gTTS` (Google Text-to-Speech).
- Extracts key vocabulary words from the story using NLP (`nltk`) and provides English definitions via `WordNet`.
- Sends a daily email at 08:00 (IST) with the story, translation, vocabulary list, and audio file using Gmail SMTP.
- Formats the email in HTML with Helvetica font for a clean look.

## Requirements
- Python 3.x
- Required libraries:
  ```plaintext
  gtts
  googletrans==3.1.0a0
  python-dotenv
  schedule
  nltk
