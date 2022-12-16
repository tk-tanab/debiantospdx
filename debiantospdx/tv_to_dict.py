from typing import Tuple


def split_tv(line: str, line_iter) -> Tuple[str, str]:
    """
    文字列をfield, valueに分割

    Args:
        line: spdx_tvの1行
        line_iter: spdx_tvの全行をiterにしたもの

    Returns:
        Tuple[str, str]: field, value
    """

    tag, value = line.split(": ", 1)
    # valueが<text>複数行にまたがれる形式だった場合
    # iterを読み進める
    if value.strip().startswith("<text>"):
        for text in line_iter:
            value += "\n"
            value += text
            if "</text>" in text:
                break
    return tag, value


# TagValue形式のspdxをjson形式に変換
def tv_to_dict(spdx_tv: str) -> dict[str, list[dict[str, list[str]]]]:
    """
    spdx_tvファイルの文字列を辞書形式に変換

    Args:
        spdx_tv: spdx_tvファイルのパス

    Returns:
        dict: 変換した辞書
    """
    # scancode-toolkitが生成したspdxを読む
    # iterにするのはtextとfieldの見分けがつかないため、
    # 条件でtextを読み飛ばすことができず、iterを送るしかないから
    with open(spdx_tv, mode="r", encoding="utf-8") as f:
        lines_strip = [s.strip() for s in f.read().strip().splitlines()]
        lines_iter = iter(lines_strip)

    spdx_dict: dict[str, list[dict[str, list[str]]]] = {}
    new_elem_dict: dict[str, list[str]] = {}
    info_name: str = ""

    for line in lines_iter:
        # infomationは新たな要素の書き出し
        if line.startswith("#"):
            info_name = line[1:].strip()

            if info_name == "Creation Info":
                info_name = "Creation Information"
            elif info_name == "Extracted Licenses":
                info_name = "Extracted License"

            if info_name not in spdx_dict:
                new_elem_dict = {}
                spdx_dict[info_name] = [new_elem_dict]
        # tag, valueの行の扱い(空行を除く)
        elif line.strip():
            tag, value = split_tv(line, lines_iter)
            if tag in new_elem_dict:
                new_elem_dict[tag].append(value)
            else:
                new_elem_dict[tag] = [value]
                if info_name == "Package":
                    if tag == "PackageName":
                        new_elem_dict["PackageVersion"] = []
                    elif tag == "SPDXID":
                        new_elem_dict["PackageHomePage"] = []
        # 空行の扱い
        elif new_elem_dict:
            new_elem_dict = {}
            spdx_dict[info_name].append(new_elem_dict)

    else:
        for info_dict_list in spdx_dict.values():
            if (last_dict := info_dict_list.pop()) != {}:
                info_dict_list.append(last_dict)

        return spdx_dict
