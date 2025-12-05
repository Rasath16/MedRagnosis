# Use Python 3.13 to match your project version
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# 1. Install system dependencies (OCR tools are required here)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the rest of the application code
COPY . .

# 4. Run the application
# Render provides the PORT env var, typically 10000
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "10000"]