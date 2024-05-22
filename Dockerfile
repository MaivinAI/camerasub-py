# Use the base image maivin/gstreamer:bullseye with the ARM64 architecture
FROM --platform=linux/arm64/v8 torizon/debian:3.2.1-bookworm

# Install libs to download the python3.10
RUN apt-get update && \
    apt-get install -y wget \
    gnupg-agent \
    libgomp1 \
    build-essential \
    zlib1g-dev \
    libssl-dev \
    libffi-dev \
    git

# Download the repository key
RUN wget https://deepviewml.com/apt/key.pub 
RUN apt-key add key.pub

# Create the repository configuration file
RUN echo "deb https://deepviewml.com/apt stable main" > /etc/apt/sources.list.d/deepviewml.list

# Update the package index and install required packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libg2d-viv \
    python3 \
    python3-pip \
    visionpack

# Set the working directory to /work
WORKDIR /app

# Copy the local directory contents into the Docker image at /work
COPY . .

# Install Python dependencies listed in requirements.txt using pip
RUN pip install --break-system-packages -r requirements.txt
ENV VAAL_LIBRARY=/usr/lib/aarch64-linux-gnu/libvaal.so
# Set the entry point for the Docker container to execute the Python script dmaSub.py
ENTRYPOINT [ "python3", "dmaSub.py" ]
