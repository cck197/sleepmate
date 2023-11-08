FROM python:3.11

# Set working directory
WORKDIR /app

# Copy project files to container
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080

# CMD ["gunicorn", "discourse.app:app", "--preload", "--timeout", "120", "--bind", "0.0.0.0:8080"]

# docker build -t sleepmate:latest .
# docker run sleepmate:latest gunicorn discourse.app:app --preload --timeout 120 --bind 0.0.0.0:8080