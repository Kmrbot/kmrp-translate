from typing import Type, Union
from enum import Enum
from nonebot.adapters.onebot.v11.event import PrivateMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import (
    Message,
)
from .translator.translator_base import TranslatorBase
from .translator.tencent_translator import TencentTranslator


class TranslatorType(Enum):
    """ 翻译器类型 """
    TRANSLATOR_NULL = 0,
    TRANSLATOR_TENCENT = 1,     # 腾讯翻译


def get_translator(translator_type: TranslatorType) -> TranslatorBase:
    """ 获取翻译器 """
    if translator_type == TranslatorType.TRANSLATOR_TENCENT:
        return TencentTranslator()
    else:
        logger.error(f"Invalid translator type ! type = {translator_type}")
        return TranslatorBase()


def get_user_id(
    matcher: Matcher,
    command_arg: Message = CommandArg(),
):
    target_user_id = command_arg.extract_plain_text().strip()
    if target_user_id and target_user_id.isdecimal():
        matcher.set_arg("target_user_id", command_arg)
    else:
        matcher.finish("UserID必须为纯数字")


def translator_only_group(
        matcher: Matcher,
        event: Union[PrivateMessageEvent, GuildMessageEvent]):
    matcher.finish("只有群里才可以使用翻译功能")
