import json
from pathlib import Path
from typing import Final, TypedDict

from utils.config import ensure_plugin_config_from_template


class TranslateRuntimeConfig(TypedDict):
    """kmrp-translate 的运行时配置。"""

    translator: str
    """当前翻译工具：youdao、tencent、ai。"""
    model: str
    """translator 为 ai 时使用的模型类型名，例如 deepseek。其他工具不读这个字段。"""


class TranslateConfig:
    """读写翻译插件配置。文件不存在时按模板生成，每次读取都重新打开。"""

    __PLUGIN: Final[str] = "kmrp-translate"
    __FILENAME: Final[str] = "translate_config.json"
    __TEMPLATE: Final[Path] = Path(__file__).resolve().parent / "translate_config_template.json"

    @classmethod
    def load(cls) -> TranslateRuntimeConfig:
        """
        读取当前翻译工具和模型。

        :return: translator 为 youdao、tencent 或 ai；model 仅在 ai 时使用
        """
        path = ensure_plugin_config_from_template(cls.__PLUGIN, cls.__FILENAME, cls.__TEMPLATE)
        data = json.loads(path.read_text(encoding="utf-8"))
        return {
            "translator": data["translator"],
            "model": data["model"],
        }
