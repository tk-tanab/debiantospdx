# pytest -q tests で実行
from template import for_sigma, joblib_sigma


def test_for_sigma():
    assert for_sigma(1, 1, 100) == 5050


def test_joblib_sigma():
    assert joblib_sigma(1, 1, 100) == 5050
