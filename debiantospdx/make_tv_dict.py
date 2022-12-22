import hashlib
import os
import shutil
import subprocess
from datetime import datetime

import tv_to_dict


def analyze_file(package_name: str, file_list: list[str], scan_copyrightfile: bool):
    """
    Debianパッケージのファイルを解析

    Args:
        package_name: 対象パッケージ
        file_list: パッケージのファイルパスのリスト
        scan_copyrightfile: copyrightファイルをscanするか

    Returns:
        list: SPDXの辞書
    """
    hash_list = []
    file_dict_list = []
    copyright_filepath = ""

    for value in file_list:
        if os.path.isfile(value):  # type: ignore
            try:
                with open(value, mode="rb") as f:
                    file_data = f.read()
                hash_sha1 = hashlib.sha1(file_data).hexdigest()  # type: ignore
                hash_list.append(hash_sha1)

                if scan_copyrightfile and value.endswith("copyright"):
                    copyright_filepath = value
                    try:
                        shutil.copyfile(value, package_name + "/copyright")
                    except (FileNotFoundError, PermissionError):
                        pass
                else:
                    file_dict = {
                        "FileName": [value],
                        "SPDXID": [],
                        "FileChecksum": ["SHA1: " + hash_sha1],
                        "LicenseConcluded": ["NOASSERTION"],
                        "LicenseInfoInFile": ["NOASSERTION"],
                        "FileCopyrightText": ["NOASSERTION"],
                    }
                    file_dict_list.append(file_dict)
            except (FileNotFoundError, PermissionError):
                pass
    else:
        hash_list.sort()
        if copyright_filepath == "":
            scan_copyrightfile = False

    tv_dict = scancode(scan_copyrightfile, package_name)
    tv_dict["Package"][0].update(
        {"PackageVerificationCode": [hashlib.sha1("".join(hash_list).encode("utf-8")).hexdigest()]}
    )
    tv_dict["File"] += file_dict_list

    if scan_copyrightfile:
        tv_dict["File"][0]["FileName"] = [copyright_filepath]
        tv_dict["File"][0]["LicenseInfoInFile"] = list(set(tv_dict["File"][0]["LicenseInfoInFile"]))

    return tv_dict


def scancode(is_scan: bool, package_name: str):
    """
    scancodeの分析結果をSPDXの辞書で返す

    Args:
        package_name: 対象パッケージ
        is_scan: scancodeするか

    Returns:
        list: SPDXの辞書
    """
    # 解析なしのテンプレート
    template_tv_dict: dict[str, list[dict[str, list[str]]]] = {
        "Document Information": [
            {
                "SPDXVersion": ["SPDX-2.2"],
                "DataLicense": ["CC0-1.0"],
                "DocumentNamespace": [],
                "DocumentName": [],
                "SPDXID": ["SPDXRef-DOCUMENT"],
                "DocumentComment": [],
                "ExternalDocumentRef": [],
                "Relationship": [],
            }
        ],
        "Creation Information": [{"Creator": [], "Created": [datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")]}],
        "Package": [
            {
                "PackageName": [],
                "PackageVersion": [],
                "SPDXID": [],
                "PackageHomePage": [],
                "PackageDownloadLocation": ["NOASSERTION"],
                "PackageVerificationCode": [],
                "PackageLicenseDeclared": ["NOASSERTION"],
                "PackageLicenseConcluded": ["NOASSERTION"],
                "PackageLicenseInfoFromFiles": ["NOASSERTION"],
                "PackageCopyrightText": ["NOASSERTION"],
            }
        ],
        "File": [],
        "Extracted License": [],
    }
    if is_scan:
        output = package_name + "/output.tag"
        subprocess.run(
            ["scancode", "-clpi", package_name, "--spdx-tv", output], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        tv_dict = tv_to_dict.tv_to_dict(output)
        tv_dict["Creation Information"][0]["Created"] = [datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")]
        return tv_dict
    else:
        return template_tv_dict


def make_tv_dict(package_name, mode):
    """
    SPDXの辞書を生成する

    Args:
        package_name: 対象パッケージ
        mode:
            0: ファイル解析しない
            1: ファイル解析はするが、ライセンスは解析しない
            2: copyrightファイルだけライセンス解析する
            3: 全てのファイルのライセンスを解析する

    Returns:
        list: SPDXの辞書
    """

    # 0: ファイル解析しない
    if mode == 0:
        tv_dict = scancode(False, package_name)
        tv_dict["Package"][0]["FilesAnalyzed"] = ["false"]
        tv_dict["Package"][0].pop("PackageLicenseInfoFromFiles")
        return tv_dict

    # ファイルを展開する作業用ディレクトリの作成
    os.mkdir(package_name)

    # パッケージを構成するファイルの一覧を取得
    file_list = subprocess.run(["dpkg", "-L", package_name], capture_output=True, text=True).stdout.splitlines()

    tv_dict = {}

    # 1: ファイル解析はするが、ライセンスは解析しない
    if mode == 1 or file_list == []:
        tv_dict = analyze_file(package_name, file_list, False)

    # 2: copyrightファイルだけライセンス解析する
    elif mode == 2:
        tv_dict = analyze_file(package_name, file_list, True)

    # 3: 全てのファイルのライセンスを解析する
    elif mode == 3:
        # ファイルを作業用ディレクトリに展開
        for value in file_list:
            if os.path.isdir(value):
                dirname = package_name + value
                os.makedirs(dirname, exist_ok=True)
            else:
                try:
                    shutil.copyfile(value, package_name + value)
                except (FileNotFoundError, PermissionError):
                    pass

        tv_dict = scancode(True, package_name)

    # 作業用ディレクトリの削除
    shutil.rmtree(package_name)

    return tv_dict
