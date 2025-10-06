# Dockerfile for launcher.py script
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the launcher script first (it has no dependencies beyond stdlib)
COPY launcher.py .

# Make the script executable
RUN chmod +x launcher.py

# Copy example configuration
COPY groups.json .

# Install pytest for testing (optional - only if testing in Docker)
# Copy test requirements and files only if needed
COPY requirements.txt .
COPY tests/ tests/

# Install dependencies with SSL cert verification disabled (for sandboxed environments)
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt || \
    echo "Warning: Could not install test dependencies. Script can still run without tests."

# Default command shows help
CMD ["python3", "launcher.py", "--help"]
