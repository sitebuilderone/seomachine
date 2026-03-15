# Setting Up a New Client Project

This guide walks you through cloning SEO Machine for a new client and connecting it to the master repo for future updates.

---

## Overview

SEO Machine is designed for **multi-client use**. The master repo contains the "engine" (commands, agents, scripts), while each client gets an independent repo that can pull engine improvements back from master without touching client-specific content (brand voice, drafts, research, etc.).

**Key concept**: Each client repo has two git remotes:
- `origin` — the client's own repository (client-specific content)
- `upstream` — the master SEO Machine repo (engine updates)

---

## Step 1: Create the Client Repository from the Template

### On GitHub

1. Go to the master SEO Machine repo: https://github.com/sitebuilderone/seomachine
2. Click the green **"Use this template"** button
3. Select **"Create a new repository"**
4. Fill in:
   - **Repository name**: `seomachine-clientname` (e.g., `seomachine-acmecorp`)
   - **Description**: "SEO Machine for [Client Name]"
   - **Visibility**: Select **"Private"** (clients shouldn't see other clients' work)
5. Click **"Create repository from template"**

GitHub will create a fresh copy of SEO Machine with no shared git history.

---

## Step 2: Clone and Set Up Remotes Locally

### Clone the new client repo

```bash
git clone https://github.com/you/seomachine-clientname.git
cd seomachine-clientname
```

### Add the master repo as "upstream"

This allows you to pull engine improvements later.

```bash
# Add the master repo as the upstream remote
git remote add upstream https://github.com/sitebuilderone/seomachine.git

# Verify both remotes are set up
git remote -v
```

You should see:
```
origin     https://github.com/you/seomachine-clientname.git (fetch)
origin     https://github.com/you/seomachine-clientname.git (push)
upstream   https://github.com/sitebuilderone/seomachine.git (fetch)
upstream   https://github.com/sitebuilderone/seomachine.git (push)
```

---

## Step 3: Install Python Dependencies

SEO Machine includes Python modules for analytics, SEO analysis, and WordPress integration. You have two options:

### Option A: Virtual Environment (Recommended)

A virtual environment isolates dependencies per project, preventing conflicts if you're managing multiple clients.

#### On Mac/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r data_sources/requirements.txt
```

#### On Windows:
```bash
python3 -m venv .venv
.venv\Scripts\activate
pip install -r data_sources/requirements.txt
```

**To exit the virtual environment later**: `deactivate`

**To re-enter it**: `source .venv/bin/activate` (Mac/Linux) or `.venv\Scripts\activate` (Windows)

### Option B: Quick Install (Mac/Linux only)

If you just want to get running without a virtual environment:

```bash
pip3 install -r data_sources/requirements.txt
```

> **Note for Mac users**: `pip` is not available by default on macOS. Always use `pip3` or the venv approach above. If you see `command not found: pip`, use `pip3` instead.

---

## Step 4: Configure Context Files for the Client

The fastest way to configure SEO Machine for your client is the **onboarding questionnaire**. Fill it in once, run a script, and all context files are auto-generated.

### Fill in the questionnaire

```bash
# Open the questionnaire in your editor
# On Mac/Linux:
open context/_onboarding-questionnaire.md

# On Windows:
start context/_onboarding-questionnaire.md

# Or open it in your editor of choice
code context/_onboarding-questionnaire.md
```

The questionnaire has 9 sections:
1. **Business Overview** — Client name, URL, description, target audience, goals
2. **Products & Features** — What they offer, key benefits, use cases
3. **Brand Voice** — Tone, personality, messaging pillars
4. **Style Guide** — Grammar rules, formatting standards, terminology
5. **Target Keywords** — Keyword clusters, search intent, priority topics
6. **Internal Links** — Key pages for internal linking strategy
7. **Competitors** — Who they compete with, differentiation angles
8. **SEO Guidelines** — Content length, structure, technical rules
9. **Writing Examples** — Links to their best published blog posts

**Fill in every section** with the client's specific information. Replace all `[ANSWER]` placeholders.

> **Tip**: You can fill in section 9 (Writing Examples) later once the client publishes content. For now, you can leave it with `[To be completed]`.

### Run the populate script

Once the questionnaire is complete:

```bash
python3 context/populate-context.py
```

This creates/updates all 8 context files automatically:
- `context/brand-voice.md`
- `context/features.md`
- `context/style-guide.md`
- `context/seo-guidelines.md`
- `context/target-keywords.md`
- `context/internal-links-map.md`
- `context/competitor-analysis.md`
- `context/writing-examples.md`

### Commit your work

```bash
git add context/
git commit -m "Configure context for [Client Name]"
git push origin main
```

---

## Step 5: Open in Claude Code

```bash
claude-code .
```

This opens SEO Machine in Claude Code, where you can:
- Use all custom commands: `/research`, `/write`, `/rewrite`, `/optimize`, etc.
- Access specialized agents for SEO analysis, meta creation, internal linking, etc.
- Integrate with Google Analytics, Search Console, and DataForSEO

---

## Step 6: Configure API Credentials (Optional but Recommended)

To use advanced analytics and research features, you'll need to set up API credentials.

### Google Analytics 4 & Search Console

1. Create a Google Cloud service account: https://console.cloud.google.com
2. Download the credentials JSON file
3. Save it as `credentials/ga4-credentials.json`

### DataForSEO

1. Sign up at https://dataforseo.com
2. Get your API key from your account settings
3. Add to `data_sources/config/.env`:
   ```
   DATAFORSEO_LOGIN=your-email@example.com
   DATAFORSEO_PASSWORD=your-api-key
   ```

### WordPress Integration

To publish articles directly to the client's WordPress site:

1. Get a WordPress Application Password (WordPress Admin → Users → Your Profile → Application Passwords)
2. Add to `data_sources/config/.env`:
   ```
   WORDPRESS_URL=https://clientsite.com
   WORDPRESS_USERNAME=your-username
   WORDPRESS_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
   ```

See `data_sources/README.md` for detailed setup instructions.

---

## Step 7: Pull Updates from Master

When improvements are made to the master SEO Machine repo (new commands, improved agents, bug fixes), you can sync them into the client project **without touching client-specific content**.

### Fetch updates from master

```bash
git fetch upstream
```

### Pull only engine files

```bash
# Pull the command and agent files
git checkout upstream/main -- .claude/

