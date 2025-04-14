# Use an official Python runtime as a parent image
FROM python:3.11.8-slim

# Set environment variables to optimize Python execution
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for building Pillow (and possibly other libraries)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libz-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff-dev \
    libwebp-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Upgrade pip to the latest version for improved wheel resolution
RUN pip install --upgrade pip

# Install Python dependencies specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of your application code into the container
COPY . /app/

# Expose the port (if needed) - adjust based on your application
EXPOSE 8501

# Define the command to run your application
# Replace 'your_app.py' with the entry point of your Streamlit or other application
CMD ["streamlit", "run", "app.py"]
