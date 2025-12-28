# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the Streamlit port
EXPOSE 8501

# Define environment variable for Ollama connection
# By default, inside Docker, 'localhost' refers to the container.
# We need to point to the host machine's Ollama.
ENV OLLAMA_HOST=http://host.docker.internal:11434

# Run the application
CMD ["streamlit", "run", "src/app.py", "--server.address=0.0.0.0"]
