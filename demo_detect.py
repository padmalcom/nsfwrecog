from nsfwrecog.nsfwrecog import NsfwRecog

if __name__ == '__main__':
    det = NsfwRecog()
    print(det.detect("test.png"))
    det.blur("test.png", "test_out.png")