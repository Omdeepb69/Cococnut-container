# Build Stage
FROM python:3.9-slim as builder

LABEL maintainer="Omdeep Borkar <omdeepborkar@gmail.com>"

WORKDIR /app

COPY requirements.txt .

# Install dependencies into a virtual environment or directly to user local to copy later
# For simplicity in this robust setup, we install to /install
RUN pip install --no-cache-dir --default-timeout=1000 --prefix=/install -r requirements.txt

# Runtime Stage
FROM python:3.9-slim as runtime

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

COPY . .

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
