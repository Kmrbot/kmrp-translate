from nonebot import on_command
from protocol_adapter.protocol_adapter import ProtocolAdapter
from protocol_adapter.adapter_type import AdapterGroupMessageEvent
from nonebot.rule import to_me
from nonebot.params import ArgPlainText
from plugins.common_plugins_function import white_list_handle
from .database.translate_info import DBPluginsTranslateInfo
from .translate_function import translator_only_group, get_user_id
from utils.permission import only_me

get_translate_list = on_command("翻译列表",
                                rule=to_me(),
                                priority=5)
get_translate_list.__doc__ = """翻译列表"""
get_translate_list.__help_type__ = None
get_translate_list.handle()(white_list_handle("translate"))
get_translate_list.handle()(only_me)
get_translate_list.handle()(translator_only_group)


@get_translate_list.handle()
async def _(event: AdapterGroupMessageEvent):
    msg_type = ProtocolAdapter.get_msg_type(event)
    msg_type_id = ProtocolAdapter.get_msg_type_id(event)
    ret_str = "当前正在翻译的成员QQ：\n"
    translator_datas = DBPluginsTranslateInfo.get_all_translate_by_msg_type_id(msg_type, msg_type_id)

    for translators in translator_datas:
        ret_str += f"{translators}\n"
    await get_translate_list.finish(ret_str)
