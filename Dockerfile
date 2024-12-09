FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install av1an
RUN pip3 install av1an

# Set up working directory
WORKDIR /app

# Copy project files
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

# Create input and output directories
RUN mkdir -p input output

# Run the script
CMD ["python3", "src/main.py"]