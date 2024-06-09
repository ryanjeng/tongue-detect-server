# Use the official Python 3.12 image from the Docker Hub
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR 1

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean

# Install pipenv
RUN pip install --upgrade pip && pip install pipenv

# Create a working directory
WORKDIR /app

# Copy Pipfile and Pipfile.lock to the working directory
COPY Pipfile Pipfile.lock /app/

# Install dependencies using pipenv
RUN pipenv install --system --deploy

# Copy the rest of the application code to the working directory
COPY . /app

# Expose the port FastAPI will run on
EXPOSE 8000

# Set the entry point to run app.py
CMD ["fastapi", "run", "app.py", "--port", "8000"]