FROM --platform=linux/amd64 ubuntu:24.04

# Download Python3 and pip.
RUN apt-get update -y && apt-get install -y \
    python3 \
    python3-pip

# Run as non-root user.
RUN groupadd -r user && useradd -m --no-log-init -r -g user user
USER user

# Set default working directory.
WORKDIR /home/user

# Copy over Python dependencies file and install.
COPY --chown=user:user requirements.txt .
RUN pip install \
    --user \
    --no-cache-dir \
    --break-system-packages \
    -r requirements.txt

# Copy over validation and scoring scripts.
COPY --chown=user:user utils.py .
COPY --chown=user:user validate.py .
COPY --chown=user:user score.py .
