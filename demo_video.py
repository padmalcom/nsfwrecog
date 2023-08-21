from nsfwdetector.nsfwdetector import NsfwDetector

if __name__ == '__main__':
    det = NsfwDetector()
    det.video("test.mp4", "test_out.mp4")