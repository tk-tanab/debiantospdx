import math
import time


def for_sigma(x0: float, x1: int, x2: int) -> float:
    """for文を使ってsigmaを計算する

    Args:
        x0 (float): 指数
        x1 (int): 底の初期値
        x2 (int): 底の終値

    Returns:
        float: 結果
    """
    time_start = time.perf_counter()

    sum_result = 0
    for k in range(x1, x2 + 1):
        sum_result += math.pow(k, x0)

    time_end = time.perf_counter()

    print("for: ", (time_end - time_start))

    return sum_result
