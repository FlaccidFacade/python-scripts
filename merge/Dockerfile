# Dockerfile for merge.py script
FROM python:3.12-slim

# Install git
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the merge script first (it has no dependencies beyond stdlib)
COPY merge.py .

# Make the script executable
RUN chmod +x merge.py

# Set git global config (needed for git operations)
RUN git config --global user.email "docker@example.com" && \
    git config --global user.name "Docker User"

# Install pytest for testing (optional - only if testing in Docker)
# Copy test requirements and files only if needed
COPY requirements.txt .
COPY tests/ tests/

# Install dependencies with SSL cert verification disabled (for sandboxed environments)
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt || \
    echo "Warning: Could not install test dependencies. Script can still run without tests."

# Default command shows help
CMD ["python3", "merge.py", "--help"]
