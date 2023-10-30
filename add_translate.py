from nonebot import on_command
from protocol_adapter.protocol_adapter import ProtocolAdapter
from protocol_adapter.adapter_type import AdapterGroupMessageEvent
from nonebot.rule import to_me
from nonebot.params import ArgPlainText
from plugins.common_plugins_function import white_list_handle
from .database.translate_info import DBPluginsTranslateInfo
from .translate_function import translator_only_group, get_user_id
from utils.permission import only_me

add_translate = on_command("添加翻译",
                           rule=to_me(),
                           priority=5,
                           block=True)
add_translate.__doc__ = """添加翻译"""
add_translate.__help_type__ = None
add_translate.handle()(white_list_handle("translate"))
add_translate.handle()(only_me)
add_translate.handle()(translator_only_group)
add_translate.handle()(get_user_id)


@add_translate.handle()
async def _(event: AdapterGroupMessageEvent,
            target_user_id: str = ArgPlainText("target_user_id")):
    msg_type = ProtocolAdapter.get_msg_type(event)
    msg_type_id = ProtocolAdapter.get_msg_type_id(event)
    if DBPluginsTranslateInfo.is_translate(msg_type, msg_type_id, target_user_id):
        await add_translate.finish("已经添加过该用户的翻译功能")
    else:
        DBPluginsTranslateInfo.add_translate(msg_type, msg_type_id, target_user_id)
        await add_translate.finish(f"已添加QQ {target_user_id} 的自动翻译功能")
