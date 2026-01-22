FROM python:3.10-slim

# ---------- Install Node.js ----------
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
 && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
 && apt-get install -y nodejs \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# ---------- Verify ----------
RUN node -v && npm -v

# ---------- App Directory ----------
WORKDIR /app

# ---------- Install Python deps ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Copy App Files ----------
COPY . .

# ---------- Expose Port ----------
EXPOSE 8000

# ---------- Start ----------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
