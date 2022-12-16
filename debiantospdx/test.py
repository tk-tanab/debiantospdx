# 2022-11-21T03:49:09Z
# YYYY-MM-DDThh:mm:ssZ
import re

text = "libgcc-s1\tlibgcc1 (= 1:12.1.0-2ubuntu1~22.04)\tlibgcc1 (<< 1:10)\t12.1.0-2ubuntu1~22.04"
vrp_name = "libgcc1[amd64] (= 1:12.1.0-2ubuntu1~22.04)"
vrp_name_split = [i for i in re.split(" |\\(|\\)|\\[.*?\\]", vrp_name) if i]
print(vrp_name_split)

value = [
    [1, 421, 4515, 14],
    [43214, 52353, 32],
    [412, 421, 523, 52],
    [43214, 52353, 32],
    [43],
    [32],
    [43],
    [412, 421, 523, 52],
]
vrp_list = [list(j) for j in list(set([tuple(i) for i in value]))]

print(vrp_list)

doc_comment = """<text>Generated with DebianToSPDX and provided on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    No content created from DebianToSPDX should be considered or used as legal advice.
    Consult an Attorney for any legal advice.</text>"""


print(doc_comment)
