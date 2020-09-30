from __future__ import annotations
import uvicore
from typing import Optional
from uvicore.auth.database.tables import users as table
from uvicore.orm.fields import Field, HasOne
from uvicore.orm.metaclass import ModelMetaclass
from uvicore.orm.model import Model
from uvicore.support.dumper import dd, dump


#Model: _Model = uvicore.ioc.make('Model', _Model)
#import sys
#sys.modules['uvicore.orm.model']._Model = 'asdf'
#dump(sys.modules['uvicore.orm.model'].__dict__)

#from uvicore.orm.model import _Model
#dump(_Model)
#asdf('asdf')

# from abc import ABC, abstractmethod
# class UserInterface(ABC):
#     # @abstractmethod
#     # def idx(self) -> Optional[int]:
#     #     pass

#     id2: Optional[int]

# UserModel for typehints only.  Import User for actual usage.
#class UserModel(Model, metaclass=ModelMetaclass):
class UserModel(Model['UserModel'], metaclass=ModelMetaclass):
#class UserModel(Model['UserModel']):
    """Auth User Model"""

    # Database connection and table information
    __tableclass__ = table.Users

    id: Optional[int] = Field('id',
        primary=True,
        description='User Primary ID',
        sortable=True,
        searchable=True,
    )

    email: str = Field('email',
        description='User Email and Username',
        required=True,
    )

    # One-To-One - User has ONE Contact
    info: Optional[UserInfo] = Field(None,
        description='User Info Model',
        relation=HasOne('uvicore.auth.models.user_info.UserInfo', 'user_id'),
    )


    # class Config:
    #     extra = 'ignore'
    #     arbitrary_types_allowed = True


# IoC Class Instance
User: UserModel = uvicore.ioc.make('uvicore.auth.models.user.User', UserModel)


from uvicore.auth.models.user_info import UserInfo
#UserInfo = uvicore.ioc.make('uvicore.auth.models.user_info.UserInfo')

User.update_forward_refs()
