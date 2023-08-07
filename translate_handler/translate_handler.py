import re
from emoji import is_emoji
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot import on_message
from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import (
    Message,
)
from nonebot.log import logger
from ..translate_function import TranslatorType, get_translator
from ..db.translator_db_utils import TranslatorDBUtils

translate_handler = on_message(priority=5)


async def is_translate_user(
        matcher: Matcher,
        event: Event):
    # 看当前群和说话人是不是对应的
    if not isinstance(event, GroupMessageEvent):
        # 不处理非群组会话
        await matcher.finish()
    if await TranslatorDBUtils.get_translator_data(
        type=event.message_type,
        type_id=event.group_id,
        target_user_id=event.user_id,
    ) is not None:
        # 可以有后续的处理
        # 如果发消息的和机器人是同一个号 就断掉
        if event.self_id == event.user_id:
            # 机器人是不会处理自己给自己发的消息的好像
            logger.error("is_translate_user fail")
            await matcher.finish()
        else:
            return
    else:
        await matcher.finish()

translate_handler.handle()(is_translate_user)


def translate_text_preprocess(text):
    """ 翻译字符预处理 """
    # 1. 过滤url
    text = re.sub("(http|www)[^ ]* *", " ", text)   # 正则匹配去掉网页链接
    # 2. 去除emoji
    for i in range(len(text)):
        c = text[i]
        if is_emoji(c):
            text = text[:i] + "," + text[i + 1:]
    return text


@translate_handler.handle()
async def _(
        event: GroupMessageEvent
):
    # 获取当前的翻译器
    translator = get_translator(TranslatorType.TRANSLATOR_YOUDAO)

    # 获取所有文本进行翻译
    for i in range(len(event.message)):
        single_msg = event.message[i]
        if single_msg.type == "text":
            text = single_msg.data.get("text", "")
            text = translate_text_preprocess(text)
            if len(text) != 0 and text != " ":
                translator.add_text(str(text))
    if translator.get_all_string_length() == 0:
        # 没有内容可以翻译
        await translate_handler.finish()
    else:
        target_str_list = translator.translate()
        if target_str_list is None:
            logger.error("translate_handler error ! target_str_list is None !")
            await translate_handler.finish()

        translate_msg = Message("翻译:\n")
        translate_str = ""
        for i in range(len(target_str_list)):
            if i != 0:
                # 如果已经有字符串了 就加一个回车
                translate_str += "\n"
            translate_str += target_str_list[i]
        translate_msg += Message(translate_str)
        msg = Message(f"[CQ:reply,id={event.message_id}]") + translate_msg
        await translate_handler.finish(msg)
