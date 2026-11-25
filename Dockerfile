# ---------------------------------------------------------------
# Dockerfile for the Multimodal RAG app
# (version 3: non-root user + model built in, ready for Hugging Face)
# ---------------------------------------------------------------

# 1. Start from a small, official Python image
FROM python:3.12-slim

# 2. Create a normal (non-root) user with ID 1000 and switch to it.
#    - Safer: if the app is ever hacked, the attacker isn't root.
#    - Required by Hugging Face Spaces, which runs containers as user 1000.
RUN useradd -m -u 1000 user
USER user

# 3. Settings inside the container
#    HOME / PATH: the user's home folder, and where pip puts its programs
#    PYTHONUNBUFFERED: show print/log output immediately
#    GRADIO_SERVER_NAME=0.0.0.0: accept connections from outside the container
#    HF_HOME: where the embedding model is saved (inside the user's home)
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860 \
    HF_HOME=/home/user/.cache/huggingface

# 4. Do all the work inside /home/user/app
WORKDIR $HOME/app

# 5. Install packages (before copying code, so this slow step is cached)
#    5a. CPU-only PyTorch: skips ~20 unused NVIDIA GPU libraries
RUN pip install --no-cache-dir torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu

#    5b. The app's packages
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Download the embedding model NOW, at build time, so it is saved
#    inside the image. Containers then start fast and don't need to
#    download it every time.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 7. From now on, never try to download models: use the saved copy
ENV HF_HUB_OFFLINE=1

# 8. Copy the code, owned by our user (.dockerignore decides what's left out)
COPY --chown=user . .

# 9. Create the data folder as our user, so the app can write to it
#    (and so a new volume attached here is owned by our user too)
RUN mkdir -p data

# 10. Note which port the app uses
EXPOSE 7860

# 11. The command that runs when the container starts
CMD ["python", "app.py"]