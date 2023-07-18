from tortoise.fields.data import CharField, IntField
from plugins.db_base_model import PluginsDBBaseModel


# 翻译
class TranslatorData(PluginsDBBaseModel):
    type = CharField(max_length=16)                 # 类型 群,私聊...
    type_id = IntField()                            # 类型对应的ID
    target_user_id = IntField()                     # 翻译目标的QQ号
