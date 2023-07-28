from typing import List


class TranslatorBase:

    @classmethod
    def set_source_language(cls, source_language):
        TranslatorBase._source_language = source_language
        pass

    @classmethod
    def set_target_language(cls, target_language):
        TranslatorBase._target_language = target_language
        pass

    @classmethod
    def add_text(cls, text):
        TranslatorBase._src_text.append(text)

    @classmethod
    def get_all_text(cls):
        return TranslatorBase._src_text

    @classmethod
    def reset(cls):
        cls._source_language = ""
        cls._target_language = ""
        cls._src_text.clear()

    def translate(self) -> str:
        pass

    _source_language: str = ""
    _target_language: str = ""
    _src_text: List[str] = []
