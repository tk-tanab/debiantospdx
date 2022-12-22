import hashlib
import json
import os
import re
import subprocess
import uuid

import control_to_dict
import dict_to_tv
import make_tv_dict
from search import take_spdx_path


class DebSpdx:

    pv_dict: dict[str, str]  # {p_name: version}
    vrp_dict: dict[str, list[list[str]]]  # {vrp_name: [[p_name, c_operator, version]]}
    tv_dict: dict[str, list[dict[str, list[str]]]]  # SPDX.json 参照
    control_dict: dict[str, list[str]]  # {field_name: [values]}
    package_name: str
    auth_name: str
    organization: str
    first_mode: int
    rest_mode: int
    rp_count: int
    trail_list: list[str]  # [p_name]
    treated_num: list[int] = [0]
    treated_list: list[str] = []
    doc_comment = """<text> Generated with DebianToSPDX and provided on an "AS IS" BASIS,
                        WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
                        No content created from DebianToSPDX should be considered or used as legal advice.
                        Consult an Attorney for any legal advice. </text>"""

    def return_spdx(self):
        return self.tv_dict

    def __init__(
        self, pv_dict, vrp_dict, package_name, auth_name, organization, trail_list: list[str], first_mode=2, rest_mode=1
    ):
        """
        初期化
        """
        self.pv_dict = pv_dict
        self.vrp_dict = vrp_dict
        self.tv_dict = {}
        self.control_dict = {}
        self.package_name = package_name
        self.auth_name = auth_name
        self.organization = organization
        self.trail_list = trail_list.copy()
        self.first_mode = first_mode
        self.rest_mode = rest_mode
        self.rp_count = 0

    def init_treated_list(self):
        self.treated_list.clear()

    def rm_license_dup(self, lic_dict_list):
        """
        未定義ライセンスの重複削除

        Args:
            lic_dict_list(list[str]): 未定義ライセンスのリスト
        """
        lic_rm_dup_list = []
        for lic_dict in lic_dict_list:
            for lic_rm_dup in lic_rm_dup_list:
                if lic_rm_dup == lic_dict:
                    break
            else:
                lic_rm_dup_list.append(lic_dict)
        else:
            return lic_rm_dup_list

    def merge_tv_control(self):
        """
        spdxファイルにcontrolファイルの情報を結合
        パッケージ間の依存関係情報 以外を追加・修正
        """
        tv_dict = self.tv_dict
        control_dict = self.control_dict

        # パッケージ情報の追加・修正
        package_dict = tv_dict["Package"][0]
        package_dict["PackageName"] = control_dict["Package"]
        package_dict["PackageVersion"] = control_dict["Version"]
        package_dict["SPDXID"] = ["SPDXRef-" + package_dict["PackageName"][0].replace("+", "Plus")]
        if "Homepage" in control_dict:
            package_dict["PackageHomePage"] = control_dict["Homepage"]
        package_dict["PackageComment"] = control_dict["Description"]
        package_dict["Relationship"] = []

        # クリエーション情報の追加・修正
        cre_dict = tv_dict["Creation Information"][0]
        cre_dict["Creator"].append("Tool: spdx_transitive")
        if self.auth_name is not None:
            cre_dict["Creator"].append("Person: " + self.auth_name)
        if self.organization is not None:
            cre_dict["Creator"].append("Organization: " + self.organization)

        # ドキュメント情報の追加・修正
        doc_dict = tv_dict["Document Information"][0]
        doc_dict["DocumentName"] = [control_dict["Package"][0] + "_" + control_dict["Version"][0]]
        # created と packagename と versionから生成(グローバルに参照できるアドレスがある方が望ましい)
        doc_dict["DocumentNamespace"] = [
            "http://spdx.org/spdxdocs/"
            + doc_dict["DocumentName"][0]
            + "-"
            + str(uuid.uuid5(uuid.NAMESPACE_URL, (doc_dict["DocumentName"][0] + cre_dict["Created"][0])))
        ]
        doc_dict["ExternalDocumentRef"] = []
        doc_dict["Relationship"] = [doc_dict["SPDXID"][0] + " DESCRIBES " + package_dict["SPDXID"][0]]

        doc_dict["DocumentComment"] = [self.doc_comment]

        # ファイルパス と SPDXID の修正 と Relationship の追加
        for i, file_dict in enumerate(tv_dict["File"]):
            file_dict["FileName"] = [file_dict["FileName"][0].replace(("./" + package_dict["PackageName"][0]), "", 1)]
            file_dict["SPDXID"] = [package_dict["SPDXID"][0] + "-file-" + str(i)]
            file_dict["Relationship"] = [package_dict["SPDXID"][0] + " CONTAINS " + file_dict["SPDXID"][0]]

        tv_dict["Extracted License"] = self.rm_license_dup(tv_dict["Extracted License"])

    def add_relationship(self, d_list: list[str]) -> list[str]:
        """
        依存関係を処理してRelationshipフィールドを追加

        Args:
            d_list: 依存しているパッケージのリスト
        Returns:
            list[str]: 未解決な相互依存パッケージのリスト
        """
        pv_dict = self.pv_dict
        vrp_dict = self.vrp_dict
        mutual_list: list[str] = []
        package_dict = self.tv_dict["Package"][0]
        termed_d_list = []
        not_out_list = []

        dori_list = []
        for dp in d_list:
            or_list = dp.split(" | ")
            ori_list = []
            for d in or_list:
                ori_list.append([i for i in re.split(" |\\(|\\)|\\[.*?\\]|:any", d) if i])
            dori_list.append(ori_list)

        for ori_list in dori_list:
            for or_list in ori_list:
                if or_list[0] in pv_dict and self.check_version(or_list[1:], ["=", pv_dict[or_list[0]]]):
                    real_dp_name = or_list[0]
                    break

                elif or_list[0] in vrp_dict:
                    for real_p_list in vrp_dict[or_list[0]]:
                        if self.check_version(or_list[1:], real_p_list[1:]):
                            real_dp_name = real_p_list[0]
                            self.rp_count += 1
                            break
                    else:
                        continue
                    break
            else:
                continue

            # 同じ依存先を複数回指定または自分を依存先に指定しているとき
            if real_dp_name in termed_d_list or real_dp_name == self.package_name:
                continue
            else:
                termed_d_list.append(real_dp_name)

            # 既に存在しているとき
            if spdx_path := take_spdx_path(real_dp_name):
                self.add_external_ref(spdx_path, real_dp_name)
            # このパッケージの別の枝(未出力)で調査済みのとき
            elif real_dp_name in not_out_list:
                package_dict["Relationship"].append(
                    package_dict["SPDXID"][0] + " DEPENDS_ON SPDXRef-" + real_dp_name.replace("+", "Plus")
                )
            # 上の階層のパッケージと相互依存になっているとき か すでに上の階層のパッケージの別の枝で調査済みのとき
            elif real_dp_name in self.trail_list or real_dp_name in self.treated_list:
                package_dict["Relationship"].append(
                    package_dict["SPDXID"][0] + " DEPENDS_ON SPDXRef-" + real_dp_name.replace("+", "Plus")
                )
                mutual_list.append(real_dp_name)
            else:
                snap_len_treated = len(self.treated_list)
                new_spdx = DebSpdx(
                    pv_dict,
                    vrp_dict,
                    real_dp_name,
                    self.auth_name,
                    self.organization,
                    self.trail_list,
                    self.first_mode,
                    self.rest_mode,
                )
                r_mutual_list = new_spdx.run()

                # 下の階層のパッケージと相互依存になっているとき
                if r_mutual_list != []:
                    # relationship
                    package_dict["Relationship"].append(
                        package_dict["SPDXID"][0] + " DEPENDS_ON SPDXRef-" + real_dp_name.replace("+", "Plus")
                    )
                    self.merge_spdx(new_spdx.return_spdx())
                    not_out_list += self.treated_list[snap_len_treated:]
                    mutual_list += [p for p in r_mutual_list if (p != self.package_name) and (p not in not_out_list)]
                # 問題なし
                else:
                    if os.path.exists(real_dp_name + ".spdx"):
                        self.add_external_ref(real_dp_name + ".spdx", real_dp_name)
                    else:
                        self.add_external_ref(real_dp_name + ".Cycle.spdx", real_dp_name)

        self.tv_dict["Document Information"][0]["ExternalDocumentRef"] = list(
            set(self.tv_dict["Document Information"][0]["ExternalDocumentRef"])
        )
        mutual_list = list(set(mutual_list))
        return mutual_list

    def add_external_ref(self, spdx_path: str, p_name: str):
        """
        外部のSPDXファイルに依存している場合のRelationshipフィールドを追加

        Args:
            spdx_path: 外部のSPDXファイルのパス
        """
        with open(spdx_path, mode="r", encoding="utf-8") as f:
            lines_strip = [s.strip() for s in f.readlines()]
        for line in lines_strip:
            if "DocumentNamespace" in line:
                ref_space = line[19:]
                break
        else:
            return

        with open(spdx_path, mode="rb") as f:
            file_data = f.read()
        hash_sha1 = hashlib.sha1(file_data).hexdigest()
        exd_list = self.tv_dict["Document Information"][0]["ExternalDocumentRef"]
        pac_dict = self.tv_dict["Package"][0]

        doc_ref = "DocumentRef-" + spdx_path[:-5]
        exd_list.append(doc_ref + " " + ref_space + " SHA1: " + hash_sha1)
        pac_dict["Relationship"].append(
            (pac_dict["SPDXID"][0] + " DEPENDS_ON " + doc_ref + ":SPDXRef-" + p_name.replace("+", "Plus"))
        )

    def merge_spdx(self, dep_tv_dict):
        """
        2つのSPDXの情報を結合

        Args:
            dep_tv_dict: 結合するSPDXの情報
        """
        self.tv_dict["Document Information"][0]["ExternalDocumentRef"] += dep_tv_dict["Document Information"][0][
            "ExternalDocumentRef"
        ]
        self.tv_dict["Package"] += dep_tv_dict["Package"]
        self.tv_dict["File"] += dep_tv_dict["File"]
        self.tv_dict["Extracted License"] += dep_tv_dict["Extracted License"]
        self.tv_dict["Extracted License"] = self.rm_license_dup(self.tv_dict["Extracted License"])

    def compare_version(self, v1, v2, c_operator) -> bool:
        try:
            subprocess.run(["dpkg", "--compare-versions", v1, c_operator, v2], check=True)
        except subprocess.CalledProcessError:
            return False
        return True

    def check_version(self, term_list, cond_list) -> bool:
        """
        バージョン制約を満たしているかの確認

        Args:
            term_list: [p_name, c_operator, version] 制約
            cond_list: [p_name, c_operator, version] 現状

        Returns:
            bool: バージョン制約を満たしていればTrue
        """
        if term_list == []:
            return True
        elif cond_list == []:
            return False

        if term_list[0] == "=":
            match cond_list[0]:
                case "=":
                    co = "eq"
                case "<=":
                    co = "le"
                case ">=":
                    co = "ge"
                case "<<":
                    co = "lt"
                case _:
                    co = "gt"
        elif term_list[0] == "<=":
            if cond_list[0] == "=" or cond_list[0] == ">=":
                co = "ge"
            elif cond_list[0] == ">>":
                co = "gt"
            else:
                return True
        elif term_list[0] == ">=":
            if cond_list[0] == "=" or cond_list[0] == "<=":
                co = "le"
            elif cond_list[0] == "<<":
                co = "lt"
            else:
                return True
        elif term_list[0] == "<<":
            if cond_list[0] == "<=" or cond_list[0] == "<<":
                return True
            else:
                co = "gt"
        else:
            if cond_list[0] == ">=" or cond_list[0] == ">>":
                return True
            else:
                co = "lt"

        return self.compare_version(term_list[1], cond_list[1], co)

    def run(self) -> list[str]:
        """
        DebianパッケージのSPDXを推移的に生成

        Returns:
            list[str]: 未解決な相互依存パッケージのリスト
        """

        package_name = self.package_name
        self.trail_list.append(package_name)

        package_status = subprocess.run(
            ["dpkg-query", "-s", package_name], capture_output=True, text=True
        ).stdout.strip()
        self.control_dict = control_to_dict.control_to_dict(package_status)

        if len(self.treated_list) == 0:
            self.tv_dict = make_tv_dict.make_tv_dict(package_name, self.first_mode)
        else:
            self.tv_dict = make_tv_dict.make_tv_dict(package_name, self.rest_mode)

        self.treated_list.append(package_name)

        self.merge_tv_control()

        self.treated_num[0] += 1
        print("\rNumber of Analyzed Pacakges: " + str(self.treated_num[0]) + "/" + str(len(self.pv_dict)), end="")

        mutual_list = self.add_relationship(self.control_dict["Depends"])

        spdx_text = dict_to_tv.dict_to_tv(self.tv_dict)

        if mutual_list == []:
            if len(self.tv_dict["Package"]) > 1:
                with open(package_name + ".Cycle.spdx", mode="w") as f:
                    f.write(spdx_text)
            else:
                with open(package_name + ".spdx", mode="w") as f:
                    f.write(spdx_text)

        # 依存関係の参照において置換した回数を保存
        with open("rp_times.json", mode="r") as f:
            rp_times: dict[str, int] = json.load(f)
        rp_times[package_name] = self.rp_count
        with open("rp_times.json", "w") as f:
            json.dump(rp_times, f, indent=4)

        return mutual_list
