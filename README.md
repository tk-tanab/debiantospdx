# debiantospdx

[![Apache2.0 License](https://img.shields.io/badge/License-Apatch2.0-green.svg?style=for-the-badge)](https://choosealicense.com/licenses/apache-2.0/)

システムに存在するすべてのDebianパッケージのSPDXファイルを生成するコマンドラインツール

パッケージ名・バージョン・ソフトウェアライセンス・コピーライト・パッケージ間の依存関係の解析を行う

## Usage/Examples

```bash
debiantospdx [ディレクトリのパス] [オプション]
```
SPDXファイルを置くパスをして実行する

オプションとその内容については以下の通り

引数を必要とするものは引数の例を併記する
```bash
  -h, --help            HELPメッセージの出力
  
  -p, --person          SPDXファイルの作者名（引数: 個人名（ex. TK tanab））
  -pe                   SPDXファイルの作者のメールアドレス（引数: 個人のメールアドレス（ex. tanab@hoge.com）
  -o, --organization    SPDXファイルの作者名（引数: 組織名（ex. HIGO Lab））
  -oe                   SPDXファイルの作者のメールアドレス（引数: 組織のメールアドレス（ex. higo-lab@hoge.com）
  
  --package             指定したパッケージのPDXファイルを生成（引数: パッケージ名（ex. python3.10））
  --all                 インストール済みのすべてのパッケージのSPDXファイルを生成
  --search              指定したパッケージの情報をSPDXファイルから抽出（引数: パッケージ名（ex. python3.10））
```
package, all, searchはどれか1つのみを選択して実行する．

packageまたはallを選択した場合は作者名となる個人名または組織名のうち少なくとも1つを必要とする

## Authors

- [@tk-tanab](https://github.com/tk-tanab)


## License

- [Apache2.0](https://choosealicense.com/licenses/apache-2.0/)

