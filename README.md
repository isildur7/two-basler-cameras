# two-basler-cameras
Code to capture video from two basler cameras simultaneously in python.

## Requirements
First, install [Basler Pylon Software Suite](https://www.baslerweb.com/en/products/software/basler-pylon-camera-software-suite/). After, install the libraries in libraries in `requirements.txt`. You can use the command:
```
pip install -r requirements.txt
```

## Using the Code
To test everything is okay, run the file `two_basler_video.py`. You can import the file to use the functions in your code. For example:

```
from two_basler_video import video_from_two_cameras

FPS = 20
RECORDING_TIME = 10  # in seconds
FILE1 = "./samplevid1.avi"  # extension can be changed
FILE2 = "./samplevid2.avi"  # extension can be changed
CAMPIXFMT = "Mono8"  # can change to anything available on the camera
VIDPIXFMT = "gray"  # since camera is in Mono mode
CAMEXPTIME = 40000
WRITER = "imageio"  # use either "imageio" or "FFMPEG"

# shoot video
videos_from_two_cameras(FILE1, FILE2, RECORDING_TIME, CAMPIXFMT, 
                        CAMEXPTIME, FPS, VIDPIXFMT, WRITER)
```
## Video Writers
The code gives you a choice to use one of two video writers `'imageio'` or `'FFMPEG'`. If you are using `'FFMPEG'`, make sure that path to ffmpeg library on line 75 in `FFMPEGwriter.py` is correct.

When in doubt, use `'imageio'`.


