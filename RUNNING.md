# How to Run Token Golf - Super Easy Guide

## Choose Your Method

### 🐍 Method 1: Local Python (Easiest)

```bash
cd /Users/keklund/projects/token-golf

# Run the script - it handles everything!
./run.sh
```

That's it! The script will:
- ✅ Create virtual environment (if needed)
- ✅ Install dependencies
- ✅ Setup .env file (you'll need to add your API key)
- ✅ Run database migrations
- ✅ Build Tailwind CSS
- ✅ Start the server

**Then open:** http://localhost:8000

---

### 🐳 Method 2: Podman/Docker (Containerized)

```bash
cd /Users/keklund/projects/token-golf

# Run the script - it handles everything!
./run-podman.sh
```

The script will:
- ✅ Check for .env file
- ✅ Check for podman-compose
- ✅ Start containers

**Then open:** http://localhost:8000

---

## Manual Steps (If Scripts Don't Work)

### Local Python (Manual)

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env
# Edit .env and add your Claude API key

# 4. Run migrations
alembic upgrade head

# 5. Start server
uvicorn app.main:app --reload --port 8000
```

### Podman (Manual)

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env and add your Claude API key

# 2. Start containers
podman-compose up
```

---

## ⚠️ IMPORTANT: Fix Before Testing

The "Generate My Username" button won't work yet.

**Quick 1-Minute Fix:**

```bash
# Open the file
nano app/templates/index.html

# Find line ~97 (search for: generate_new_user)
# CHANGE: hx-vals='{"generate_new_user": true}'
# TO:     hx-vals='{"action": "generate", "course_id": "beginner-course"}'

# Save and refresh browser
```

Or see `ISSUES.md` for detailed instructions.

---

## What You'll See

After starting, visit these URLs:

- **Home**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (interactive!)
- **Leaderboard**: http://localhost:8000/leaderboard
- **Health**: http://localhost:8000/health

---

## Troubleshooting

### "Port 8000 already in use"

```bash
# Find what's using it
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### "Claude API key not found"

```bash
# Check your .env file
cat .env | grep CLAUDE_API_KEY

# Should see:
# CLAUDE_API_KEY=sk-ant-...

# If not, edit .env and add your key
```

### "Database locked"

```bash
# Stop all processes, then
rm token_golf.db
alembic upgrade head
```

### "ModuleNotFoundError"

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Stop the Server

**Local Python:**
- Press `Ctrl+C` in terminal

**Podman:**
```bash
podman-compose down
```

---

## Quick Commands Reference

```bash
# Start (auto setup)
./run.sh                    # Local Python
./run-podman.sh            # Podman

# Start (manual)
uvicorn app.main:app --reload --port 8000    # Local
podman-compose up                             # Podman

# Stop
Ctrl+C                      # Local
podman-compose down        # Podman

# View logs
# (local: already in terminal)
podman-compose logs -f     # Podman

# Reset database
rm token_golf.db && alembic upgrade head

# Rebuild CSS
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css
```

---

## Ready to Play?

1. ✅ Run the app (script handles setup)
2. ✅ Fix the button issue (1 minute)
3. ✅ Open http://localhost:8000
4. ✅ Generate username or sign in
5. ✅ Play challenges!

**Have fun! ⛳**
