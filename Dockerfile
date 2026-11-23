# ---------------------------------------------------------------
# Dockerfile for the Multimodal RAG app (version 1: the basics)
# ---------------------------------------------------------------

# 1. Start from a small, official Python image
FROM python:3.12-slim

# 2. Settings inside the container
#    PYTHONUNBUFFERED: show print/log output immediately
#    GRADIO_SERVER_NAME=0.0.0.0: accept connections from outside the
#    container (Gradio's default, 127.0.0.1, only listens inside it)
ENV PYTHONUNBUFFERED=1 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860

# 3. Do all the work inside the /app folder
WORKDIR /app

# 4. Install packages FIRST, before copying the code.
#    Docker caches each step, so if only your code changes,
#    this slow step is skipped on the next build.
#
#    4a. Install the CPU-only build of PyTorch first. The default build
#        also installs ~20 NVIDIA GPU (CUDA) libraries worth many GB,
#        which this app never uses. Because torch is then already
#        installed, step 4b keeps it and skips the GPU version.
RUN pip install --no-cache-dir torch==2.15.0 --index-url  \
https://download.pytorch.org/whl/cpu

# 4. Install packages FIRST, before copying the code.
#    Docker caches each step, so if only your code changes,
#    this slow step is skipped on the next build.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the code (.dockerignore decides what's left out)
COPY . .

# 6. Note which port the app uses
EXPOSE 7860

# 7. The command that runs when the container starts
CMD ["python", "app.py"]