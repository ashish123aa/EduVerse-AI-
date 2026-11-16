# EduVerse AI (Groq version) - run on your laptop

## Quick start (Windows)
1. Install Python 3.10+ from python.org (tick "Add Python to PATH").
2. Get a key at console.groq.com (API Keys -> Create API Key).
3. Open `.env` in Notepad and paste the key after `GROQ_API_KEY=` (no spaces). Save.
4. Double-click `run.bat`. The browser opens at http://127.0.0.1:5000

## Mac / Linux
    chmod +x run.sh && ./run.sh

## Manual
    python -m venv venv
    venv\Scripts\activate        (Mac/Linux: source venv/bin/activate)
    pip install -r requirements.txt
    python app.py

## Models (change in .env if Groq renames or retires them)
- GROQ_MODEL         text model for chat, notes, quiz, planner, PDF
- GROQ_VISION_MODEL  model used by the Photo Solver (needs image support)
See the current list at console.groq.com/docs/models

## Notes
- Pro plan is a demo: Profile -> Upgrade to Pro -> Pay (Demo). No real payment.
- User data is saved in this browser (localStorage). Use the same browser each time.
- Groq has usage limits; if you see "rate limit", wait a minute and retry.
- Keep `.env` private. Stop the app with Ctrl+C in the terminal.
