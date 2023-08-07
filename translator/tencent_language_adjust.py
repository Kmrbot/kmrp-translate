import json
from nonebot.log import logger
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import tmt_client, models
from .translator_config import get_tencent_translator_config
from ..translator_type import TranslatorType


def language_adjust(src_texts, translator_type):
    """ 腾讯语言判断 """
    source_language = "ja"
    target_language = "zh"
    if len(src_texts) != 0:
        tencent_translator_config = get_tencent_translator_config()
        secret_id = tencent_translator_config.get("secret_id")
        secret_key = tencent_translator_config.get("secret_key")

        cred = credential.Credential(secret_id, secret_key)
        http_profile = HttpProfile()
        http_profile.endpoint = "tmt.tencentcloudapi.com"

        client_profile = ClientProfile()
        client_profile.http_profile = http_profile
        client = tmt_client.TmtClient(cred, "ap-guangzhou", client_profile)

        req = models.LanguageDetectRequest()
        req.from_json_string(json.dumps({"Text": src_texts[0], "ProjectId": 0}))
        resp = client.LanguageDetect(req)
        resp_json = json.loads(resp.to_json_string())

        def convert_translate_type(tencent_translate_type, dst_translator_type):
            """ 将腾讯的语言类型转换至目标语言类型 """
            if dst_translator_type == TranslatorType.TRANSLATOR_TENCENT:
                return tencent_translate_type
            if tencent_translate_type == "zh":
                if dst_translator_type == TranslatorType.TRANSLATOR_YOUDAO:
                    return "zh-CHS"
            elif tencent_translate_type == "jp":
                if dst_translator_type == TranslatorType.TRANSLATOR_YOUDAO:
                    return "ja"
            logger.error(f"convert_translate_type fail ! tencent_translate_type = {tencent_translate_type}")
            return "zh"

        if resp_json["Lang"] == "zh":
            source_language = convert_translate_type("zh", translator_type)
            target_language = convert_translate_type("jp", translator_type)
    return source_language, target_language
