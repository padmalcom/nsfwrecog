from nsfwrecog.nsfwrecog import NsfwRecog

if __name__ == '__main__':
    det = NsfwRecog()
    det.video("test.mp4", "test_out.mp4")