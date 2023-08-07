import uuid
import requests
import hashlib
import json
import time
from .translator_base import TranslatorBase
from .translator_config import get_youdao_translator_config
from .tencent_language_adjust import language_adjust
from ..translator_type import TranslatorType


def encrypt(sign_str):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(sign_str.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def do_request(url, data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(url, data=data, headers=headers)


class YouDaoTranslator(TranslatorBase):
    """ 有道翻译 """
    def translate(self):
        youdao_translator_config = get_youdao_translator_config()
        url = youdao_translator_config.get("url")
        app_key = youdao_translator_config.get("app_key")
        app_secret = youdao_translator_config.get("app_secret")

        query_str = ""
        for i in range(len(super()._src_text)):
            query_str += super()._src_text[i]
            if i != 0:
                query_str += "\n"

        source_language, target_language = language_adjust(super()._src_text, TranslatorType.TRANSLATOR_YOUDAO)

        cur_time = str(int(time.time()))
        salt = str(uuid.uuid1())
        data = {
            "from": source_language,
            "to": target_language,
            "signType": "v3",
            "curtime": cur_time,
            "appKey": app_key,
            "q": query_str,
            "salt": salt,
            "sign": encrypt(app_key + truncate(query_str) + salt + cur_time + app_secret),
            "vocabId": "DEB868CEED0847B09FD4F931576234E0"
        }
        response = do_request(url, data)
        rsp_json = json.loads(response.text)

        super().reset()   # 清理

        # 返回的是一个带回车的字符串 将其转换成数组
        ret = []
        translation_str = rsp_json["translation"][0]
        start_pos = 0
        enter_pos = translation_str.find("\n", start_pos)
        while enter_pos != -1:
            sub_str = translation_str[start_pos:enter_pos]
            if len(sub_str) != 0:
                ret.append(sub_str)
            start_pos = enter_pos + 1
            enter_pos = translation_str.find("\n", start_pos)
        ret.append(translation_str[start_pos:])
        return ret
