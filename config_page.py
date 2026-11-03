"""翻译插件的控制台配置页。"""

from __future__ import annotations

from typing import Any, Callable, Final

from nicegui import ui

from kmrbot.web.i18n.i18n_manager import I18nManager
from kmrbot.web.panel.plugin_page import PluginPageRegistry
from utils.config import AIConfig

from .translate_config import TranslateConfig, TranslateRuntimeConfig


class TranslateConfigPage:
    """编辑当前翻译，以及 AI、腾讯、有道各自的配置。每种最多一块。"""

    __KINDS: Final[tuple[str, ...]] = ("ai", "tencent", "youdao")
    __TITLES: Final[dict[str, str]] = {
        "ai": "AI 翻译",
        "tencent": "腾讯翻译",
        "youdao": "有道翻译",
    }
    __YOUDAO_URL: Final[str] = "https://openapi.youdao.com/api"

    @classmethod
    def register(cls) -> None:
        """
        把配置页登记到控制台侧栏。插件加载时调用。

        :return: 无
        """
        PluginPageRegistry.register("translate", "config", "配置", cls.build)

    @classmethod
    def build(cls) -> None:
        """画出当前翻译和每种翻译自己的区域。"""
        with ui.column().classes("w-full gap-4"):
            ui.label(
                "上面是正在使用的翻译，切换后下一句就生效。"
                "下面每种一块：AI 填模型和提示词，腾讯和有道只填密钥。"
                "改完要点保存。添加和删除会直接写进配置。"
            ).classes("text-body2 text-grey-5")

            @ui.refreshable
            def render() -> None:
                cls.__render(render.refresh)

            render()

    @classmethod
    def __render(cls, refresh: Callable[[], None]) -> None:
        """
        按当前文件重画整页。

        :param refresh: 保存、添加或删除后重画
        :return: 无
        """
        config = TranslateConfig.load()
        present = [kind for kind in cls.__KINDS if kind in config]
        cls.__current_bar(config, present, refresh)
        for kind in present:
            cls.__section(kind, config, refresh)
        cls.__add_form(config, present, refresh)

    @classmethod
    def __current_bar(
        cls,
        config: TranslateRuntimeConfig,
        present: list[str],
        refresh: Callable[[], None],
    ) -> None:
        """
        画出当前使用的翻译。改下拉框会立刻写回。

        :param config: 刚读到的配置
        :param present: 文件里还在的种类，按页面顺序
        :param refresh: 切换成功后重画
        :return: 无
        """
        loaded = config["translator"]
        with ui.card().classes("w-full").props("flat bordered"):
            ui.label("当前使用的翻译").classes("text-subtitle1")
            if not present:
                ui.label("还没有翻译，在下面添加。").classes("text-body2 text-grey-5")
                return
            if loaded not in present:
                shown = loaded or "空"
                ui.label(f"配置里的当前项是 {shown}，下面没有这一项。").classes("text-body2 text-negative")
            kind_select = ui.select(
                {kind: cls.__TITLES[kind] for kind in present},
                value=loaded if loaded in present else None,
                label="翻译",
            ).props("outlined dense dark").classes("w-72")

            def on_current(event: Any) -> None:
                kind = str(event.value or "")
                if not kind or kind == loaded:
                    return
                TranslateConfig.save_current(kind)
                cls.__notify(f"当前翻译已改为{cls.__TITLES[kind]}")
                refresh()

            kind_select.on_value_change(on_current)

    @classmethod
    def __section(
        cls,
        kind: str,
        config: TranslateRuntimeConfig,
        refresh: Callable[[], None],
    ) -> None:
        """
        画出一种翻译的编辑区。AI 含模型和提示词，腾讯只有密钥，有道是接口地址和密钥。

        :param kind: ai、tencent 或 youdao
        :param config: 刚读到的配置
        :param refresh: 保存或删除后重画
        :return: 无
        """
        with ui.card().classes("w-full").props("flat bordered"):
            with ui.row().classes("w-full items-center justify-between"):
                with ui.row().classes("items-center gap-2"):
                    ui.label(cls.__TITLES[kind]).classes("text-subtitle1")
                    if kind == config["translator"]:
                        ui.label("使用中").classes("text-body2 text-primary")
                ui.button(
                    I18nManager.t("common.delete"),
                    icon="delete",
                    on_click=lambda kind=kind: cls.__ask_remove(kind, config, refresh),
                ).props("flat dense color=negative no-caps")

            if kind == "ai":
                ui.label("模型和提示词。提示词会整段作为系统提示发给模型。").classes("text-body2 text-grey-5")
                ai = config["ai"]
                model_field = cls.__model_field(ai["model"])
                prompt_field = cls.__prompt_field(ai["prompt"])

                def on_save_ai() -> None:
                    TranslateConfig.save_ai(
                        str(model_field.value or ""),
                        str(prompt_field.value or ""),
                    )
                    cls.__notify(I18nManager.t("config.saved"))
                    refresh()

                ui.button(
                    I18nManager.t("common.save"),
                    icon="save",
                    on_click=on_save_ai,
                ).props("color=primary unelevated no-caps")
                return

            if kind == "tencent":
                ui.label("SecretId 和 SecretKey。有道翻译判断原文语种时也读这组密钥。").classes(
                    "text-body2 text-grey-5"
                )
                tencent = config["tencent"]
                secret_id = cls.__text_field("SecretId", tencent["secret_id"])
                secret_key = cls.__text_field("SecretKey", tencent["secret_key"], secret=True)

                def on_save_tencent() -> None:
                    TranslateConfig.save_tencent(
                        str(secret_id.value or ""),
                        str(secret_key.value or ""),
                    )
                    cls.__notify(I18nManager.t("config.saved"))
                    refresh()

                ui.button(
                    I18nManager.t("common.save"),
                    icon="save",
                    on_click=on_save_tencent,
                ).props("color=primary unelevated no-caps")
                return

            ui.label("接口地址、App Key 和 App Secret。").classes("text-body2 text-grey-5")
            youdao = config["youdao"]
            url = cls.__text_field("接口地址", youdao["url"])
            app_key = cls.__text_field("App Key", youdao["app_key"])
            app_secret = cls.__text_field("App Secret", youdao["app_secret"], secret=True)

            def on_save_youdao() -> None:
                TranslateConfig.save_youdao(
                    str(url.value or ""),
                    str(app_key.value or ""),
                    str(app_secret.value or ""),
                )
                cls.__notify(I18nManager.t("config.saved"))
                refresh()

            ui.button(
                I18nManager.t("common.save"),
                icon="save",
                on_click=on_save_youdao,
            ).props("color=primary unelevated no-caps")

    @classmethod
    def __ask_remove(
        cls,
        kind: str,
        config: TranslateRuntimeConfig,
        refresh: Callable[[], None],
    ) -> None:
        """
        确认后删除一种翻译。删掉正在使用的那项时，改用剩下的第一种。

        :param kind: ai、tencent 或 youdao
        :param config: 打开这块时读到的配置
        :param refresh: 删除成功后重画
        :return: 无
        """
        from kmrbot.web.panel.nicegui_panel import _open_confirm_dialog

        title = cls.__TITLES[kind]
        message = f"删除{title}？这块里的内容会从配置里去掉。"
        if kind == "tencent":
            message += "有道翻译判断语种也要用这组密钥。"
        if kind == config["translator"]:
            others = [name for name in cls.__KINDS if name != kind and name in config]
            if others:
                message += "这是当前正在使用的翻译，删除后会改用剩下的第一种。"
            else:
                message += "这是当前正在使用的翻译，删除后就没有正在使用的翻译了。"

        def do_remove() -> None:
            switched = TranslateConfig.remove(kind)
            if switched:
                cls.__notify(f"已删除，当前翻译改为{cls.__TITLES[switched]}")
            else:
                cls.__notify("已删除")
            refresh()

        _open_confirm_dialog(
            I18nManager.t("common.delete_confirm_title"),
            message,
            do_remove,
            confirm_text=I18nManager.t("common.confirm"),
            cancel_text=I18nManager.t("common.cancel"),
        )

    @classmethod
    def __add_form(
        cls,
        config: TranslateRuntimeConfig,
        present: list[str],
        refresh: Callable[[], None],
    ) -> None:
        """
        画出添加区。三种都在时不再出现表单。

        :param config: 刚读到的配置
        :param present: 文件里还在的种类
        :param refresh: 添加成功后重画
        :return: 无
        """
        missing = [kind for kind in cls.__KINDS if kind not in present]
        with ui.card().classes("w-full").props("flat bordered"):
            ui.label("添加翻译").classes("text-subtitle1")
            if not missing:
                ui.label("AI、腾讯、有道都已添加。").classes("text-body2 text-grey-5")
                return
            kind_select = ui.select(
                {kind: cls.__TITLES[kind] for kind in missing},
                value=missing[0],
                label="类型",
            ).props("outlined dense dark").classes("w-72")
            holder: dict[str, Any] = {}

            @ui.refreshable
            def fields() -> None:
                cls.__add_fields(str(kind_select.value or missing[0]), holder)

            fields()
            kind_select.on_value_change(lambda _event: fields.refresh())

            def on_add() -> None:
                cls.__commit_add(str(kind_select.value or ""), holder, config, refresh)

            ui.button(
                I18nManager.t("common.add"),
                icon="add",
                on_click=on_add,
            ).props("color=primary unelevated no-caps")

    @classmethod
    def __add_fields(cls, kind: str, holder: dict[str, Any]) -> None:
        """
        按类型画出添加表单。控件放进 holder，点添加时读取。

        :param kind: ai、tencent 或 youdao
        :param holder: 调用方持有的控件表，本方法会先清空
        :return: 无
        """
        holder.clear()
        holder["kind"] = kind
        if kind == "ai":
            holder["model"] = cls.__model_field("")
            holder["prompt"] = cls.__prompt_field("")
            ui.label("模型和提示词。提示词会整段作为系统提示发给模型。").classes("text-body2 text-grey-5")
            return
        if kind == "tencent":
            holder["secret_id"] = cls.__text_field("SecretId", "")
            holder["secret_key"] = cls.__text_field("SecretKey", "", secret=True)
            ui.label("有道翻译判断原文语种时也读这组密钥。").classes("text-body2 text-grey-5")
            return
        holder["url"] = cls.__text_field("接口地址", cls.__YOUDAO_URL)
        holder["app_key"] = cls.__text_field("App Key", "")
        holder["app_secret"] = cls.__text_field("App Secret", "", secret=True)

    @classmethod
    def __commit_add(
        cls,
        kind: str,
        holder: dict[str, Any],
        config: TranslateRuntimeConfig,
        refresh: Callable[[], None],
    ) -> None:
        """
        把添加表单写进配置。当前项已经不在文件里时，把新加的设为当前。

        :param kind: 下拉框选中的类型
        :param holder: __add_fields 放进的控件
        :param config: 打开添加区时读到的配置
        :param refresh: 写完后重画
        :return: 无
        """
        if holder.get("kind") != kind:
            return
        if kind == "ai":
            TranslateConfig.save_ai(
                str(holder["model"].value or ""),
                str(holder["prompt"].value or ""),
            )
        elif kind == "tencent":
            TranslateConfig.save_tencent(
                str(holder["secret_id"].value or ""),
                str(holder["secret_key"].value or ""),
            )
        elif kind == "youdao":
            TranslateConfig.save_youdao(
                str(holder["url"].value or ""),
                str(holder["app_key"].value or ""),
                str(holder["app_secret"].value or ""),
            )
        else:
            return
        current = config["translator"]
        if current not in config:
            TranslateConfig.save_current(kind)
        cls.__notify("已添加")
        refresh()

    @classmethod
    def __model_field(cls, value: str) -> Any:
        """
        画出 AI 模型。AI 配置里有类型时用下拉，一项都没有时改成输入框。

        :param value: 当前模型类型名。下拉里没有时补进选项
        :return: 下拉框或输入框，读取 .value
        """
        options: dict[str, str] = {
            kind: item["title"] for kind, item in AIConfig.list_items().items()
        }
        if value and value not in options:
            options[value] = value
        if not options:
            return ui.input("模型", value=value).props("outlined dense dark").classes("w-full")
        selected = value if value in options else next(iter(options))
        return ui.select(
            options,
            value=selected,
            label="模型",
        ).props("outlined dense dark").classes("w-72")

    @classmethod
    def __prompt_field(cls, value: str) -> Any:
        """
        画出 AI 提示词。

        :param value: 已拼成一段的提示词
        :return: 多行输入框
        """
        return ui.textarea(
            "提示词",
            value=value,
        ).props('outlined dark input-style="min-height: 280px; height: 280px"').classes("w-full")

    @classmethod
    def __text_field(cls, label: str, value: str, *, secret: bool = False) -> Any:
        """
        画出一行密钥或地址。

        :param label: 输入框标题
        :param value: 当前内容
        :param secret: 为真时遮住内容，可切换显示
        :return: 输入框
        """
        return ui.input(
            label,
            value=value,
            password=secret,
            password_toggle_button=secret,
        ).props("outlined dense dark").classes("w-full")

    @classmethod
    def __notify(cls, message: str) -> None:
        """
        弹出一条成功提示。

        :param message: 提示文案
        :return: 无
        """
        from kmrbot.web.panel.nicegui_panel import _notify

        _notify(message, notify_type="positive")
