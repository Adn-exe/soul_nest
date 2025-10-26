# 🌿 Soul Nest

**Soul Nest** is a minimalist web app built to give people a quiet digital space to express their thoughts, emotions, and reflections.  
It’s a safe corner of the internet where users can write freely, comment gently, and connect through shared feelings — no noise, no judgment.

---

## ✨ Features
- 🪶 **Thought Sharing** – Post your inner reflections and moods.
- 💬 **Comments** – Leave kind notes or responses on others’ thoughts.
- 🌙 **Mood Selector** – Express emotions visually with mood tags.
- 🌈 **Clean, Calm UI** – Focused layout for mindful journaling.
- 🧭 **User-Centric Feed** – See everyone’s thoughts arranged neatly.

---

## 🧠 Tech Stack
| Area | Technology |
|------|-------------|
| **Frontend** | HTML / CSS / JavaScript (Bootstrap for styling) |
| **Backend** | Flask (Python) |
| **Database** | SQLAlchemy + SQLite |
| **Templating** | Jinja2 |
| **Version Control** | Git / GitHub |
| **Deployment** | Render (Backend) & Vercel (Optional Frontend Hosting) |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/soul-nest.git
cd soul-nest


### 2️⃣ Activate virtual environment (Windows)
```bash
venv\Scripts\activate

#    or (macOS/Linux)
source venv/bin/activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Set environment variables (for Flask)
# Windows PowerShell
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"

# macOS/Linux
export FLASK_APP=app.py
export FLASK_ENV=development

# 5️⃣ Initialize the database (if using SQLAlchemy)
python
>>> from app import db
>>> db.create_all()
>>> exit()

# 6️⃣ Run the development server
flask run
