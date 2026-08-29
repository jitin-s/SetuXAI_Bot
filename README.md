# SetuX AI Assistant - Citizen Document Helpdesk & Self-Learning Engine

An AI-powered Citizen Assistance Helpdesk & Self-Learning Engine designed for **SetuX Document Portal**. Powered by local open-weight LLMs via **Ollama** (`qwen2.5:1.5b` / `qwen2.5-coder:latest`), featuring live website scanning, multilingual translation (7 Indian languages), dynamic script execution, and an embeddable website widget.

---

## 🌟 Key Features

- **100% Local & Privacy-Preserving**: Runs completely offline using **Ollama** on CPU/GPU without external cloud API dependencies.
- **Live Website Scanner & Self-Learning**: Crawls any website URL or ingests live host DOM content to learn new service details, FAQs, and price plans dynamically into `learned_memory.json`.
- **Embeddable Website Widget (`setux-widget.js`)**: Integrate onto ANY host website with a single line:
  ```html
  <script src="http://localhost:5173/setux-widget.js"></script>
  ```
- **Multilingual Support**: Supports 7 Indian languages with native script generation (**English**, **Hindi**, **Marathi**, **Bengali**, **Tamil**, **Telugu**, **Gujarati**).
- **Processing Modes**: Highlights `✅ 100% Online Process` vs `⚠️ Offline Visit Required (Biometrics / Verification Slot)`.
- **Accessibility Toolbar**: Text resizing (**A-**, **A**, **A+**), High Contrast mode, Dark Blue theme, and Screen Reader Text-to-Speech (**Listen Audio 🔊**).

---

## 🛠️ Project Structure

```
NationNet_aiBOT/
├── webpage/                      # React Frontend Application (Vite + Tailwind/CSS)
│   ├── public/setux-widget.js   # Universal Embeddable Widget Script
│   ├── src/App.jsx               # SetuX AI Webpage Component
│   └── package.json
│
├── setux_bot/                    # Core AI Engine & Knowledge System
│   ├── engine.py                 # RAG Retriever, Response Sanitizer & Learning Manager
│   ├── scanner.py                # Web Crawler & HTML Parser (BeautifulSoup4)
│   ├── ollama_client.py          # Real-time HTTP Streaming Client for Ollama
│   ├── knowledge_base.json       # Core Document Workflows, Proofs & Fees
│   ├── learned_memory.json       # Persisted Scanned Website Snippets & Facts
│   └── guardrails.py             # Domain Scope Filter
│
├── server.py                     # FastAPI Backend REST & SSE Server (Port 8000)
├── setux_cli.py                  # Interactive Terminal CLI Application
├── requirements.txt              # Backend Python Dependencies
├── setup.bat                     # One-Click Setup Script for Windows
└── run_all.bat                   # One-Click Launch Script
```

---

## 🚀 Quick Start Guide

### Prerequisites
1. **Python 3.10+** installed.
2. **Node.js 18+** installed.
3. **Ollama** installed from [ollama.com](https://ollama.com).

### Step 1: Install & Pull Local Model
Start Ollama and pull the local model:
```bash
ollama serve
ollama pull qwen2.5:1.5b
```

### Step 2: Install Dependencies
- **Backend Dependencies**:
  ```bash
  pip install -r requirements.txt
  ```
- **Frontend Dependencies**:
  ```bash
  cd webpage
  npm install
  cd ..
  ```

### Step 3: Start the Application
- **FastAPI Server** (Port 8000):
  ```bash
  python server.py
  ```
- **React Frontend Webpage** (Port 5173):
  ```bash
  cd webpage
  npm run dev
  ```
- **Or use One-Click Windows Launcher**:
  Double click `run_all.bat`!

---

## 📤 How to Upload to GitHub

Follow these steps to push your project to GitHub:

### 1. Initialize Git in Project Directory
Open your terminal in `d:\NationNet_aiBOT` and run:
```bash
git init
git add .
git commit -m "Initial commit of SetuX AI Assistant with Local LLM & Self-Learning Engine"
```

### 2. Create a Repository on GitHub
1. Go to [github.com/new](https://github.com/new).
2. Name your repository (e.g. `SetuX-AI-Bot`).
3. Select **Public** or **Private**.
4. **Do NOT** check "Initialize with a README" (you already have one).
5. Click **Create repository**.

### 3. Connect and Push Code
Copy the commands shown on GitHub and run them in your terminal:
```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/SetuX-AI-Bot.git
git push -u origin main
```

---

## 📄 License
Created for SetuX Document Portal.
