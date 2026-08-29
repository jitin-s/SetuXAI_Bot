# ==============================================================================
# 24/7 FREE Hugging Face Spaces Ollama Dockerfile
# Deploy on https://huggingface.co/new-space (Docker SDK)
# ==============================================================================

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV OLLAMA_HOST=0.0.0.0:7860

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    zstd \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Pre-download Qwen 1.5B Model into the container image
RUN ollama serve & \
    sleep 5 && \
    ollama pull qwen2.5:1.5b

EXPOSE 7860

# Start Ollama listening on port 7860 (Hugging Face default)
CMD ["ollama", "serve"]
