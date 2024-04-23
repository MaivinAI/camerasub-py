# DMA Buffer to JPEG Converter

This script demonstrates how to subscribe to DMA topic and process received messages containing image data and storing to JPEG. More documentation can be found [here](https://support.deepviewml.com/hc/en-us/articles/26118202550925-DMA-Buffer-to-JPEG-From-Python)

## Prerequisites

Before running the script, ensure you have the following dependencies installed:

- Python 3.8
```bash
pip install -r requirements.txt
``` 

## Usage

Run the script `dmaSub.py` with the following command-line arguments:

```
python dmaSub.py [-h] [-c CONNECT] [-t TIME] [topic]
```

- `-h, --help`: Show the help message and exit.
- `-c CONNECT, --connect CONNECT`: Connection point for the Zenoh session. Default is 'tcp/127.0.0.1:7447'.
- `-t TIME, --time TIME`: Time to run the subscriber before exiting. Default is 5 seconds.
- `topic`: The topic to which to subscribe. Default is 'rt/camera/dma'.

# License

This project is licensed under the AGPL-3.0 or under the terms of the DeepView AI Middleware Commercial License.

# Support

Commercial Support is provided by Au-Zone Technologies through the [DeepView Support](https://support.deepviewml.com) site.


