import re

from nonebot import on_command
from protocol_adapter.protocol_adapter import ProtocolAdapter
from protocol_adapter.adapter_type import AdapterMessageEvent
from nonebot.log import logger
from nonebot.rule import to_me
from .translate_function import get_translate_result, get_translator, translate_text_preprocess
from utils.permission import white_list_handle

force_translate = on_command("机翻",
                             rule=to_me(),
                             priority=5,
                             block=True)
force_translate.__doc__ = """机翻"""
force_translate.__help_type__ = None
force_translate.handle()(white_list_handle("translate"))


@force_translate.handle()
async def _(event: AdapterMessageEvent):
    # 获取当前的翻译器
    translator = get_translator()
    translator.reset()  # 清理
    # 获取所有文本进行翻译 第一个机翻需要去除
    for text in ProtocolAdapter.get_text(event):
        if translator.get_all_string_length() == 0:
            regex_groups = re.match("机翻 *(.*)", text).groups()
            if len(regex_groups) == 1:
                text = regex_groups[0]
            else:
                logger.error("force_translate fail ! message begin is invalid !")
                await force_translate.finish()
            translator.add_text(text)

    translate_msg = await get_translate_result(translator)
    if translate_msg is None:
        await force_translate.finish(ProtocolAdapter.MS.reply(event) +
                                     ProtocolAdapter.MS.text("机翻：{无可机翻内容}"))
    if translate_msg == "=":
        await force_translate.finish()
    await force_translate.finish(ProtocolAdapter.MS.reply(event) +
                                 ProtocolAdapter.MS.text(f"机翻：{translate_msg}"))
