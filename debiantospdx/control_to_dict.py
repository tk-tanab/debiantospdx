import re
from typing import Tuple


def split_fv(line, control_lines) -> Tuple[str, str]:
    """
    文字列をfield, valueに分割

    Args:
        line: control_linesの1行
        control_lines: controlファイルのテキスト

    Returns:
        Tuple[str, str]: field, value
    """
    field, value = line.split(": ", 1)
    # valueが複数行にまたがれる形式だった場合
    # <text></text>で包む
    if field == "Description":
        value = "<text>" + value
        for text in control_lines[control_lines.index(line) + 1 :]:
            if text[0].isspace():
                value += "\n"
                value += text
            else:
                break
        value += "</text>"
    return field, value


def make_dict(field, value, control_dict):
    """
    field, dictから辞書を生成

    Args:
        field: controlのfield
        value: controlのvalue
        control_dict: 入力する辞書
    """
    # 仮想パッケージの扱いどうしよう？showpkgでProvidesは確認できるが。。(未実装)
    # パッケージ群のvalueをリスト化・整形して辞書に入力
    if field in [
        "Depends",
        "Suggests",
        "Pre-Depends",
        "Recommends",
        "Enhances",
        "Breaks",
        "Conflicts",
        "Build-Depends",
        "Build-Depends-Indep",
        "Build-Conflicts",
        "Build-Conflicts-Indep",
    ]:
        control_dict[field] = [i for i in re.split(", ", value) if i]
    else:
        control_dict[field] = [value]


def control_to_dict(control_text: str) -> dict[str, list[str]]:
    """
    controlファイルの文字列を辞書形式に変換

    Args:
        control_text: controlファイルのテキスト

    Returns:
        dict: 変換した辞書
    """
    control_lines = control_text.splitlines()

    # 初期化
    control_dict: dict[str, list[str]] = {}
    control_dict["Depends"] = []

    # 1行ずつ分解
    for line in control_lines:
        # fieldがある行に対してのみ実行
        if line and (not line[0].isspace()) and (": " in line):
            field, value = split_fv(line, control_lines)
            make_dict(field, value, control_dict)

    # 依存関係系をまとめる
    for k in list(control_dict.keys()):
        if k in ["Suggests", "Pre-Depends", "Recommends"]:
            control_dict["Depends"] += control_dict.pop(k)

    return control_dict
