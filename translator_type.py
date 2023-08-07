from enum import Enum


class TranslatorType(Enum):
    """ 翻译器类型 """
    TRANSLATOR_NULL = 0,
    TRANSLATOR_TENCENT = 1,     # 腾讯翻译
    TRANSLATOR_YOUDAO = 2,      # 有道翻译
