import logging
import os
import requests
from tqdm import tqdm
from ultralytics import YOLO
import cv2

logger = logging.getLogger(__name__)

MODEL_URL = "https://github.com/padmalcom/nsfwrecog/releases/download/nsfwrecog_v1/nsfwrecog_v1.onnx"
CLASSES_URL = "https://github.com/padmalcom/nsfwrecog/releases/download/nsfwrecog_v1/classes.txt"

class NsfwRecog:

    model = None
    classes = None

    def __download__(self, url, file_name, chunk_size=1024):
        resp = requests.get(
            url,
            stream=True
        )
        
        if resp.status_code != 200:
            raise Exception("Unexpected status code {code}.".format(code = resp.status_code))
            
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

    def __not_found__(self, file_path):
        try:
            with open(file_path, 'r') as f:
               lines = f.readlines()
               if len(lines) == 1:
                   if lines[0] == "Not Found":
                       return True
        except UnicodeDecodeError:
            return False
        return False                 

    def __init__(self, model_file=None):
        if model_file is None:
            # create a path to store the models
            home = os.path.expanduser("~")
            model_folder = os.path.join(home, f".NsfwRecog/")
            if not os.path.exists(model_folder):
                os.makedirs(model_folder)

            # prepare filenames
            model_name = os.path.basename(MODEL_URL)
            model_path = os.path.join(model_folder, model_name)
            classes_path = os.path.join(model_folder, "classes.txt")
            print("Model path", model_path)
            
            if not os.path.exists(model_path) or os.path.getsize(model_path) == 0:
                logger.info("Downloading the checkpoint to %s", model_path)
                self.__download__(MODEL_URL, model_path)

            if not os.path.exists(classes_path) or os.path.getsize(classes_path) == 0:
                logger.info("Downloading the classes list to %s", classes_path)
                self.__download__(CLASSES_URL, classes_path)
        else:
            model_path = model_file
            classes_path = os.path.join(os.path.dirname(model_file), "classes.txt")
            if not os.path.exists(model_path):
                raise Exception("Model path {mp} does not exist.".format(mp=model_path))
            if not os.path.exists(classes_path):
                raise Exception("Classes path {cp} does not exist.".format(cp=classes_path))

        if os.path.getsize(model_path) == 0:
            raise Exception("Model file size is 0.")

        if os.path.getsize(classes_path) == 0:
            raise Exception("Classes file size is 0.")        

        if self.__not_found__(model_path):
           raise Exception("Model file not downloaded correctly.")
           
        if self.__not_found__(classes_path):
           raise Exception("Classes file not downloaded correctly.")
        
        self.model = YOLO(model_path, task="detect")
        self.classes = [c.strip() for c in open(classes_path).readlines() if c.strip()]

    def detect(self, image, confidence=0.25):
        res = self.model.predict(task="detect", source=image, conf=confidence, verbose=False)
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
                    (int(bb.xyxy[0][0].item()) + 1, int(bb.xyxy[0][1].item()) + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1,
                    (255, 0, 0),
                    2,
                    cv2.LINE_AA
                )
        return frame

    def camera(self, cam_id=0, confidence=0.25):
        cap = cv2.VideoCapture(cam_id)
        if not cap.isOpened():
            raise IOError("Cannot open webcam")

        while True:
            ret, frame = cap.read()
            res = self.model.predict(source=frame, conf=confidence, verbose=False)

            frame = self.__res_to_frame__(frame, res)

            cv2.imshow('Input', frame)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def video(self, video_input, video_output, confidence=0.25):
        cap = cv2.VideoCapture('test.mp4')
        if (cap.isOpened()== False): 
            raise IOError("Cannot open video stream or file")

        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        out = cv2.VideoWriter(video_output, cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width,frame_height))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        for i in tqdm(range(frame_count)):
            ret, frame = cap.read()
            if ret == True:
                res = self.model.predict(source=frame, conf=confidence, verbose=False)
                frame = self.__res_to_frame__(frame, res)
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
        cv2.imwrite(image_output, image)
