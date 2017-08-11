import os

def install_requirements():
    try:
        os.system("pip install -r requirements.txt")
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print "pip not found! please install it first..."
        else:
            raise