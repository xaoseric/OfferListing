from fabric.api import *
import os


def test():
    os.envron["TEST"] = True
