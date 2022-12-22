import glob
import json
import os
import pprint


def take_spdx_path(p_name) -> str:
    """
    指定されたパッケージ情報を含むSPDXファイルの検出
    ない場合は空、ある場合はSPDXファイルのパスを返す

    Args:
        p_name: 存在するか確認するパッケージ
        version: パッケージのバージョン
    Returns:
        空 or SPDXファイルのパス
    """
    if os.path.exists(p_name + ".spdx"):
        return p_name + ".spdx"
    else:
        for spdx_path in glob.glob("*.Cycle.spdx"):
            with open(spdx_path, mode="r", encoding="utf-8") as f:
                text = f.read()
            if ("\nPackageName: " + p_name + "\nPackageVersion: ") in text:
                return spdx_path
        else:
            return ""


def pick_version(path, p_name):
    in_package_info = False
    version = ""
    with open(path, mode="r") as f:
        for line in f:
            if in_package_info:
                version = line[16:].strip()
                break
            if line == "## File\n":
                break
            if line == ("PackageName: " + p_name + "\n"):
                in_package_info = True
    return version


def take_pakages(path):
    packages = []
    with open(path, mode="r") as f:
        for line in f:
            if line.startswith("PackageName: "):
                packages.append(line[13:].strip())
            if line == "## File\n":
                break
    return packages


def take_expaths(path):
    expaths = []
    with open(path, mode="r") as f:
        for line in f:
            if line.startswith("ExternalDocumentRef: "):
                expaths.append(line.split()[1][12:].strip() + ".spdx")
            if line == "## Package\n":
                break
    return expaths


def make_spdx_dict() -> dict[str, list[str]]:
    spdx_dict: dict[str, list[str]] = {}
    for spdx_path in glob.glob("*.spdx"):
        spdx_dict[spdx_path] = take_expaths(spdx_path)
    else:
        return spdx_dict


# 実行時間を考慮する
def make_depend_recursive_dict(spdx_dict: dict[str, list[str]]):
    dr_dict: dict[str, list[str]] = {}
    for spdx in spdx_dict:
        if spdx not in dr_dict:
            make_dr_dict_sub(spdx, dr_dict, spdx_dict)
    else:
        return dr_dict


def make_dr_dict_sub(spdx_path: str, dr_dict: dict[str, list[str]], spdx_dict: dict[str, list[str]]):
    dr_dict[spdx_path] = spdx_dict[spdx_path].copy()
    for spdx in spdx_dict[spdx_path]:
        if spdx not in dr_dict:
            make_dr_dict_sub(spdx, dr_dict, spdx_dict)
        dr_dict[spdx_path] += dr_dict[spdx]
    else:
        dr_dict[spdx_path] = list(set(dr_dict[spdx_path]))


def take_depends_recursive(p_name: str, spdx_path: str, dr_dict: dict[str, list[str]]):
    depends = take_pakages(spdx_path)
    depends.remove(p_name)
    for ex_spdx in dr_dict[spdx_path]:
        depends += take_pakages(ex_spdx)
    else:
        return depends


def take_rdepends_recursive(p_name: str, spdx_path: str, dr_dict: dict[str, list[str]]):
    rdepends = take_pakages(spdx_path)
    rdepends.remove(p_name)
    for spdx, ex_spdxs in dr_dict.items():
        if spdx_path in ex_spdxs:
            rdepends += take_pakages(spdx)
    else:
        return rdepends


def count_cycle_depend(dr_dict: dict[str, list[str]]):
    counter = 0
    for spdx, ex_spdxs in dr_dict.items():
        times = 1
        selfcycle = 0
        if spdx.endswith("Cycle.spdx"):
            times = len(take_pakages(spdx))
            selfcycle = 1
        counter += (sum(ex_spdx.endswith("Cycle.spdx") for ex_spdx in ex_spdxs) + selfcycle) * times
    else:
        return counter


def count_cycle_spdx():
    return len(glob.glob("*.Cycle.spdx"))


def get_spdxs_size():
    sum_bytesize = 0
    for spdx in glob.glob("*.spdx"):
        sum_bytesize += os.path.getsize(spdx)
    else:
        return sum_bytesize


def count_spdx():
    return len(glob.glob("*.spdx"))


def count_packages():
    counter = 0
    for spdx in glob.glob("*.spdx"):
        counter += len(take_pakages(spdx))
    else:
        return counter


def take_files(path):
    packages = []
    with open(path, mode="r") as f:
        for line in f:
            if line.startswith("PackageName: "):
                packages.append(line[13:].strip())
            if line == "## File\n":
                break
    return packages


def count_files():
    counter = 0
    for spdx in glob.glob("*.spdx"):
        with open(spdx, mode="r") as f:
            text = f.read()
        counter += text.count("\nFileName: ")
    else:
        return counter


def count_replace(dr_dict: dict[str, list[str]]):
    with open("rp_times.json", mode="r") as f:
        rp_dict: dict[str, int] = json.load(f)

    file_rp_dict: dict[str, int] = {}
    numpackage_dict: dict[str, int] = {}
    for spdx in dr_dict:
        file_rp_dict[spdx] = 0
        packages = take_pakages(spdx)
        numpackage_dict[spdx] = len(packages)
        for package in packages:
            file_rp_dict[spdx] += rp_dict[package]

    sum_counter = 0

    for spdx, ex_spdxs in dr_dict.items():
        counter = file_rp_dict[spdx]
        for ex_spdx in ex_spdxs:
            counter += file_rp_dict[ex_spdx]
        else:
            sum_counter = counter * numpackage_dict[spdx]

    return sum_counter


def print_package_info(p_name):
    spdx_path = take_spdx_path(p_name)
    version = pick_version(spdx_path, p_name)
    spdx_dict = make_spdx_dict()
    dr_dict = make_depend_recursive_dict(spdx_dict)
    depends = take_depends_recursive(p_name, spdx_path, dr_dict)
    rdepends = take_rdepends_recursive(p_name, spdx_path, dr_dict)
    print("Package Name".ljust(17) + ":", p_name)
    print("Package Version".ljust(17) + ":", version)
    print("SPDX File Name".ljust(17) + ":", spdx_path, "\n")
    print("Dependency Recursive:")
    pprint.pprint(depends, width=150, compact=True)
    print("Reverse Dependency Recursive:")
    pprint.pprint(rdepends, width=150, compact=True)


def print_spdx_files_info():
    spdx_dict = make_spdx_dict()
    dr_dict = make_depend_recursive_dict(spdx_dict)
    print("Number of Cycle.spdx files".ljust(50) + ":", count_cycle_spdx())
    print("Number of Circulation Dependent Occurrences".ljust(50) + ":", count_cycle_depend(dr_dict))
    print("Total Bytes".ljust(50) + ":", get_spdxs_size())
    print("Number of SPDX files".ljust(50) + ":", count_spdx())
    print("Number of Packages".ljust(50) + ":", count_packages())
    print("Number of Files".ljust(50) + ":", count_files())
    print("Number of times Replace or Provide was referenced".ljust(50) + ":", count_replace(dr_dict))
