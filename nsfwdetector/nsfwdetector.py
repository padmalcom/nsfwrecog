import logging
import os
import requests
from tqdm import tqdm
from ultralytics import YOLO
import cv2

logger = logging.getLogger(__name__)

MODEL_URL = "https://github.com/padmalcom/nsfwdectector/releases/download/nsfwdetector_v1/nsfwdetector_v1.onnx"
CLASSES_URL = "https://github.com/padmalcom/nsfwdectector/releases/download/nsfwdetector_v1/classes.txt"

class NsfwDetector:

    model = None
    classes = None

    def __download__(self, url, file_name, chunk_size=1024):
        resp = requests.get(
            url,
            stream=True
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
        for r in res:
            result = r.cpu()
            for bb in result.boxes:
                o = {}
                o['class'] = self.classes[int(bb.cls.item())]
                o['bbox'] = [
                    int(bb.xyxy[0][0].item()),
                    int(bb.xyxy[0][1].item()),
                    int(bb.xyxy[0][2].item()),
                    int(bb.xyxy[0][3].item())
                ]
                objects.append(o)
        return objects

    def __res_to_frame__(self, frame, res):
        for r in res:
            result = r.cpu()
            for bb in result.boxes:
                frame = cv2.rectangle(
                    frame,
                    (int(bb.xyxy[0][0].item()), int(bb.xyxy[0][1].item())),
                    (int(bb.xyxy[0][2].item()), int(bb.xyxy[0][3].item())),
                    (255, 0, 0),
                    2
                )
                frame = cv2.putText(
                    frame,
                    self.classes[int(bb.cls.item())],
                    (int(bb.xyxy[0][0].item()) + 5, int(bb.xyxy[0][1].item()) + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1,
                    (255, 0, 0),
                    2,
                    cv2.LINE_AA
                )
        return frame

    def camera(self, confidence=0.25):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise IOError("Cannot open webcam")

        while True:
            ret, frame = cap.read()
            #frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            res = self.model.predict(source=frame, conf=confidence)

            frame = self.__res_to_frame__(frame, res)

            cv2.imshow('Input', frame)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def video(self, video_input, video_output, confidence=0.25):
        cap = cv2.VideoCapture('test.mp4')
        if (cap.isOpened()== False): 
            print("Error opening video stream or file")

        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        out = cv2.VideoWriter(video_output, cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width,frame_height))
 
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:
                res = self.model.predict(source=frame, conf=confidence)
                frame = self.__res_to_frame__(frame, res)

                #cv2.imshow('Frame',frame)
                out.write(frame)
 
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            else: 
                break
 
        cap.release()
        out.release()
        cv2.destroyAllWindows()


    def blur(self, image_input, image_output):
        image = cv2.imread(image_input)
        res = self.detect(image_input)

        for r in res:
            top_x = r['bbox'][0]
            top_y = r['bbox'][1]
            bottom_x = r['bbox'][2]
            bottom_y = r['bbox'][3]

            region = image[top_y:bottom_y, top_x:bottom_x]
            blurred_region = cv2.GaussianBlur(region, (17, 17), 30)
            image[top_y:top_y+blurred_region.shape[0], top_x:top_x+blurred_region.shape[1]] = blurred_region

            #image = cv2.rectangle(image, (r['bbox'][0], r['bbox'][1]), (r['bbox'][2], r['bbox'][3]), (0, 0, 0), cv2.FILLED)

            cv2.imwrite(image_output, image)
