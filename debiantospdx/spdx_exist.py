import os
import glob

def spdx_exist(p_name, version)-> str:
        """
        指定されたパッケージ情報を含むSPDXファイルの検出
        ない場合はFalse、ある場合はSPDXファイルのパスを返す

        Args: 
            p_name: 存在するか確認するパッケージ
        Returns:
            bool or SPDXファイルのパス
        """
        if os.path.exists(p_name + ".spdx"):
            return p_name + ".spdx"
        else:
            for spdx_path in glob.glob("*.Cycle.spdx"):
                with open(spdx_path, mode="r", encoding="utf-8") as f:
                    text = f.read()
                if ("\nPackageName: " + p_name + '\nPackageVersion: ' + version) in text:
                    return spdx_path
            else:
                return ""
            
if __name__ == "__main__":
    p_name = "zstd"
    version = "1.4.8+dfsg-3build1"
    os.chdir("/home/tk-tanab/taketo/syuron/git/spdx_transitive/SPDX/ALL")
    if (path:=spdx_exist(p_name, version)):
        print(path)
    else:
        print("Not exist")