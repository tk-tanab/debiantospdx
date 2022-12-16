# poetry runでテストする際はこのファイルが呼ばれる
# pyproject.tomlの [tool.poetry.scripts] には指定できないので注意
from template import cli

if __name__ == "__main__":
    cli.entry()
