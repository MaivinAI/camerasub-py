import atexit
import io  
import sys  
import time  
from argparse import ArgumentParser  
import av  
from PIL import Image, ImageDraw  
from edgefirst.schemas.edgefirst_msgs import Detect as Boxes # Import ImageAnnotation schema from edgefirst package
import zenoh  # Zenoh library for distributed systems
import threading

# Define the encoding prefix for zenoh
ENCODING_PREFIX = str(zenoh.Encoding.APP_OCTET_STREAM())
exit_flag = False

# Initialize variables
mcap_image = None  # To store the current image frame
frame_position = 0  # Current position in the video stream
rawData = io.BytesIO()  # Stream to store raw video data
container = av.open(rawData, format="h264", mode='r')  # Open the AV container to parse H.264 video format
exit_event = threading.Event()  # Event to signal exit

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
    global frame_position, mcap_image, rawData, container
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
                img = Image.fromarray(frame_array)  # Create PIL image
                img.save("output.jpg", format="JPEG", quality=100)  # Save image to file
                mcap_image = img  # Store image frame
        except Exception as e:  # Handle exceptions
            print(f"Error processing packet: {e}")
            continue  # Continue processing next packets

# Callback function to handle detection messages
def detect_message_callback(msg):
    global mcap_image
    img = mcap_image # Get the stored image frame
    if img is None:
        return

    try:
        payload = bytes(msg.value.payload)
        boxes = Boxes.deserialize(payload) # Deserialize the detection message to get bounding boxes
    except Exception as e:
        print(f"Error deserializing detection message: {e}")
        return
    
    # Iterate over annotation points
    for points_annotation in boxes.boxes:
        points = points_annotation  # Get bounding box points
        
        # Check if points are available
        if points:
            draw = ImageDraw.Draw(img)  # Create draw object
            frame_height = 1080
            frame_width = 1920
            scale = 1
            
            x = int((points.center_x - points.width / 2) * frame_width/scale)
            y = int((points.center_y - points.height / 2) * frame_height/scale)
            w = int(points.width * frame_width/scale)
            h = int(points.height * frame_height/scale)
            
            draw.rectangle([(x, y), (x + w, y + h)], outline=(255, 0, 0), width=2) # Draw bounding box on image
    
    # Save image with bounding boxes
    img.save("output_with_boxes.jpg", format="JPEG", quality=100)
    global exit_flag
    if not exit_flag:
        print("Trying to exit might take a few seconds....")
        exit_flag = True
    exit_event.set()  # Signal the main thread to exit

# Main function
def main():
    args = parse_args()  # Parse command line arguments
    cfg = zenoh.Config()  # Create zenoh configuration object
    cfg.insert_json5(zenoh.config.CONNECT_KEY, '["%s"]' % args.connect)  # Set connection point
    session = zenoh.open(cfg)  # Open zenoh session

    # Ensure the session is closed when the script exits
    def _on_exit():
        print("Output image with boxes saved.")
        session.close()
    atexit.register(_on_exit)  # Register exit handler

    camera_sub = session.declare_subscriber("rt/camera/h264", message_callback)  # Subscriber for camera frames
    detect_sub = session.declare_subscriber("rt/detect/boxes2d", detect_message_callback)  # Subscriber for detection messages
    
    exit_event.wait(args.time)  # Wait for either the exit event or the timeout

# Entry point of the script
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # Handle keyboard interrupt
        sys.exit(0)  # Exit the program
