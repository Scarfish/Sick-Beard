import os, sys

def isAppFrozen():
    return hasattr(sys, "frozen")

def currentFileDirName():
    if isAppFrozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

def currentFileAbsPath():
    if isAppFrozen():
        return os.path.abspath(sys.executable)
    return os.path.abspath(__file__)
