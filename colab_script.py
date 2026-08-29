# ==============================================================================
# SetuX AI Assistant - FREE Cloud Ollama Hosting (Google Colab / Kaggle GPU)
# Run this entire script in a Google Colab notebook cell (with T4 GPU enabled)
# ==============================================================================

"""
# Copy & Paste these exact commands into a Google Colab Notebook Cell:

!apt-get update && apt-get install -y zstd
!curl -fsSL https://ollama.com/install.sh | sh
import subprocess, time
subprocess.Popen(["ollama", "serve"])
time.sleep(5)
!ollama pull qwen2.5:1.5b
!npx localtunnel --port 11434
"""

import subprocess
import time

def start_free_cloud_ollama():
    print("==================================================")
    print("   Starting FREE Cloud Ollama Server on Colab/GPU ")
    print("==================================================")
    
    # 1. Install zstd dependency first
    print("\n[1/5] Installing zstd extraction dependency...")
    subprocess.run("apt-get update && apt-get install -y zstd", shell=True)
    
    # 2. Install Ollama
    print("\n[2/5] Installing Ollama...")
    subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True)
    
    # 3. Start Ollama in background
    print("\n[3/5] Starting Ollama service...")
    subprocess.Popen(["ollama", "serve"])
    time.sleep(5)
    
    # 4. Pull Qwen 1.5B Model
    print("\n[4/5] Pulling Local LLM Model (qwen2.5:1.5b)...")
    subprocess.run("ollama pull qwen2.5:1.5b", shell=True)
    
    # 5. Create Free HTTPS Tunnel via Localtunnel
    print("\n[5/5] Creating FREE Public HTTPS URL Tunnel for Vercel...")
    print("Copy the HTTPS URL below and paste it into Vercel as OLLAMA_BASE_URL:\n")
    subprocess.run("npx localtunnel --port 11434", shell=True)

if __name__ == "__main__":
    start_free_cloud_ollama()
