import re

import emoji
from nonebot import on_message
from protocol_adapter.adapter_type import AdapterBot, AdapterGroupMessageEvent
from protocol_adapter.protocol_adapter import ProtocolAdapter
from utils.permission import white_list_handle
from nonebot.log import logger
from ..translate_function import TranslatorType, get_translator
from ..database.translate_info import DBPluginsTranslateInfo


def is_translate_user(
        bot: AdapterBot,
        event: AdapterGroupMessageEvent):
    if ProtocolAdapter.get_bot_id(bot) == ProtocolAdapter.get_user_id(event):
        # 如果发消息的和机器人是同一个号 就断掉
        # 机器人是不会处理自己给自己发的消息的好像
        return False
    # 看当前群和说话人是不是对应的
    msg_type = ProtocolAdapter.get_msg_type(event)
    msg_type_id = ProtocolAdapter.get_msg_type_id(event)
    return DBPluginsTranslateInfo.is_translate(msg_type, msg_type_id, ProtocolAdapter.get_user_id(event))


translate_handler = on_message(priority=10, rule=is_translate_user)  # 调低相应级别

translate_handler.handle()(white_list_handle("translate"))


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
    if re.sub(r"(https?://|\w+\.\w+\.\w+)[^ ]* *", "", text) != text:
        # 如果网页链接出现了url过滤 则直接返回空
        return ""
    return text


@translate_handler.handle()
async def _(
        bot: AdapterBot,
        event: AdapterGroupMessageEvent
):
    # 获取当前的翻译器
    translator = get_translator(TranslatorType.TRANSLATOR_YOUDAO)

    # 获取所有文本进行翻译
    for text in ProtocolAdapter.get_text(event):
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

        translate_msg = ProtocolAdapter.MS.text("翻译:\n")
        translate_str = ""
        for i in range(len(target_str_list)):
            if i != 0:
                # 如果已经有字符串了 就加一个回车
                translate_str += "\n"
            translate_str += target_str_list[i]
        translate_msg += ProtocolAdapter.MS.text(translate_str)
        msg = ProtocolAdapter.MS.reply(event) + translate_msg
        await translate_handler.finish(msg)
