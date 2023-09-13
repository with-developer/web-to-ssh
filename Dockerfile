# Base image
FROM python:3.10.13

# Copy requirements and install dependencies
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

# Copy application code
COPY . /app/

# Set environment variables
ENV FLASK_APP app.py
ENV FLASK_DEBUG 1
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 5000

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
