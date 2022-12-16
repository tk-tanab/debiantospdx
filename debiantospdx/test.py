# 2022-11-21T03:49:09Z
# YYYY-MM-DDThh:mm:ssZ
import os


def get_dir_size(path="."):
    total = 0
    counter = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
                counter += 1
        else:
            print("file_num", counter)
    return total


text = "libgcc-s1\tlibgcc1 (= 1:12.1.0-2ubuntu1~22.04)\tlibgcc1 (<< 1:10)\t12.1.0-2ubuntu1~22.04"
dpkg_s_list = dpkg_s_list = text.strip().split("\t")

print(dpkg_s_list)
