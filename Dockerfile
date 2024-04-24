# Use the base image maivin/gstreamer:bullseye with the ARM64 architecture
FROM --platform=linux/arm64/v8 maivin/gstreamer:bullseye AS builderz

# Update the package index and install required packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    pip \
    visionpack 

# Copy the local directory contents into the Docker image at /work
COPY . .

# Set the working directory to /work
WORKDIR /work

# Install Python dependencies listed in requirements.txt using pip
RUN pip install -r requirements.txt

# Set the entry point for the Docker container to execute the Python script dmaSub.py
ENTRYPOINT [ "python3", "dmaSub.py" ]
