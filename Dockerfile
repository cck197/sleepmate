FROM python:3.11

# Set working directory
WORKDIR /app

# Copy project files to container
COPY . .

RUN pip install -r requirements.txt

RUN cd whoop_client && python setup.py bdist_wheel
RUN pip install whoop_client/dist/whoop_client-1.0.0-py3-none-any.whl


EXPOSE 8080

# CMD ["gunicorn", "discourse.app:app", "--preload", "--timeout", "120", "--bind", "0.0.0.0:8080"]

# docker build -t sleepmate:latest .
# docker run sleepmate:latest gunicorn discourse.app:app --preload --timeout 120 --bind 0.0.0.0:8080