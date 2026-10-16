import json
import re
import emoji
from pathlib import Path
from typing import Union
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.log import logger
from protocol_adapter.adapter_type import AdapterMessage, AdapterPrivateMessageEvent, AdapterGroupMessageEvent
from protocol_adapter.protocol_adapter import ProtocolAdapter
from utils.config import ensure_plugin_config_from_template
from .translator.translator_base import TranslatorBase
from .translator.tencent_translator import TencentTranslator
from .translator.youdao_translator import YouDaoTranslator
from .translator_type import TranslatorType

__SHIELD_INFO_TEMPLATE_PATH = Path(__file__).resolve().parent / "shield_info" / "shield_info_template.json"


def get_translator(translator_type: TranslatorType) -> TranslatorBase:
    """ 获取翻译器 """
    if translator_type == TranslatorType.TRANSLATOR_TENCENT:
        return TencentTranslator()
    elif translator_type == TranslatorType.TRANSLATOR_YOUDAO:
        return YouDaoTranslator()
    else:
        logger.error(f"Invalid translator type ! type = {translator_type}")
        return TranslatorBase()


def translate_text_preprocess(text):
    """ 翻译字符预处理 """
    text = text.lstrip()
    # 过滤url
    # 过滤emoji
    text = emoji.replace_emoji(text, "")
    # 过滤零宽字符
    zero_width_character_regex = r"[" \
                                 u"\U0000200a" \
                                 u"\U0000200b" \
                                 r"]"
    text = re.sub(zero_width_character_regex, "", text)

    # 拿所有屏蔽信息
    shield_path = ensure_plugin_config_from_template(
        "kmrp-translate",
        "shield_info.json",
        __SHIELD_INFO_TEMPLATE_PATH,
    )
    with open(shield_path, encoding="utf-8") as f:
        try:
            shield_info = json.load(f)
            for single_shield_info in shield_info["shield_words"]:
                if re.sub(single_shield_info["reg"], "", text) != text:
                    match single_shield_info["shield_type"]:
                        case "SHIELD_TYPE_SKIP":
                            return ""
                        case _:
                            logger.error(f"Invalid shield_type! shield_type = {single_shield_info['shield_type']}")
                            return ""
        except Exception as e:
            logger.error(f"check shield info exception {e} !")
    return text


async def get_translate_result(translator: TranslatorBase) -> str | None:
    if translator.get_all_string_length() == 0:
        # 没有内容可以翻译
        return None
    else:
        target_str_list = translator.translate()
        if target_str_list is None:
            logger.error("translate_handler error ! target_str_list is None !")
            return None

        translate_str = ""
        for i in range(len(target_str_list)):
            if i != 0:
                # 如果已经有字符串了 就加一个回车
                translate_str += "\n"
            translate_str += target_str_list[i]
        return translate_str


async def get_user_id(
    matcher: Matcher,
    command_arg: AdapterMessage = CommandArg(),
):
    target_user_id = command_arg.extract_plain_text().strip()
    if target_user_id and target_user_id.isdecimal():
        matcher.set_arg("target_user_id", command_arg)
    else:
        await matcher.finish("UserID必须为纯数字")


async def translator_only_group(
        matcher: Matcher,
        event: Union[AdapterPrivateMessageEvent]):
    await matcher.finish("只有群里才可以使用翻译功能")
