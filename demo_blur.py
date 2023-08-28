from nsfwdetection.nsfwdetection import NsfwDetection

if __name__ == '__main__':
    det = NsfwDetection()
    print(det.detect("test.png"))
    det.blur("test.png", "test_out.png")