# 2022-11-21T03:49:09Z
# YYYY-MM-DDThh:mm:ssZ

import json

# with open("rp_times.json", mode="r") as f:
#     rp_times: dict[str, int] = json.load(f)
rp_times = {}
rp_times["aa"] = 22
with open("rp_times.json", "w") as f:
    json.dump(rp_times, f, indent=4)
