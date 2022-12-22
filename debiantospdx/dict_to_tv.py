def dict_to_tv(tv_dict: dict[str, list[dict[str, list[str]]]]) -> str:
    """
    SPDXのdictをTagValue形式のtextに変換

    Args:
        tv_dict: dict[str, list[dict[str, list[str]]]]: SPDXのdict

    Returns:
        str: TagValue形式のtext
    """

    tv_text = ""

    for info_name, dict_list in tv_dict.items():
        tv_text += "## " + info_name + "\n\n"

        for elem_dict in dict_list:
            for tag, value_list in elem_dict.items():
                for value in value_list:
                    tv_text += tag + ": " + value + "\n"
            else:
                tv_text += "\n\n"
    else:
        return tv_text
