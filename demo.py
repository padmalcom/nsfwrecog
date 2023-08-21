from nsfwdetector.nsfwdetector import NsfwDetector

if __name__ == '__main__':
    det = NsfwDetector()
    print(det.detect("test.png"))
    det.blur("test.png", "test_out.png")