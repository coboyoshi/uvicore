from abc import ABC, abstractmethod
from typing import Any, Dict, List

from uvicore.contracts import Application, Package, Dispatcher


class Provider(ABC):

    @property
    @abstractmethod
    def app(self) -> Application:
        """Uvicore application instance"""
        pass

    @property
    @abstractmethod
    def events(self) -> Dispatcher:
        """Event instance"""
        pass

    @property
    @abstractmethod
    def package(self) -> Package:
        """The current package class.  Not available in boot()"""
        pass

    @property
    @abstractmethod
    def app_config(self) -> Dict: pass

    @property
    @abstractmethod
    def package_config(self) -> Dict: pass

    @property
    def name(self) -> Dict: pass

    @abstractmethod
    def register(self) -> None: pass

    @abstractmethod
    def boot(self) -> None: pass

    @abstractmethod
    def bind(self,
        name: str,
        object: Any,
        *,
        factory: Any = None,
        kwargs: Dict = None,
        singleton: bool = False,
        aliases: List = []
    ) -> None:
        pass

    @abstractmethod
    def views(self, package: Package, paths: List) -> None: pass

    @abstractmethod
    def assets(self, package: Package, paths: List) -> None: pass

    @abstractmethod
    def template(self, package: Package, options: Dict) -> None: pass

    @abstractmethod
    def web_routes(self, package: Package, routes_class: Any) -> None: pass

    @abstractmethod
    def api_routes(self, package: Package, routes_class: Any) -> None: pass

    @abstractmethod
    def commands(self, package: Package, options: Dict) -> None: pass

    @abstractmethod
    def configs(self, modules: List) -> None:
        """Register your app configs with the configuration system"""
        pass
