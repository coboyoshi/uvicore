import uvicore
from uvicore.support import module
from uvicore.typing import Dict, Any
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Cache as CacheInterface


@uvicore.service('uvicore.cache.manager.Manager',
    aliases=['Cache', 'cache'],
    singleton=True,
)
class Manager:

    @property
    def default(self) -> str:
        return self._default

    @property
    def stores(self) -> Dict[str, Dict]:
        return self._stores

    @property
    def backends(self) -> Dict:
        return self._backends

    def __init__(self):
        #self.default = config.default
        #self.stores = config.stores
        self._current_store = None
        self._backends = Dict()
        self._default: str = uvicore.config.app.cache.default
        self._stores: Dict = uvicore.config.app.cache.stores

    def connect(self, store: str = None) -> CacheInterface:
        """Connect to a cache backend store"""
        store_name = store or self.default
        store = self.stores.get(store_name)
        if not store:
            raise Exception('Cache store {} not found'.format(store_name))

        if store_name not in self.backends:
            # Instantiate, connect and save store in local backends cache
            driver = module.load(store.driver).object(self, store)
            self._backends[store_name] = driver

        return self.backends[store_name]

    def store(self, store: str = None) -> CacheInterface:
        """Alias to connect"""
        return self.connect(store)
