# DMA Buffer to JPEG Converter

This project demonstrates how to subscribe to DMA, H264 and Detect topic and process received messages containing image and boxes data and storing to JPEG. More documentation can be found [here](https://support.deepviewml.com/hc/en-us/articles/26118202550925-DMA-Buffer-to-JPEG-From-Python)

Refer to [Maivin EdgeFirst Schemas](https://github.com/MaivinAI/schemas) for an overview of the services and their schemas used by this example project.

## Prerequisites

Before running the script, ensure you have the following dependencies installed:

- Python 3.8
```bash
pip install -r requirements.txt
``` 

## Usage

Run the script `dmaSub.py` with the following command-line arguments:

```
sudo -E python dmaSub.py [-h] [-c CONNECT] [-t TIME] [topic]
```

- `-h, --help`: Show the help message and exit.
- `-c CONNECT, --connect CONNECT`: Connection point for the Zenoh session. Default is 'tcp/127.0.0.1:7447'.
- `-t TIME, --time TIME`: Time to run the subscriber before exiting. Default is 5 seconds.
- `topic`: The topic to which to subscribe. Default is 'rt/camera/dma'.

There is also a dockerfile which goes over how to use the sample using a docker container, the container is self contained and should include all the dependencies inside the container it self. However as the sample requires access to the board resources it need to run as follow:
```
docker run -it --privileged --pid=host --network=host --entrypoint bash <NAME_OF_CONTAINER>
```

The container need to be built and hosted by the user and can be done using:
```
docker build . -f Dockerfile --platform linux/arm64/v8 --tag <NAME_OF_CONTAINER>
```

Run the script `zenoh_to_jpeg.py` with the following command-line arguments:

```
python zenoh_to_jpeg.py [-h] [-c CONNECT] [-t TIME]
```

- `-h, --help`: Show the help message and exit.
- `-c CONNECT, --connect CONNECT`: Connection point for the Zenoh session. Default is 'tcp/127.0.0.1:7447'.
- `-t TIME, --time TIME`: Time to run the subscriber before exiting. Default is 5 seconds.


# License

This project is licensed under the AGPL-3.0 or under the terms of the DeepView AI Middleware Commercial License.

# Support

Commercial Support is provided by Au-Zone Technologies through the [DeepView Support](https://support.deepviewml.com) site.


