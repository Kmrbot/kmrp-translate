from typing import Union
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.log import logger
from protocol_adapter.adapter_type import AdapterMessage, AdapterPrivateMessageEvent
from .translator.translator_base import TranslatorBase
from .translator.tencent_translator import TencentTranslator
from .translator.youdao_translator import YouDaoTranslator
from .translator_type import TranslatorType


def get_translator(translator_type: TranslatorType) -> TranslatorBase:
    """ 获取翻译器 """
    if translator_type == TranslatorType.TRANSLATOR_TENCENT:
        return TencentTranslator()
    elif translator_type == TranslatorType.TRANSLATOR_YOUDAO:
        return YouDaoTranslator()
    else:
        logger.error(f"Invalid translator type ! type = {translator_type}")
        return TranslatorBase()


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
