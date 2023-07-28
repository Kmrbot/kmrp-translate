import yaml
import yaml.scanner
import os
from pathlib import Path
from nonebot.log import logger


def get_translator_yaml_data():
    try:
        # 每次都重新加载 即可以动态重载 性能消耗可忽略
        with open(Path(os.path.dirname(__file__)).joinpath("translator_config.yaml"), "r", encoding="utf8") as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        logger.error("get_translator_yaml_data fail ! File not found !")
        data = None
    except yaml.scanner.ScannerError:
        logger.error("get_translator_yaml_data fail ! Scanner Error !")
        data = None
    return data


def get_tencent_translator_config():
    """ 获取腾讯翻译的配置 """
    data = get_translator_yaml_data()
    if data is None:
        return {}
    else:
        return data.get("Tencent", {})


def get_youdao_translator_config():
    """ 获取有道翻译的配置 """
    data = get_translator_yaml_data()
    if data is None:
        return {}
    else:
        return data.get("Youdao", {})

