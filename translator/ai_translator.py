from typing import Final

from nonebot.log import logger

from utils.ai.chat import AIChat
from utils.config import AIConfig

from .translator_base import TranslatorBase


class AITranslator(TranslatorBase):
    """用已配置的一种 AI 做日中对译。每次请求只有系统提示和一条原文。"""

    __PROMPT: Final[str] = (
        "1.仅在回答中写出翻译的内容即可，不要掺杂任何其他信息；"
        "发的什么就翻译什么，有错误，模棱两可的词，也尽可能猜出意思。\n"
        "2.发现是日语就翻译成中文，发现是中文就翻译成日语。"
        "如果是纯汉字，则看一下是不是日语形式的纯汉字；"
        "如果翻译内容和原内容相同，则返回一个 = 即可。"
    )

    def __init__(self, model_name: str) -> None:
        """
        本次待译文本。每条消息单独一个实例，避免并发时互相覆盖。

        :param model_name: ai_config.json 里的类型名，例如 deepseek
        """
        self.__model_name: str = model_name
        self.__texts: list[str] = []

    def reset(self) -> None:
        """清空本次待译文本。"""
        self.__texts.clear()

    def add_text(self, text: str) -> None:
        """
        追加一段待译文本。

        :param text: 消息里的一段纯文本
        :return: 无
        """
        self.__texts.append(text)

    def get_all_string_length(self) -> int:
        """
        本次待译文本的总字数。

        :return: 各段长度之和
        """
        return sum(len(text) for text in self.__texts)

    async def translate(self) -> list[str] | None:
        """
        把本次文本合成一条发给模型。

        :return: 只有译文的列表。译文与原文相同或模型返回 = 时为 ["="]。请求失败时为 None
        """
        source = "\n".join(self.__texts).strip()
        if not source:
            return None
        item = AIConfig.list_items().get(self.__model_name)
        if item is None or not item["api_key"]:
            logger.error(f"AITranslator fail ! {self.__model_name} not configured")
            return None
        content, err = await AIChat(item).complete([
            {"role": "system", "content": self.__PROMPT},
            {"role": "user", "content": source},
        ])
        if err or not content.strip():
            logger.error(f"AITranslator fail ! err = {err or 'empty content'}")
            return None
        translated = content.strip()
        if translated == "=" or translated == source:
            return ["="]
        return [translated]
