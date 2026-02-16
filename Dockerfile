# Build stage not needed for this app; use slim runtime image.
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY start.py .

# Cloud Run sets PORT (default 8080).
ENV PORT=8080
EXPOSE 8080

CMD ["python", "start.py"]
