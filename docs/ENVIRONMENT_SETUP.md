# Environment Setup Guide — MacBook Air M1 (Apple Silicon)

> This guide is specifically written for Apple Silicon (ARM64) Macs. All tools and packages are compatible with M1/M2/M3 chips.

---

## Step 1: Verify System

Open Terminal (Cmd+Space → "Terminal") and run:

```bash
# Check macOS version (should be 12.0+)
sw_vers

# Check processor architecture (should show arm64)
uname -m

# Expected output: arm64
```

---

## Step 2: Install Homebrew (ARM64 version)

Homebrew is the package manager for macOS. Install the ARM64 version:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, add Homebrew to your PATH (follow the instructions it prints, typically):
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Verify:
```bash
brew --version
# Expected: Homebrew 4.x.x
which brew
# Expected: /opt/homebrew/bin/brew (NOT /usr/local — that's Intel)
```

---

## Step 3: Install pyenv (Python Version Manager)

```bash
brew install pyenv

# Add to ~/.zshrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# Reload shell
source ~/.zshrc

# Install Python 3.11.9
pyenv install 3.11.9
pyenv global 3.11.9

# Verify
python --version
# Expected: Python 3.11.9
```

---

## Step 4: Install Node.js via nvm

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# Reload shell
source ~/.zshrc

# Install Node.js 20 LTS
nvm install 20
nvm use 20
nvm alias default 20

# Verify
node --version    # Expected: v20.x.x
npm --version     # Expected: 10.x.x
```

---

## Step 5: Install PostgreSQL 16

```bash
brew install postgresql@16

# Start PostgreSQL service
brew services start postgresql@16

# Add to PATH
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify
psql --version
# Expected: psql (PostgreSQL) 16.x

# Connect to PostgreSQL
psql postgres

# Create database and user (run inside psql):
CREATE USER smartattend WITH PASSWORD 'password';
CREATE DATABASE smartattend_db OWNER smartattend;
GRANT ALL PRIVILEGES ON DATABASE smartattend_db TO smartattend;
\q
```

---

## Step 6: Install Git and configure

```bash
# Git comes with Xcode CLI tools, install if needed:
xcode-select --install

git --version
# Expected: git version 2.x.x

git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git config --global init.defaultBranch main
```

---

## Step 7: Install VS Code

Download from: https://code.visualstudio.com/download (choose Apple Silicon)

Install recommended extensions:
```bash
code --install-extension ms-python.python
code --install-extension ms-python.pylance
code --install-extension bradlc.vscode-tailwindcss
code --install-extension esbenp.prettier-vscode
code --install-extension ms-azuretools.vscode-docker
code --install-extension eamodio.gitlens
code --install-extension usernamehw.errorlens
code --install-extension formulahendry.auto-rename-tag
code --install-extension christian-kohler.path-intellisense
code --install-extension PKief.material-icon-theme
```

---

## Step 8: Install Docker Desktop

Download Docker Desktop for Apple Silicon from: https://docs.docker.com/desktop/install/mac-install/

Verify:
```bash
docker --version
docker-compose --version
```

---

## Step 9: Install Database GUI

**Option A: TablePlus (recommended)**
Download from: https://tableplus.com

**Option B: pgAdmin 4**
```bash
brew install --cask pgadmin4
```

---

## Step 10: Setup Project Virtual Environment

```bash
cd /path/to/smartattend/backend

# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate

# Your prompt should now show (.venv) prefix

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

---

## Verification Checklist

Run all these commands and verify expected output:

```bash
sw_vers -productVersion    # 12.0 or higher
uname -m                   # arm64
brew --version             # 4.x.x from /opt/homebrew
python --version           # 3.11.9
node --version             # v20.x.x
npm --version              # 10.x.x
git --version              # 2.x.x
psql --version             # 16.x
docker --version           # 25.x or higher
```

All green? You're ready to start development! ✅

---

## Common Issues

| Issue | Fix |
|-------|-----|
| `brew: command not found` | Run the Homebrew install command again; check PATH |
| `python: command not found` | Reload shell: `source ~/.zshrc` |
| `psql: command not found` | Add PostgreSQL to PATH (Step 5) |
| `permission denied` for psql | Run `brew services restart postgresql@16` |
| M1 package incompatibility | Ensure you used ARM64 Homebrew from `/opt/homebrew` |
| Port 5432 in use | `lsof -i :5432` then kill the process |
