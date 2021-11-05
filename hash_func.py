import hashlib
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(10*1024*1024), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

