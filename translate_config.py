import json
from pathlib import Path
from typing import Any, Final, NotRequired, TypedDict

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
    """kmrp-translate 的运行时配置。某种翻译被删掉后，对应字段不出现。"""

    translator: str
    """当前翻译工具：youdao、tencent、ai。该项已删除时为空字符串。"""
    ai: NotRequired[TranslateAIConfig]
    """AI 翻译的模型和提示词。未添加时没有这个字段。"""
    tencent: NotRequired[TranslateTencentConfig]
    """腾讯翻译密钥。未添加时没有这个字段。"""
    youdao: NotRequired[TranslateYoudaoConfig]
    """有道翻译接口和密钥。未添加时没有这个字段。"""


class TranslateConfig:
    """读写翻译插件配置。文件不存在时按模板生成，每次读取都重新打开。"""

    __PLUGIN: Final[str] = "kmrp-translate"
    __FILENAME: Final[str] = "translate_config.json"
    __TEMPLATE: Final[Path] = Path(__file__).resolve().parent / "translate_config_template.json"

    __KINDS: Final[tuple[str, ...]] = ("ai", "tencent", "youdao")

    @classmethod
    def load(cls) -> TranslateRuntimeConfig:
        """
        读取当前翻译工具，以及还留在文件里的各段配置。

        :return: translator 为 youdao、tencent、ai 或空字符串。已删除的段不出现
        """
        data = cls.__read_raw()
        result: TranslateRuntimeConfig = {"translator": data["translator"]}
        if "ai" in data:
            ai = data["ai"]
            prompt = ai["prompt"]
            if isinstance(prompt, list):
                prompt = "\n".join(prompt)
            result["ai"] = {
                "model": ai["model"],
                "prompt": prompt,
            }
        if "tencent" in data:
            tencent = data["tencent"]
            result["tencent"] = {
                "secret_id": tencent["secret_id"],
                "secret_key": tencent["secret_key"],
            }
        if "youdao" in data:
            youdao = data["youdao"]
            result["youdao"] = {
                "url": youdao["url"],
                "app_key": youdao["app_key"],
                "app_secret": youdao["app_secret"],
            }
        return result

    @classmethod
    def save_current(cls, kind: str) -> None:
        """
        把当前使用的翻译改成 kind 并写回文件。

        :param kind: youdao、tencent 或 ai
        :return: 无
        """
        data = cls.__read_raw()
        data["translator"] = kind
        cls.__write_raw(data)

    @classmethod
    def save_ai(cls, model: str, prompt: str) -> None:
        """
        写入 AI 翻译的模型和提示词。多行提示词按行存成数组。

        :param model: ai_config.json 里的类型名
        :param prompt: 发给模型的系统提示
        :return: 无
        """
        data = cls.__read_raw()
        data["ai"] = {
            "model": model,
            "prompt": cls.__store_prompt(prompt),
        }
        cls.__write_raw(data)

    @classmethod
    def save_tencent(cls, secret_id: str, secret_key: str) -> None:
        """
        写入腾讯翻译密钥。

        :param secret_id: 腾讯云 SecretId
        :param secret_key: 腾讯云 SecretKey
        :return: 无
        """
        data = cls.__read_raw()
        data["tencent"] = {
            "secret_id": secret_id,
            "secret_key": secret_key,
        }
        cls.__write_raw(data)

    @classmethod
    def save_youdao(cls, url: str, app_key: str, app_secret: str) -> None:
        """
        写入有道翻译的接口和密钥。

        :param url: 有道开放接口地址
        :param app_key: 有道应用 ID
        :param app_secret: 有道应用密钥
        :return: 无
        """
        data = cls.__read_raw()
        data["youdao"] = {
            "url": url,
            "app_key": app_key,
            "app_secret": app_secret,
        }
        cls.__write_raw(data)

    @classmethod
    def remove(cls, kind: str) -> str:
        """
        删掉一种翻译。如果删的是当前使用的，改成剩下的第一种。

        :param kind: ai、tencent 或 youdao
        :return: 当前翻译因此被换掉时，返回新的种类；没换，或删光之后，为空字符串
        """
        data = cls.__read_raw()
        del data[kind]
        switched = ""
        if data["translator"] == kind:
            data["translator"] = ""
            for name in cls.__KINDS:
                if name in data:
                    data["translator"] = name
                    switched = name
                    break
        cls.__write_raw(data)
        return switched

    @classmethod
    def __path(cls) -> Path:
        """
        返回运行时 translate_config.json 的路径。文件不存在时按模板生成。

        :return: 配置文件路径
        """
        return ensure_plugin_config_from_template(cls.__PLUGIN, cls.__FILENAME, cls.__TEMPLATE)

    @classmethod
    def __read_raw(cls) -> dict[str, Any]:
        """
        读出配置文件原文。

        :return: JSON 对象
        """
        return json.loads(cls.__path().read_text(encoding="utf-8"))

    @classmethod
    def __write_raw(cls, data: dict[str, Any]) -> None:
        """
        把配置对象写回文件。

        :param data: 完整的配置对象
        :return: 无
        """
        cls.__path().write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @classmethod
    def __store_prompt(cls, prompt: str) -> str | list[str]:
        """
        提示词写回文件的形状。多行按行拆成数组，和模板一致。

        :param prompt: 页面上的整段提示词
        :return: 单行时为字符串，多行时为每一行
        """
        text = prompt.replace("\r\n", "\n").replace("\r", "\n")
        if "\n" in text:
            return text.split("\n")
        return text
