from nsfwdetection.nsfwdetection import NsfwDetection

if __name__ == '__main__':
    det = NsfwDetection()
    det.video("test.mp4", "test_out.mp4")