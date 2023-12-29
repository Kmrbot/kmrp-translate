from nonebot import on_command
from protocol_adapter.protocol_adapter import ProtocolAdapter
from protocol_adapter.adapter_type import AdapterGroupMessageEvent
from nonebot.rule import to_me
from nonebot.params import ArgPlainText
from utils.permission import only_me, white_list_handle
from .database.translate_info import DBPluginsTranslateInfo
from .translate_function import translator_only_group, get_user_id


del_translate = on_command("删除翻译",
                           rule=to_me(),
                           priority=5)
del_translate.__doc__ = """删除翻译"""
del_translate.__help_type__ = None
del_translate.handle()(white_list_handle("translate"))
del_translate.handle()(translator_only_group)
del_translate.handle()(get_user_id)
del_translate.handle()(only_me)


@del_translate.handle()
async def _(event: AdapterGroupMessageEvent,
            target_user_id: str = ArgPlainText("target_user_id")):
    msg_type = ProtocolAdapter.get_msg_type(event)
    msg_type_id = ProtocolAdapter.get_msg_type_id(event)
    if not DBPluginsTranslateInfo.is_translate(msg_type, msg_type_id, target_user_id):
        await del_translate.finish("尚未添加过该用户的翻译功能")
    else:
        DBPluginsTranslateInfo.del_translate(msg_type, msg_type_id, target_user_id)
        await del_translate.finish(f"已删除QQ {target_user_id} 的自动翻译功能")
