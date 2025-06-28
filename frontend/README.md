# 📒 LevelNotes

LevelNotes is a full-stack, Notion-inspired note-taking app with gamified leveling. Users can create pages, add editable text and todo blocks, and level up based on how much they write.

## ✨ Features

- 📝 Rich-text editing with live syncing
- ✅ TODO blocks with checkbox functionality
- 🌑 Dark/light mode toggle
- 🎮 Gamified user levels based on word count
- 🔐 Auth (register/login/logout with sessions)
- 🚀 Deployed full stack (e.g., Render, Vercel)

---

## 🏗️ Tech Stack

- **Frontend**: React + TypeScript + CSS
- **Backend**: Node.js + Express + Prisma + SQLite/PostgreSQL
- **Database**: Prisma ORM
- **Auth**: Cookie-based sessions
- **Hosting**: Compatible with Render/Vercel

---

## Run Locally (Recommended for Best Performance)

```bash
# Clone the repo
git clone https://github.com/rhuynh06/notes-app.git
cd notes-app

# Backend setup
cd backend
pip install flask flask-cors flask-sqlalchemy python-dotenv sqlalchemy werkzeug
python app.py  # Runs at http://localhost:5050

# Frontend setup (in a new terminal)
cd ../frontend
npm install
npm run dev  # Runs at http://localhost:5173