import logging
import os
import requests
from tqdm import tqdm
from ultralytics import YOLO

logger = logging.getLogger(__name__)

MODEL_URL = "https://github.com/padmalcom/nsfwdectector/releases/download/nsfwdetector_v1/nsfwdetector_v1.onnx"
CLASSES_URL = "https://github.com/padmalcom/nsfwdectector/releases/download/nsfwdetector_v1/classes.txt"

class NsfwDetector:

    model = None
    classes = None

    def __download__(self, url, file_name, chunk_size=1024):
        resp = requests.get(
            url,
            stream=True,
            headers={
                'accept': 'application/vnd.github.v3.raw',
                'authorization': 'token {}'.format("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")
            }
        )
        total = int(resp.headers.get('content-length', 0))
        with open(file_name, 'wb') as file, tqdm(
            desc=file_name,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in resp.iter_content(chunk_size=chunk_size):
                size = file.write(data)
                bar.update(size)    

    def __init__(self):
        # create a path to store the models
        home = os.path.expanduser("~")
        model_folder = os.path.join(home, f".NsfwDetector/")
        if not os.path.exists(model_folder):
            os.makedirs(model_folder)

        # prepare filenames
        model_name = os.path.basename(MODEL_URL)
        model_path = os.path.join(model_folder, model_name)
        classes_path = os.path.join(model_folder, "classes.txt")
        
        if not os.path.exists(model_path):
            logger.info("Downloading the checkpoint to %s", model_path)
            self.__download__(MODEL_URL, model_path)

        if not os.path.exists(classes_path):
            logger.info("Downloading the classes list to %s", classes_path)
            self.__download__(CLASSES_URL, classes_path)

        self.model = YOLO(model_path)
        self.classes = [c.strip() for c in open(classes_path).readlines() if c.strip()]

    def detect(self, image, confidence=0.25):
        res = self.model.predict(task="detect", source=image, conf=confidence)
        objects = []
        box_count = 0
        for r in res:
            result = r.cpu()
            for bb in result.boxes:
                o = {}
                o['class'] = self.classes[int(bb.cls.item())]
                o['bbox'] = [
                    bb.xyxy[0][0].item(),
                    bb.xyxy[0][1].item(),
                    bb.xyxy[0][2].item(),
                    bb.xyxy[0][3].item()
                ]
                objects.append(o)
        return objects
