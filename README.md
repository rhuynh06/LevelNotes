# LevelNotes

LevelNotes is a full-stack, Notion-inspired note-taking app that **gamifies writing**. Users can create rich text pages, add editable blocks (text and to-do), and **level up** as they write more—offering gentle encouragement and a sense of progress. It's a productivity tool designed to make note-taking feel rewarding..

## Features

- Rich-text editing with live syncing
- TODO blocks with checkbox functionality
- Dark/light mode toggle (Solo Leveling Themed)
- Gamified user levels based on word count
- Auth (register/login/logout with sessions)
- Deployed full stack (e.g., Render, Vercel)

---

## Tech Stack

- **Frontend**: React + TypeScript + CSS
- **Backend**: Node.js + Express + Prisma + SQLite
- **Database**: Prisma ORM
- **Auth**: Cookie-based sessions
- **Hosting**: Compatible with Render/Vercel

---

## Run Locally (Recommended for Best Performance)

```bash
# Clone the repo
git clone https://github.com/rhuynh06/LevelNotes.git
cd LevelNotes

# Backend setup
cd backend
pip install flask flask-cors flask-sqlalchemy python-dotenv sqlalchemy werkzeug
python app.py  # Runs at http://localhost:5050

# Frontend setup (in a new terminal)
cd ../frontend
npm install
npm run dev  # Runs at http://localhost:5173
