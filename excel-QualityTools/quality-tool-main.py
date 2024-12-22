import xlwt
import re
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, List, NamedTuple, Sequence, Tuple, Union, cast

class YenpWarningTool(object):
    warningSplitFilesMap = {
        "phy_ip": {
            "fileName": "aks_phy",
            "keywords": [
                "aks_phy"
            ]
        },
        "ddrc_ip": {
            "fileName": "umctl2",
            "keywords": [
                "umctl2"
            ]
        }
    }

    def LoadSourceFiles(self, sourceFilesPath: Union[str, list]):
        filePaths = []
        if isinstance(sourceFilesPath, str):
            filePaths = [sourceFilesPath]
        else:
            filePaths = sourceFilesPath
    
        print(filePaths)
    
    def RunLogSplit(self, splitRulesMap: dict, logLines: list = []):
        for idx, line in enumerate(logLines):
            print(idx, line)

class YenpEnvDefineTool(object):
    defineSplitFilesMap = {
        "phy_ip": {
            "fileName": "aks_phy",
            "keywords": [
                "aks_phy"
            ]
        },
        "ddrc_ip": {
            "fileName": "umctl2",
            "keywords": [
                "umctl2"
            ]
        }
    }

    def LoadSourceFiles(self, sourceFilesPath: Union[str, list]):
        filePaths = []
        if isinstance(sourceFilesPath, str):
            filePaths = [sourceFilesPath]
        else:
            filePaths = sourceFilesPath
    
        print(filePaths)
    
    def RunLogSplit(self, splitRulesMap: dict, logLines: list = []):
        # fileContent = "\n".join(logLines)
        # print(fileContent)
        _splitLinePattern = r'File:\s*(/[^ ]+\..+)'
        _splitIdxs = []
        
        for idx, line in enumerate(logLines):
            # 使用 re.search() 查找匹配
            match = re.search(_splitLinePattern, line)
            if match:
                # 获取匹配的文件路径
                file_path = match.group(1)
                print(idx, f"匹配的文件路径: {file_path}")
                _splitIdxs.append(idx)
            else:
                print(idx, "未找到匹配的文件路径")
        
        _matchedBuffer = ""


class QualityTool(object):
    pass


if __name__ == "__main__":
    print("hello world")
    testTool = YenpEnvDefineTool()
    testTool.RunLogSplit({}, ["line1", "line2"])