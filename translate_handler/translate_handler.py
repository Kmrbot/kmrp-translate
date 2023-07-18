from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot import on_message
from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import (
    Message,
)
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
            await matcher.finish()
        else:
            return
    else:
        await matcher.finish()

translate_handler.handle()(is_translate_user)


@translate_handler.handle()
async def _async(
        event: GroupMessageEvent
):
    # 获取当前的翻译器
    # 仅使用腾讯翻译
    translator = get_translator(TranslatorType.TRANSLATOR_TENCENT)
    translator.set_source_language("ja")
    translator.set_target_language("zh")

    # 获取所有文本进行翻译
    for single_msg in event.message:
        text = single_msg.data.get("text")
        if text is not None:
            translator.add_text(str(text))

    target_str_list = translator.translate()
    translate_str = ""
    for i in range(len(target_str_list)):
        if i != 0:
            # 如果已经有字符串了 就加一个回车
            translate_str += "\n"
        translate_str += target_str_list[i]
    msg = Message(f"[CQ:reply,id={event.message_id}]") + Message("翻译:\n" + translate_str)
    await translate_handler.finish(msg)
