# 外部パッケージの例として導入した
# https://karupoimou.hatenablog.com/entry/20200305/1583407204
import math
import time

import joblib


def pow_process(k: int, x0: float) -> float:
    """べき乗の結果を返す

    Args:
        k (int): 底
        x0 (float): 指数

    Returns:
        float: 結果
    """
    return math.pow(k, x0)


def joblib_sigma(x0: float, x1: int, x2: int) -> float:
    """joblibを使ってsigmaを計算する

    Args:
        x0 (float): 指数
        x1 (int): 底の初期値
        x2 (int): 底の終値

    Returns:
        float: 結果
    """
    time_start = time.perf_counter()

    k_list = list(range(x1, x2 + 1))
    powk_list = joblib.Parallel(n_jobs=-2)([joblib.delayed(pow_process)(k, x0) for k in k_list])
    sum_result = sum(powk_list)

    time_end = time.perf_counter()

    print("joblib: ", (time_end - time_start))

    return sum_result
