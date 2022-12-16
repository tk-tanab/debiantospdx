import os
import re
import subprocess
import sys
import time

import deb_spdx
import spdx_exist


def make_pv_vrp_dict(pv_dict: dict[str, str], vrp_dict: dict[str, list[list[str]]]):
    """
    pv_dict と vrp_dict の作成

    Args:
        pv_dict: パッケージとバージョンの対応辞書
        vrp_dict: Virtual と Replace の辞書
    """
    dpkg_status_list = subprocess.run(
        ["dpkg-query", "-W", "-f=${Package}\t${Provides}\t${Replaces}\t${Version}\n"], capture_output=True, text=True
    ).stdout.splitlines()

    # Virtual と Replace の辞書作成
    for dpkg_s in dpkg_status_list:

        # dpkg_s_list: Package, Provides, Replaces, Version
        dpkg_s_list = dpkg_s.strip().split("\t")

        pv_dict[dpkg_s_list[0]] = dpkg_s_list[3]

        if dpkg_s_list[1]:
            add_vrp_dict(dpkg_s_list[1], dpkg_s_list[0], vrp_dict)
        if dpkg_s_list[2]:
            add_vrp_dict(dpkg_s_list[2], dpkg_s_list[0], vrp_dict)

    # 重複削除
    for key, value in vrp_dict.items():
        vrp_dict[key] = [list(j) for j in list(set([tuple(i) for i in value]))]


def add_vrp_dict(vrp_names: str, p_name: str, vrp_dict: dict[str, list[list[str]]]):
    """
    Virtual と Replace の辞書に情報を追加

    Args:
        vrp_names: 代替できるパッケージの名前の列記
        p_name: リアルなパッケージの名前
        vrp_dict: Virtual と Replace の辞書
    """
    vrp_name_list = vrp_names.split(", ")
    for vrp_name in vrp_name_list:
        # vrp_name_split: [Virtual or Replace Package, (比較演算子, Version)]
        vrp_name_split = [i for i in re.split(" |\\(|\\)|\\[.*?\\]", vrp_name) if i]

        if vrp_name_split[0] in vrp_dict:
            vrp_dict[vrp_name_split[0]].append([p_name] + vrp_name_split[1:])
        else:
            vrp_dict[vrp_name_split[0]] = [[p_name] + vrp_name_split[1:]]


if __name__ == "__main__":
    package_name = "accountsservice"
    auth_name = "Taketo"
    all_analyze = True
    dir_path = ""

    time_start = time.perf_counter()

    pv_dict: dict[str, str] = {}  # {p_name: version}
    vrp_dict: dict[str, list[list[str]]] = {}  # {vrp_name: [[p_name, c_operator, version]]}

    make_pv_vrp_dict(pv_dict, vrp_dict)

    if package_name not in pv_dict:
        print(package_name, "is Not exist", file=sys.stderr)
        exit(1)

    # ディレクトリ記憶
    cwd = os.getcwd()

    if all_analyze:
        package_name = "ALL"

    # すでに同名のSPDX展開ディレクトリがある場合はエラー出力
    # 完全に同名のバージョンは複数ない
    dir_name = os.path.dirname(__file__) + "/../SPDX/" + package_name
    try:
        os.makedirs(dir_name)
        os.chdir(dir_name)
    except FileExistsError:
        print("That SPDX already exists", file=sys.stderr)
        sys.exit(1)

    # dir_name = os.path.dirname(__file__) + "/../SPDX/ALL"
    # os.chdir(dir_name)

    if all_analyze:
        # すべてのパッケージ解析
        for p_name in pv_dict.keys():
            if not spdx_exist.spdx_exist(p_name, pv_dict[p_name]):
                deb_class = deb_spdx.Deb_Spdx(pv_dict, vrp_dict, p_name, auth_name, [], 0, 0)
                deb_class.init_treated_list()
                deb_class.run()
    else:
        # 通常実行
        deb_class = deb_spdx.Deb_Spdx(pv_dict, vrp_dict, package_name, auth_name, [], 0, 0)
        deb_class.init_treated_list()
        deb_class.run()

    os.chdir(cwd)

    time_finish = time.perf_counter()

    # print("time", time_finish-time_start)
    # print("num of packages", len(deb_class.treated_list))
