import os
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict


def is_dependencies_satisfied():
    with open("requirements.txt",'r') as f:
        dependencies = f.readlines()
    f.close()
    try:
        pkg_resources.require(dependencies)
        return True
    except (DistributionNotFound,VersionConflict): #not satisfied
        return False

def install_requirements():
    try:
        if not is_dependencies_satisfied():
            os.system("sudo -H pip install -r requirements.txt") #only for linux
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print "pip not found! please install it first..."
        else:
            raise

if __name__ == '__main__':
    if not is_dependencies_satisfied():
        install_requirements()