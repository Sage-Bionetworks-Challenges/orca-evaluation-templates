FROM --platform=linux/amd64 ubuntu:24.04

# Download Python3 and uv.
RUN apt-get update -y && apt-get install -y python3
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Run as non-root user.
RUN groupadd -r user && useradd -m --no-log-init -r -g user user
USER user

# Set default working directory.
WORKDIR /home/user

# Create virtual environment and add it to PATH.
ENV VIRTUAL_ENV=/home/user/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy over Python dependencies file and install.
COPY --chown=user:user requirements.txt .
RUN uv venv $VIRTUAL_ENV && \
    uv pip install --no-cache -r requirements.txt

# Copy over validation and scoring scripts.
COPY --chown=user:user utils.py .
COPY --chown=user:user validate.py .
COPY --chown=user:user score.py .
