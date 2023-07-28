import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import tmt_client, models
from .translator_config import get_tencent_translator_config


def language_adjust(src_texts):
    """ 腾讯语言判断 """
    # 如果只有一句就请求语言识别 否则自动强制ja->zh
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
        if resp_json["Lang"] == "zh":
            source_language = "zh"
            target_language = "ja"
    return source_language, target_language
