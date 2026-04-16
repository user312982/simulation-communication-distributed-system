FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements map
COPY requirements.txt .

# Install packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy all codes
COPY . .

# Expose Web Port
EXPOSE 8000

# Run Uvicorn Server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
