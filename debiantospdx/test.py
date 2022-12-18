# 2022-11-21T03:49:09Z
# YYYY-MM-DDThh:mm:ssZ
import os
import pathlib
import shutil


def remove_glob(dirname, pathname):
    path_object = pathlib.Path(pathname)
    for p in path_object.glob("**"):
        if os.path.isdir(p) and dirname == os.path.basename(p):
            shutil.rmtree(p)


remove_glob("__pycache__", ".venv")
