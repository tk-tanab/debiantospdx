# debiantospdx

[![Apache2.0 License](https://img.shields.io/badge/License-Apatch2.0-green.svg?style=for-the-badge)](https://choosealicense.com/licenses/apache-2.0/)

システムに存在するすべてのDebianパッケージのSPDXファイルを生成するコマンドラインツール

パッケージ名・バージョン・ソフトウェアライセンス・コピーライト・パッケージ間の依存関係の解析を行う

## Usage/Examples

```bash
debiantospdx [ディレクトリのパス] [オプション]
```
SPDXファイルを置くパスをして実行する

オプションについては以下の通り
```bash
  -h, --help            HELPメッセージの出力
  
  -p, --person          SPDXファイルの作者名（個人）
  -pe                   SPDXファイルの作者のメールアドレス
  -o, --organization    SPDXファイルの作者名（組織）
  -oe                   SPDXファイルの作者のメールアドレス
  
  --package             指定したパッケージのPDXファイルを生成
  --all                 インストール済みのすべてのパッケージのSPDXファイルを生成
  --search              指定したパッケージの情報をSPDXファイルから抽出
```


## Authors

- [@tk-tanab](https://github.com/tk-tanab)


## License

- [Apatch2.0](https://choosealicense.com/licenses/apache-2.0/)

