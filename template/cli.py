import argparse

# initファイルがあるのでimportされているのは関数そのもの
# 同じディレクトリでもパッケージ名で指定する必要がある（と思われる）
from template import for_sigma, joblib_sigma


# メインの処理
def main(args):
    """引数に応じて計算したシグマの値を返す

    Args:
        args : parseされた引数オブジェクト
    """
    if args.both or args.for_sigma:
        sigma_result = for_sigma(args.x0, args.x1, args.x2)
        print("for_result", sigma_result * args.coefficient)

    if args.both or args.joblib_sigma:
        sigma_result = joblib_sigma(args.x0, args.x1, args.x2)
        print("joblib_result", sigma_result * args.coefficient)


# 引数の処理 （エントリーポイント）
def entry():
    parser = argparse.ArgumentParser(description="add one float and two integers")
    # 必須の位置引数
    parser.add_argument("x0", type=float, help="exponent number (float)")
    # デフォルト値のあるオプションの位置引数 nargsの指定が必須
    parser.add_argument("x1", type=int, nargs="?", default=1, help="start k number (int)")
    parser.add_argument("x2", type=int, nargs="?", default=100, help="start k number (int)")

    # オプション引数 変数名は長い方になる（cは省略形）
    parser.add_argument("-c", "--coefficient", nargs="?", type=float, default=1, help="coefficient number (float)")

    # 排他的で必須なオプション引数
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--both", action="store_true", help="exert both for_sigma and joblib_sigma")
    group.add_argument("--for_sigma", action="store_true", help="exert for_sigma")
    group.add_argument("--joblib_sigma", action="store_true", help="exert joblib_sigma")

    args = parser.parse_args()
    main(args)
