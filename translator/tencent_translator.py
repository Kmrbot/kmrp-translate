import json
from nonebot.log import logger
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import tmt_client, models
from .translator_base import TranslatorBase
from .translator_config import get_tencent_translator_config
from .tencent_language_adjust import language_adjust
from ..translator_type import TranslatorType


class TencentTranslator(TranslatorBase):
    """ 腾讯翻译 """
    def translate(self):
        try:
            tencent_translator_config = get_tencent_translator_config()
            secret_id = tencent_translator_config.get("secret_id")
            secret_key = tencent_translator_config.get("secret_key")

            cred = credential.Credential(secret_id, secret_key)
            http_profile = HttpProfile()
            http_profile.endpoint = "tmt.tencentcloudapi.com"

            client_profile = ClientProfile()
            client_profile.http_profile = http_profile
            client = tmt_client.TmtClient(cred, "ap-guangzhou", client_profile)

            source_language, target_language = language_adjust(super()._src_text, TranslatorType.TRANSLATOR_TENCENT)

            req = models.TextTranslateBatchRequest()
            params = {
                "Source": source_language,
                "Target": target_language,
                "ProjectId": 0,
                "SourceTextList": super()._src_text
            }
            req.from_json_string(json.dumps(params))

            resp = client.TextTranslateBatch(req)
            resp_json = json.loads(resp.to_json_string())

            super().reset()   # 清理
            return resp_json["TargetTextList"]
        except TencentCloudSDKException as err:
            logger.error(f"TencentTranslator fail ! err = {err}")
