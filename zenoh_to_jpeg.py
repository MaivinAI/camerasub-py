import atexit
import io  
import sys  
import time  
from argparse import ArgumentParser  
import av  
from PIL import Image, ImageDraw  

from edgefirst.schemas.foxglove_msgs import ImageAnnotations as Boxes # Import ImageAnnotation schema from edgefirst package
import zenoh  # Zenoh library for distributed systems

# Define the encoding prefix for zenoh
ENCODING_PREFIX = str(zenoh.Encoding.APP_OCTET_STREAM())

# Initialize variables
mcap_image = None  # To store the current image frame
frame_position = 0  # Current position in the video stream
rawData = io.BytesIO()  # Stream to store raw video data
container = av.open(rawData, format="h264", mode='r')  # Open the AV container to parse H.264 video format

# Define function to parse command line arguments
def parse_args():
    parser = ArgumentParser(description="Topics Example")
    parser.add_argument('-c', '--connect', type=str, default='tcp/127.0.0.1:7447',
                        help="Connection point for the zenoh session, default='tcp/127.0.0.1:7447'")
    parser.add_argument('-t', '--time', type=float, default=5,
                        help="Time to run the subscriber before exiting.")
    return parser.parse_args()

# Callback function to handle incoming video frame messages
def message_callback(msg):
    global frame_position, mcap_image
    received_message = bytes(msg.value.payload) # Store received message
    rawData.write(received_message)
    rawData.seek(frame_position) # Move the buffer position to the specified frame position
    
    # Iterate over packets in the video container
    for packet in container.demux():
        try:
            if packet.size == 0:  # Skip empty packets
                continue
            frame_position += packet.size  # Update frame position
            for frame in packet.decode():  # Decode video frames
                frame_array = frame.to_ndarray(format='rgb24')  # Convert frame to numpy array
                height, width, _ = frame_array.shape  # Get frame dimensions
                img = Image.frombytes('RGB', (width, height), frame_array.tobytes())  # Create PIL image
                img.save("output.jpg", format="JPEG", quality=100)  # Save image to file
                mcap_image = img  # Store image frame
                detect_message_callback()  # Process detection messages
        except Exception as e:  # Handle exceptions
            continue  # Continue processing next packets

# Callback function to handle detection messages
def detect_message_callback(msg):
    global mcap_image
    img = mcap_image # Get the stored image frame
    boxes = Boxes.deserialize(bytes(msg.value.payload)) # Deserialize the detection message to get bounding boxes
    
    # Iterate over annotation points
    for points_annotation in boxes.points:
        points = points_annotation.points  # Get bounding box points
        
        # Check if points and image are available
        if points and img is not None:
            draw = ImageDraw.Draw(img)  # Create draw object
            box_points = [(int(point.x), int(point.y)) for point in points]  # Convert points to integers
            
            # Calculate bounding box coordinates
            min_x = min(point[0] for point in box_points)
            min_y = min(point[1] for point in box_points)
            max_x = max(point[0] for point in box_points)
            max_y = max(point[1] for point in box_points)
            
            draw.rectangle([(min_x, min_y), (max_x, max_y)], outline=(255, 0, 0), width=2) # Draw bounding box on image
    
    # Save image with bounding boxes
    if img is not None:
        img.save("output_with_boxes.jpg", format="JPEG", quality=100)
        exit()  # Exit the program

# Main function
def main():
    args = parse_args()  # Parse command line arguments
    cfg = zenoh.Config()  # Create zenoh configuration object
    cfg.insert_json5(zenoh.config.CONNECT_KEY, '["%s"]' % args.connect)  # Set connection point
    session = zenoh.open(cfg)  # Open zenoh session

    # Ensure the session is closed when the script exits
    def _on_exit():
        session.close()
    atexit.register(_on_exit)  # Register exit handler

    camera_sub = session.declare_subscriber("rt/camera/h264", message_callback)  # Subscriber for camera frames
    detect_sub = session.declare_subscriber("rt/detect/boxes2d", detect_message_callback)  # Subscriber for detection messages
    
    time.sleep(args.time) # Block the main thread to keep the program running 

# Entry point of the script
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # Handle keyboard interrupt
        sys.exit(0)  # Exit the program