# Pull the analysis modules
git checkout upstream/main -- data_sources/

# Pull the questionnaire and populate script
git checkout upstream/main -- context/_onboarding-questionnaire.md
git checkout upstream/main -- context/populate-context.py

# Pull updated documentation
git checkout upstream/main -- README.md

# Pull WordPress integration files
git checkout upstream/main -- wordpress/
```

### Review and commit

```bash
# See what changed
git diff --staged

# Commit the update
git commit -m "Sync engine updates from master"

# Push to the client's repo
git push origin main
```

> **Important**: Never run `git merge upstream/main` — this would try to merge client-specific context files with master's templates, causing conflicts. Always use `git checkout upstream/main -- <path>` to pull specific files only.

---

## Step 8: Set Up `.gitignore` (Optional)

If you want to keep generated content (drafts, research reports) out of the repo:

```bash
# Create or edit .gitignore
echo "
# Client content — commit intentionally, not by default
drafts/
research/
rewrites/
audits/
landing-pages/
published/

# Credentials — never commit
data_sources/config/.env
credentials/
data_sources/cache/
.venv/
" >> .gitignore

git add .gitignore
git commit -m "Add .gitignore for client content"
git push origin main
```

This keeps generated content out of git, but if you want to version control drafts and published articles, you can remove these lines from `.gitignore`.

---

## You're Ready!

At this point, the client project is fully set up and ready to use:

1. ✅ Client repo created and connected to master
2. ✅ Python dependencies installed
3. ✅ Context files configured with client information
4. ✅ Claude Code opened and ready to use
5. ✅ API credentials (optionally) configured

### Next steps:

- Run `/research [topic]` to research a topic
- Run `/write [topic]` to create an SEO-optimized article
- Run `/analyze-existing [URL]` to audit existing content
- Check the main README.md for all available commands and workflows

---

## Troubleshooting

### "command not found: pip"

**Problem**: On Mac, `pip` is not available by default.

**Solution**: Use `pip3` instead, or set up a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r data_sources/requirements.txt
```

### "fatal: 'upstream' does not appear to be a git repository"

**Problem**: The upstream remote hasn't been added yet.

**Solution**: Run this in the client repo:
```bash
git remote add upstream https://github.com/sitebuilderone/seomachine.git
git remote -v  # Verify both remotes are set
```

### "Could not find populate-context.py"

**Problem**: The file might be named differently or in a different location.

**Solution**: Check the context directory:
```bash
ls context/
# Should show: populate-context.py, _onboarding-questionnaire.md, brand-voice.md, etc.
```

### Merge conflicts when pulling from upstream

**Problem**: If you edited engine files (like `.claude/commands/`) in the client repo, pulling from upstream might cause conflicts.

**Solution**: Engine files should only be edited in the master repo. If you've customized commands for this client:
1. Keep your customizations in the client repo
2. Document them separately (e.g., in a `CUSTOMIZATIONS.md` file)
3. When pulling updates, manually merge the changes with your customizations

---

## Getting Help

- **SEO Machine README**: Check `/README.md` for full documentation
- **Command Reference**: See `/README.md` → "Commands Reference"
- **Claude Code Docs**: https://docs.claude.com/claude-code
- **Issue Tracking**: Report bugs or feature requests on the master repo: https://github.com/sitebuilderone/seomachine/issues
