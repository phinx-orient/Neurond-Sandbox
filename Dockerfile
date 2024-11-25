FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt ./
# Install Docker client
RUN apt-get update && apt-get install -y docker.io
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Start of Selection
# Command to run the application
CMD ["python", "main.py"]

# Add this line to run as root
USER root  
