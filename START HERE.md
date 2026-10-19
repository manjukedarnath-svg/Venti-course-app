# Moving VentCourse to Claude Code / Cowork / Desktop

Same app, same files, new place to work on it. Nothing is rebuilt.

## Step 1: put the folder on GitHub (once)
GitHub's website rejects big uploads, so use **GitHub Desktop** (free):
1. Install GitHub Desktop and sign in.
2. **File → Clone repository** → `manjukedarnath-svg/Venti-course-app` → choose a folder.
3. Delete everything in that cloned folder **except** the hidden `.git` folder.
4. Copy everything from this `ventcourse` folder into it.
5. In GitHub Desktop: write "Move to source files", then click **Commit to main** → **Push origin**.
6. Railway redeploys by itself in about a minute. Open the site and check it.

From now on this folder is the app. Edits made here go live when you push.

## Step 2: pick where you work

### Claude Code (building and fixing)
In the folder, open Terminal and run `claude`. First message:
```
Read CLAUDE.md and README.md. This is my live VentCourse app. We are continuing it, not rebuilding.
Run npm start and confirm it works. Then wait for my first change.
```
Then ask for changes in plain words, e.g. "Add a lesson to Module 03 after lesson 4 with this text…".
Finish each change with: "Check it at phone width, commit, and push."

### Claude Cowork (content and files)
Start a task, give it access to the same folder. First message:
```
This folder is my live VentCourse app. Read CLAUDE.md first and follow its rules.
Only edit what I ask. Tell me which files you changed.
```
Good for adding X-rays or sounds to `assets/`, editing lesson text, and writing documents.

### Claude Desktop: Project (thinking and planning)
New project **VentCourse**. Upload `CLAUDE.md`, `README.md`, `index.html` and `vent-graphics.js` as knowledge.
Custom instructions:
```
You help me run VentCourse, my paediatric ventilation course app. The knowledge files are the live app.
Help me plan lessons, check clinical accuracy and draft text. Keep answers short and non-technical.
When I want a change built, give me a clear instruction I can paste into Claude Code.
```

## Keep private
Admin: `admin` / `VentAdmin@2026` (change it via Railway → Variables → `ADMIN_PASSWORD`).
