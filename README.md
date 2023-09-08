# NSFW Recog
This library is meant to detect and censor nsfw content in public media. Models can be found
[here](https://github.com/padmalcom/nsfwrecog/releases/tag/nsfwrecog_v1), they are downloaded automatically and cached in ~/.NsfwRecog.

![sample image](https://raw.githubusercontent.com/padmalcom/nsfwrecog/main/graphics/sample.png)

## Installation
NSFW Recog can either be used as stand-alone software or as module to be embedded in your python application.

### Stand-alone
- install requirements.txt
- install pytorch according to your cuda version
- (optional) install onnxruntime-gpu to support cuda usage
- Run one of the scripts listed in *Usage*

### As module
- pip install nsfw-recog
- Include the module as shown exemplarily in the demos listed in *Usage*

## Usage
Instantiate a NsfwDetector class and use the methods detect(), blur(), video() and camera(). The demos show the usage:
- [demo_detect.py](https://github.com/padmalcom/nsfwrecog/blob/main/demo_detect.py): Detecting body parts/objects in an image
- [demo_camera.py](https://github.com/padmalcom/nsfwrecog/blob/main/demo_camera.py): Live detecting objects in a webcam stream
- [demo_video.py](https://github.com/padmalcom/nsfwrecog/blob/main/demo_video.py): Detecting objects in a video and draw bounding boxes and labels to a new video
- [demo_blur.py](https://github.com/padmalcom/nsfwrecog/blob/main/demo_blur.py): Detecting objects in an image and blurring them.

## Models
I provide a basic model [here](https://github.com/padmalcom/nsfwrecog/releases/tag/nsfwrecog_v1). Please contact me if a better model with a higher accuracy is required.
