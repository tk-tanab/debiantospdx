# from や import でパッケージ名を指定するとこのファイルが呼ばれる
# 外部に公開する関数をimport
# 外部に公開したくないパッケージもfrom testpackageforjoblibsigma.cli(モジュール名まで指定) import entry(関数名を指定) とすると呼ばれてしまう
from .for_sigma import for_sigma
from .joblib_sigma import joblib_sigma

# 公開する関数名を指定
__all__ = ["for_sigma", "joblib_sigma"]

# pyproject.tomlと合わせる
__version__ = "0.1.0"
