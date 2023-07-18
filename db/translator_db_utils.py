import os
from pathlib import Path
from typing import List
from nonebot import get_driver
from tortoise import Tortoise
from tortoise.connection import connections
from plugins.common_plugins_function import get_plugin_db_path
from .translator_db import TranslatorData


class TranslatorDBUtils:

    @classmethod
    async def init(cls):
        plugin_name = os.path.split(Path(os.path.dirname(os.path.dirname(__file__))))[1]
        config = {
            "connections": {
                "translator_data_conn": f"sqlite://{get_plugin_db_path('translator_data.sqlite3')}"
            },
            "apps": {
                "kmr_bot_app": {
                    "models": [f"plugins.{plugin_name}.db.translator_db"],
                    "default_connection": "translator_data_conn",
                }
            }
        }

        await Tortoise.init(config)
        await Tortoise.generate_schemas()

    @classmethod
    async def get_translator_data_list(cls, **kwargs) -> List[TranslatorData]:
        """ 获取翻译数据信息 """
        return await TranslatorData.get(**kwargs)

    @classmethod
    async def get_translator_data(cls, **kwargs):
        """ 获取翻译数据信息 """
        return await TranslatorData.get(**kwargs).first()

    @classmethod
    async def add_translator_data(cls, **kwargs):
        """ 添加翻译数据信息 """
        if not await cls.get_translator_data(**kwargs):
            await TranslatorData.add(
                type=kwargs["type"],
                type_id=kwargs["type_id"],
                target_user_id=kwargs["target_user_id"])

    @classmethod
    async def del_translator_data(cls, **kwargs):
        """ 删除翻译数据信息 """
        return await TranslatorData.delete(**kwargs)

get_driver().on_startup(TranslatorDBUtils.init)
# get_driver().on_shutdown(connections.close_all)
