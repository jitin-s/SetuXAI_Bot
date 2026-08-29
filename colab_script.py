# ==============================================================================
# SetuX AI Assistant - FREE Cloud Ollama Hosting (Google Colab / Kaggle GPU)
# Run this entire script in a Google Colab notebook cell (with T4 GPU enabled)
# ==============================================================================

"""
# Copy & Paste these commands into a Google Colab / Kaggle Notebook:

!curl -fsSL https://ollama.com/install.sh | sh
import subprocess, time
subprocess.Popen(["ollama", "serve"])
time.sleep(5)
subprocess.run(["ollama", "pull", "qwen2.5:1.5b"])
!npx localtunnel --port 11434
"""

import subprocess
import time
import os

def start_free_cloud_ollama():
    print("==================================================")
    print("   Starting FREE Cloud Ollama Server on Colab/GPU ")
    print("==================================================")
    
    # 1. Install Ollama
    print("\n[1/4] Installing Ollama...")
    subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True)
    
    # 2. Start Ollama in background
    print("\n[2/4] Starting Ollama service...")
    subprocess.Popen(["ollama", "serve"])
    time.sleep(4)
    
    # 3. Pull Qwen 1.5B Model
    print("\n[3/4] Pulling Local LLM Model (qwen2.5:1.5b)...")
    subprocess.run(["ollama", "pull", "qwen2.5:1.5b"])
    
    # 4. Create Free HTTPS Tunnel via Localtunnel / Ngrok
    print("\n[4/4] Creating FREE Public HTTPS URL Tunnel for Vercel...")
    print("Copy the HTTPS URL below and paste it into Vercel as OLLAMA_BASE_URL:\n")
    subprocess.run("npx localtunnel --port 11434", shell=True)

if __name__ == "__main__":
    start_free_cloud_ollama()
