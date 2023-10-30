import copy
import re
from database.interface.db_impl_interface import DBImplInterface
from database.db_manager import DBManager


# B站翻译信息
class DBPluginsTranslateInfo(DBImplInterface):

    """
    key: {msg_type}_{msg_type_id}_{user_id}
    """
    _default_value = {
    }

    @classmethod
    def is_translate(cls, msg_type, msg_type_id, user_id):
        """ 是否已经添加过翻译 """
        key = cls.generate_key(msg_type, msg_type_id, user_id)
        data = cls.get_data_by_key(key)
        return data is not None

    @classmethod
    def add_translate(cls, msg_type, msg_type_id, user_id):
        """ 添加翻译 """
        key = cls.generate_key(msg_type, msg_type_id, user_id)
        data = copy.deepcopy(cls._default_value)
        cls.set_data(key, data)

    @classmethod
    def del_translate(cls, msg_type, msg_type_id, user_id):
        """ 删除翻译 """
        key = cls.generate_key(msg_type, msg_type_id, user_id)
        cls.del_data(key)

    @classmethod
    def clear_translate_by_msg_type_id(cls, msg_type, msg_type_id):
        """ 根据msg_type和msg_type_id 清空翻译信息 """
        for key, data in copy.deepcopy(cls.get_data().items()):
            key_info = cls.analysis_key(key)
            if key_info["msg_type"] == msg_type and key_info["msg_type_id"] == msg_type_id:
                cls.del_data(key)

    @classmethod
    def get_all_translate_by_msg_type_id(cls, msg_type, msg_type_id):
        """ 根据msg_type和msg_type_id 获取翻译信息 """
        translate_info = []
        for key, data in cls.get_data().items():
            key_info = cls.analysis_key(key)
            if key_info["msg_type"] == msg_type and key_info["msg_type_id"] == msg_type_id:
                translate_info.append(key_info["user_id"])
        return translate_info

    @classmethod
    def db_key_name(cls, bot_id):
        # 公共的
        return f"{cls.__name__}_BOT_{bot_id}"

    @classmethod
    async def init(cls):
        """ 初始化 """
        pass

    @classmethod
    def generate_key(cls, msg_type, msg_type_id, user_id):
        """ 生成__data内存放的key """
        return f"{msg_type}_{msg_type_id}_{user_id}"

    @classmethod
    def analysis_key(cls, key):
        """ 解析generate_key生成的key """
        regex_groups = re.match("([a-zA-Z]*)_([0-9]*)_([0-9]*)", key).groups()
        if regex_groups is not None:
            return {
                "msg_type": regex_groups[0],
                "msg_type_id": int(regex_groups[1]),
                "user_id": int(regex_groups[2])
            }


DBManager.add_db(DBPluginsTranslateInfo)
