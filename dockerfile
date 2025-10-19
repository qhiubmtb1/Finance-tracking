# 1. Base image
FROM python:3.11-slim

# 2. Set working file in container
WORKDIR /app

# 3. Copy file requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy src to container
COPY . .

# 5. Expose port
EXPOSE 8000

# 6. run FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
