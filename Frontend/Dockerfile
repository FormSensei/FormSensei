# Use the official Python image as the base image
FROM python:3.9-slim

# Needed for psycopg2 postgresql adapter
RUN apt-get update && apt-get install -y git libpq-dev gcc

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY frontend_requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r frontend_requirements.txt

# Copy the entire application into the container
COPY . .

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
