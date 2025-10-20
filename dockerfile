# 1️⃣ Chọn base image
FROM python:3.11-slim

# 2️⃣ Tạo thư mục làm việc
WORKDIR /app

# 3️⃣ Cài dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4️⃣ Copy mã nguồn
COPY . .

# 5️⃣ Expose port FastAPI
EXPOSE 8000

# 6️⃣ Lệnh chạy app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
