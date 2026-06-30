FROM python:3.12.10-slim

WORKDIR /app

# Create non-root user early so we can chown copied files
RUN adduser --disabled-password --no-create-home appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source with correct ownership so appuser can read it
COPY --chown=appuser:appuser src/ .

USER appuser

EXPOSE 8000