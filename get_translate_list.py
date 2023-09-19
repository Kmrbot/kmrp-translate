from nonebot import on_command
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.rule import to_me
from nonebot.params import ArgPlainText
from plugins.common_plugins_function import permission_only_me, white_list_handle
from .db.translator_db_utils import TranslatorDBUtils
from .translate_function import translator_only_group, get_user_id

get_translate_list = on_command("获取翻译列表",
                                rule=to_me(),
                                priority=5)
get_translate_list.__doc__ = """获取翻译列表"""
get_translate_list.__help_type__ = None
get_translate_list.handle()(white_list_handle("translate"))
get_translate_list.handle()(permission_only_me)
get_translate_list.handle()(translator_only_group)
get_translate_list.handle()(get_user_id)


@get_translate_list.handle()
async def _(event: GroupMessageEvent,
            target_user_id: str = ArgPlainText("target_user_id")):
    ret_str = "当前正在翻译的成员QQ：\n"
    translator_datas = await TranslatorDBUtils.get_translator_data_list(
        type=event.message_type,
        type_id=event.group_id,
        target_user_id=target_user_id)

    for translator_data in translator_datas:
        ret_str += f"{translator_data.target_user_id}\n"
    get_translate_list.finish(ret_str)
