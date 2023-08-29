from .core import ThumbTest

def test(*args, **kwargs):
    thumb = ThumbTest()
    return thumb.test(*args, **kwargs)

def load(file_path):
    filename = file_path.split('/')[-1]
    tid = filename.replace(".csv", "").replace("thumb_test_", "")
    
    return ThumbTest(tid)