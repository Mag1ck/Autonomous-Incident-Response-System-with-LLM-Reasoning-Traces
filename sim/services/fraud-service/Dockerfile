FROM python:3.11-slim
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

# Copy in the source code
COPY main.py .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]