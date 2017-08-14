import os

def install_requirements():
    try:
        os.system("sudo -H pip install -r requirements.txt") #only for linux
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print "pip not found! please install it first..."
        else:
            raise