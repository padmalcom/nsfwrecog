# NSFW detector
This library is meant to detect and censor nsfw content in public media. Models can be found
[here](https://github.com/padmalcom/nsfwdectector/releases/tag/nsfwdetector_v1), they are downloaded automatically and cached.

![](test.png)
![](test_out.png)

## Installation
- install requirements.txt
- install pytorch according to your cuda version
- install onnxruntime or onnxruntime-gpu

## Usage
See demo.py. Instantiate a NsfwDetector class and use the methods detect() and blur().