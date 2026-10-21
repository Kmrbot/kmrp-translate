import json
from pathlib import Path
from typing import Final, TypedDict

from utils.config import ensure_plugin_config_from_template


class TranslateAIConfig(TypedDict):
    """translator 为 ai 时使用的配置。其他翻译工具不读这段。"""

    model: str
    """ai_config.json 里的类型名，例如 deepseek。"""
    prompt: str
    """发给模型的系统提示。配置文件里按行写成数组，读取时用换行拼成这一段。"""


class TranslateTencentConfig(TypedDict):
    """腾讯翻译的密钥。有道的语种判断也读这段。"""

    secret_id: str
    """腾讯云 SecretId。"""
    secret_key: str
    """腾讯云 SecretKey。"""


class TranslateYoudaoConfig(TypedDict):
    """有道翻译的接口和密钥。"""

    url: str
    """有道开放接口地址。"""
    app_key: str
    """有道应用 ID。"""
    app_secret: str
    """有道应用密钥。"""


class TranslateRuntimeConfig(TypedDict):
    """kmrp-translate 的运行时配置。"""

    translator: str
    """当前翻译工具：youdao、tencent、ai。"""
    ai: TranslateAIConfig
    """AI 翻译的模型和提示词。"""
    tencent: TranslateTencentConfig
    """腾讯翻译密钥。"""
    youdao: TranslateYoudaoConfig
    """有道翻译接口和密钥。"""


class TranslateConfig:
    """读写翻译插件配置。文件不存在时按模板生成，每次读取都重新打开。"""

    __PLUGIN: Final[str] = "kmrp-translate"
    __FILENAME: Final[str] = "translate_config.json"
    __TEMPLATE: Final[Path] = Path(__file__).resolve().parent / "translate_config_template.json"

    @classmethod
    def load(cls) -> TranslateRuntimeConfig:
        """
        读取当前翻译工具、AI 提示词，以及腾讯、有道的接口配置。

        :return: translator 为 youdao、tencent 或 ai
        """
        path = ensure_plugin_config_from_template(cls.__PLUGIN, cls.__FILENAME, cls.__TEMPLATE)
        data = json.loads(path.read_text(encoding="utf-8"))
        ai = data["ai"]
        tencent = data["tencent"]
        youdao = data["youdao"]
        prompt = ai["prompt"]
        if isinstance(prompt, list):
            prompt = "\n".join(prompt)
        return {
            "translator": data["translator"],
            "ai": {
                "model": ai["model"],
                "prompt": prompt,
            },
            "tencent": {
                "secret_id": tencent["secret_id"],
                "secret_key": tencent["secret_key"],
            },
            "youdao": {
                "url": youdao["url"],
                "app_key": youdao["app_key"],
                "app_secret": youdao["app_secret"],
            },
        }
