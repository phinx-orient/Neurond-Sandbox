# Use the official Python base image
FROM python:3.10.15-bullseye

# Set the working directory
WORKDIR /app

# Install the required Python libraries
RUN pip install --no-cache-dir \
    pandas==1.5.3 \
    openpyxl==3.0.10 \
    xlrd==2.0.1 \
    sqlalchemy==1.4.47 \
    numpy==1.23.5 \
    plotly==5.10.0 \
    seaborn==0.12.1

# Copy the rest of the application code
COPY . .

# Command to run the application (modify as needed)
CMD ["python3"]