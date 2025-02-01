# Use an official Python image
FROM python:3.11.10

# Set the working directory in the container
WORKDIR /app

# Copy the application's dependencies and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the application
CMD ["python", "app/app.py"]
