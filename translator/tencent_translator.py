import json
from nonebot.log import logger
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import tmt_client, models
from .translator_base import TranslatorBase
from .tencent_language_adjust import language_adjust
from ..translate_config import TranslateTencentConfig
from ..translator_type import TranslatorType


class TencentTranslator(TranslatorBase):
    """ 腾讯翻译 """

    def __init__(self, config: TranslateTencentConfig) -> None:
        """
        :param config: translate_config.json 里 tencent 段
        """
        self.__secret_id: str = config["secret_id"]
        self.__secret_key: str = config["secret_key"]

    async def translate(self):
        try:
            cred = credential.Credential(self.__secret_id, self.__secret_key)
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
