from nonebot import on_command
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.rule import to_me
from nonebot.params import ArgPlainText
from plugins.common_plugins_function import permission_only_me
from .db.translator_db_utils import TranslatorDBUtils
from .translate_function import translator_only_group, get_user_id

add_translate = on_command("添加翻译",
                           rule=to_me(),
                           priority=5)
add_translate.__doc__ = """添加翻译"""
add_translate.__help_type__ = None
add_translate.handle()(permission_only_me)
add_translate.handle()(translator_only_group)
add_translate.handle()(get_user_id)


@add_translate.handle()
async def _(event: GroupMessageEvent,
            target_user_id: str = ArgPlainText("target_user_id")):
    if await TranslatorDBUtils.get_translator_data(
        type=event.message_type,
        type_id=event.group_id,
        target_user_id=target_user_id,
    ) is not None:
        await add_translate.finish("已经添加过该用户的翻译功能")
    else:
        await TranslatorDBUtils.add_translator_data(
            type=event.message_type,
            type_id=event.group_id,
            target_user_id=target_user_id,
        )
        await add_translate.finish(f"已添加QQ {target_user_id} 的自动翻译功能")
