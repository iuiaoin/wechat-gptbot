import subprocess
import sys


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def install_file(file):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", file])
