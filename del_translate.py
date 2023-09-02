from nonebot import on_command
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.rule import to_me
from nonebot.params import ArgPlainText
from plugins.common_plugins_function import permission_only_me, while_list_handle
from .db.translator_db_utils import TranslatorDBUtils
from .translate_function import translator_only_group, get_user_id

del_translate = on_command("删除翻译",
                           rule=to_me(),
                           priority=5)
del_translate.__doc__ = """删除翻译"""
del_translate.__help_type__ = None
del_translate.handle()(while_list_handle("translate"))
del_translate.handle()(permission_only_me)
del_translate.handle()(translator_only_group)
del_translate.handle()(get_user_id)


@del_translate.handle()
async def _(event: GroupMessageEvent,
            target_user_id: str = ArgPlainText("target_user_id")):
    if await TranslatorDBUtils.get_translator_data(
        type=event.message_type,
        type_id=event.group_id,
        target_user_id=target_user_id,
    ) is None:
        await del_translate.finish("尚未添加过该用户的翻译功能")
    else:
        await TranslatorDBUtils.del_translator_data(
            type=event.message_type,
            type_id=event.group_id,
            target_user_id=target_user_id,
        )
        await del_translate.finish(f"已删除QQ {target_user_id} 的自动翻译功能")
