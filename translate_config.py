import json
from pathlib import Path
from typing import Final, TypedDict

from utils.config import ensure_plugin_config_from_template


class TranslateAIConfig(TypedDict):
    """translator 为 ai 时使用的配置。其他翻译工具不读这段。"""

    model: str
    """ai_config.json 里的类型名，例如 deepseek。"""
    prompt: str
    """发给模型的系统提示。每次翻译只附带这一段和一条原文。"""


class TranslateRuntimeConfig(TypedDict):
    """kmrp-translate 的运行时配置。"""

    translator: str
    """当前翻译工具：youdao、tencent、ai。"""
    ai: TranslateAIConfig
    """AI 翻译的模型和提示词。"""


class TranslateConfig:
    """读写翻译插件配置。文件不存在时按模板生成，每次读取都重新打开。"""

    __PLUGIN: Final[str] = "kmrp-translate"
    __FILENAME: Final[str] = "translate_config.json"
    __TEMPLATE: Final[Path] = Path(__file__).resolve().parent / "translate_config_template.json"

    @classmethod
    def load(cls) -> TranslateRuntimeConfig:
        """
        读取当前翻译工具，以及 AI 使用的模型和提示词。

        :return: translator 为 youdao、tencent 或 ai；ai 仅在 translator 为 ai 时使用
        """
        path = ensure_plugin_config_from_template(cls.__PLUGIN, cls.__FILENAME, cls.__TEMPLATE)
        data = json.loads(path.read_text(encoding="utf-8"))
        ai = data["ai"]
        return {
            "translator": data["translator"],
            "ai": {
                "model": ai["model"],
                "prompt": ai["prompt"],
            },
        }
