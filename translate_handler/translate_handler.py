from nonebot import on_message
from protocol_adapter.adapter_type import AdapterBot, AdapterGroupMessageEvent
from protocol_adapter.protocol_adapter import ProtocolAdapter
from utils.permission import white_list_handle
from ..translate_function import get_translate_result, get_translator, translate_text_preprocess
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


@translate_handler.handle()
async def _(
        event: AdapterGroupMessageEvent
):
    # 获取当前的翻译器
    translator = get_translator()
    translator.reset()  # 清理
    # 获取所有文本进行翻译
    for text in ProtocolAdapter.get_text(event):
        text = translate_text_preprocess(text)
        if len(text) != 0 and text != " ":
            translator.add_text(str(text))
    translate_msg = await get_translate_result(translator)
    if translate_msg is None or translate_msg == "=":
        await translate_handler.finish()
    else:
        msg = ProtocolAdapter.MS.reply(event) + ProtocolAdapter.MS.text(f"翻译:\n{translate_msg}")
        await translate_handler.finish(msg)
