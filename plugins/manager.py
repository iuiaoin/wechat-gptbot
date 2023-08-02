import json
import re
import os
import importlib
from common.singleton import singleton
from config import conf
from utils.log import logger
from typing import Set
from dulwich import porcelain
from utils.package import install_file
from plugins.plugin import Plugin
from common.emitter import Emitter
from plugins.event import Event, EventType
from plugins.built_in import Cmd


@singleton
class PluginManager(Emitter):
    def __init__(self):
        super().__init__()
        self._plugins = {}
        self._configs = {}
        self.built_in(self._plugins)

    def register(self, cls: Plugin):
        name = cls.name
        config = self._configs.get(name)
        self._plugins[name] = cls(config)
        return cls

    def load_plugins(self):
        new_plugins = self.check_plugins()
        failed_plugins = self.install_plugins(new_plugins)
        all_plugins = conf().get("plugins") or []
        plugins = [
            plugin for plugin in all_plugins if plugin["name"] not in failed_plugins
        ]
        self.import_plugins(plugins)
        self.activate_plugins(plugins)

    def check_plugins(self) -> Set[str]:
        logger.info("Checking plugins...")
        plugins = conf().get("plugins") or []
        existed_plugins = self.get_existed()
        new_plugins = set()
        for plugin in plugins:
            if plugin["name"] not in existed_plugins:
                new_plugins.add(plugin["name"])
        return new_plugins

    def install_plugins(self, plugins: Set[str]) -> Set[str]:
        failed_plugins = set()
        if len(plugins) == 0:
            logger.info("All plugins are installed")
            return failed_plugins
        else:
            logger.info(f"Installing plugins: {plugins}")
            source = dict()
            try:
                with open("./plugins/source.json", "r", encoding="utf-8") as f:
                    source = json.load(f)
            except Exception as e:
                logger.error(f"Invalid plugin source: {e}")
                return plugins
            for plugin_name in plugins:
                if plugin_name in source:
                    repo = source[plugin_name]["repo"]
                    match = re.match(
                        r"^(https?:\/\/|git@)([^\/:]+)[\/:]([^\/:]+)\/(.+).git$", repo
                    )
                    if not match:
                        failed_plugins.add(plugin_name)
                        logger.error(f"Invalid repo: {repo}")
                    else:
                        try:
                            dirname = os.path.join("./plugins", plugin_name)
                            porcelain.clone(repo, dirname, checkout=True)
                            dependency_path = os.path.join(dirname, "requirements.txt")
                            if os.path.exists(dependency_path):
                                logger.info(
                                    f"Installing dependencies for {plugin_name}"
                                )
                                install_file(dependency_path)
                            logger.info(f"Install plugin {plugin_name} successfully")
                        except Exception as e:
                            failed_plugins.add(plugin_name)
                            logger.error(f"Fail to install plugin {plugin_name}: {e}")
                else:
                    failed_plugins.add(plugin_name)
                    logger.error(f"Plugin {plugin_name} is not found in source.json")
            return failed_plugins

    def get_existed(self) -> Set[str]:
        plugins_dir = os.path.abspath("./plugins")
        existed_plugins = set()
        for plugin_name in os.listdir(plugins_dir):
            plugin_path = os.path.join(plugins_dir, plugin_name)
            if os.path.isdir(plugin_path):
                # detect __init__.py in the plugin directory
                module_path = os.path.join(plugin_path, "__init__.py")
                if os.path.isfile(module_path):
                    existed_plugins.add(plugin_name)
        return existed_plugins

    def import_plugins(self, plugins: list) -> None:
        for plugin in plugins:
            try:
                self._configs[plugin["name"]] = plugin
                importlib.import_module(f"plugins.{plugin['name']}")
            except Exception as e:
                logger.exception(f"Failed to load plugin {plugin['name']}: {e}")

    def activate_plugins(self, plugins: list) -> None:
        for plugin in plugins:
            instance = self._plugins.get(plugin["name"])
            if instance is not None:
                self.on(EventType.DID_RECEIVE_MESSAGE, instance.did_receive_message)
                self.on(EventType.WILL_GENERATE_REPLY, instance.will_generate_reply)
                self.on(EventType.WILL_DECORATE_REPLY, instance.will_decorate_reply)
                self.on(EventType.WILL_SEND_REPLY, instance.will_send_reply)

    def emit(self, event: Event) -> Event:
        listeners = self.__events__.get(event.type)
        if listeners is not None and len(listeners) > 0:
            for fn in listeners:
                if event.is_proceed:
                    fn(event)
                else:
                    break
        return event

    def built_in(self, plugins: dict):
        self.on(EventType.WILL_GENERATE_REPLY, Cmd(plugins).will_generate_reply)
