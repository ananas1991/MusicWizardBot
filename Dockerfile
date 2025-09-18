# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the cache, which reduces the image size.
# --trusted-host pypi.python.org: Helps with potential network issues in some environments.
RUN apt-get update && apt-get install -y ffmpeg && \
    pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . .

# Command to run the application
CMD ["python", "bot.py"]
