from nonebot import on_command
from protocol_adapter.protocol_adapter import ProtocolAdapter
from protocol_adapter.adapter_type import AdapterGroupMessageEvent
from nonebot.rule import to_me
from utils.permission import only_me, white_list_handle
from .database.translate_info import DBPluginsTranslateInfo
from .translate_function import translator_only_group


clear_translate = on_command("清空翻译",
                             rule=to_me(),
                             priority=5)
clear_translate.__doc__ = """清空翻译"""
clear_translate.__help_type__ = None
clear_translate.handle()(white_list_handle("translate"))
clear_translate.handle()(translator_only_group)
clear_translate.handle()(only_me)


@clear_translate.handle()
async def _(event: AdapterGroupMessageEvent):
    msg_type = ProtocolAdapter.get_msg_type(event)
    msg_type_id = ProtocolAdapter.get_msg_type_id(event)
    DBPluginsTranslateInfo.clear_translate_by_msg_type_id(msg_type, msg_type_id)
    await clear_translate.finish(f"已删除该群组的所有的自动翻译")
