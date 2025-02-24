import uvicore
from uvicore.auth.user_info import UserInfo
from uvicore.support.hash import sha1
from uvicore.contracts import UserProvider
from uvicore.support.dumper import dump, dd
from uvicore.auth.support import password as pwd
from uvicore.http.request import HTTPConnection
from uvicore.typing import List, Union, Any, Dict
from uvicore.auth.models.user import User as UserModel
from uvicore.auth.models.group import Group
from datetime import datetime


@uvicore.service()
class Orm(UserProvider):
    """Retrieve and validate user from uvicore.auth ORM User model during Authentication middleware

    This is NOT a stateless user provider as it queries the user, groups, roles tables from a database.
    """

    # def __init__(self):
    #     # Only need for an __init__ override is to modify field mappings
    #     super().__init__()

    #     # Temp, until I add username to ORM model
    #     self.field_map['username'] = 'email'

    async def _retrieve_user(self,
        key_name: str,
        key_value: Any,
        request: HTTPConnection,
        *,
        password: str = None,

        # Parameters from auth config
        anonymous: bool = False,
        includes: List = None,

        # Must have kwargs for infinite allowed optional params, even if not used.
        **kwargs,
    ) -> UserInfo:
        """Retrieve user from backend"""

        # Get password hash for cache key.  Password is still required to pull the right cache key
        # or else someone could login with an invalid password for the duration of the cache
        password_hash = '/' + sha1(password) if password is not None else ''

        # Check if user already validated in cache
        cache_key = 'auth/user/' + str(key_value) + password_hash
        if await uvicore.cache.has(cache_key):
            # User is already validated and cached
            # Retrieve user from cache, no password check required because cache key has password has in it
            user = await uvicore.cache.get(cache_key)
            return user

        # ORM is currently thworing a Warning: Truncated incorrect DOUBLE value: '='
        # when using actual bool as bit value.  So I convert to '1' or '0' strings instead
        disabled = '1' if anonymous else '0'

        # Cache not found.  Query user, validate password and convert to user class
        find_kwargs = {key_name: key_value}
        db_user = await (UserModel.query()
            .include(*includes)
            .where('disabled', disabled)
            #.show_writeonly(['password'])
            .show_writeonly(True)
            .find(**find_kwargs)
        )

        # User not found or disabled.  Return None means not verified or found.
        if not db_user: return None

        # If we are checking passwords and the db_user has NO password, user cannot be logged into
        if password is not None and db_user.password is None: return None

        # If password, validate credentials
        if password is not None:
            if not pwd.verify(password, db_user.password):
                # Invalid password.  Return None means not verified or found.
                return None

        # Get users groups->roles->permissions (roles linked to a group)
        groups = []
        roles = []
        permissions = []
        if 'groups' in includes:
            user_groups = db_user.groups
            if user_groups:
                for group in user_groups:
                    groups.append(group.name)
                    if not group.roles: continue
                    for role in group.roles:
                        roles.append(role.name)
                        if not role.permissions: continue
                        for permission in role.permissions:
                            permissions.append(permission.name)

        # Get users roles->permissions (roles linked directly to the user)
        if 'roles' in includes:
            user_roles = db_user.roles
            if user_roles:
                for role in user_roles:
                    roles.append(role.name)
                    if not role.permissions: continue
                    for permission in role.permissions:
                        permissions.append(permission.name)

        # Unique groups, roles and permissions (sets are unique)
        groups = sorted(list(set(groups)))
        roles = sorted(list(set(roles)))
        permissions = sorted(list(set(permissions)))

        # Set super admin, existence of 'admin' permission
        # Fixme, there is a 'superadmin' field on the roles table.
        # If user is in any role with superadmin=True they are a superadmin
        superadmin = False
        if 'admin' in permissions:
            # No need for any permissinos besides ['admin']
            permissions = ['admin']
            superadmin = True

        # Build UserInfo dataclass with REQUIRED fields
        user = UserInfo(
            id=db_user.id or '',
            uuid=db_user.uuid or '',
            sub=db_user.uuid or '',
            username=db_user.username or '',
            email=db_user.email or '',
            first_name=db_user.first_name or '',
            last_name=db_user.last_name or '',
            title=db_user.title or '',
            avatar=db_user.avatar_url or '',
            groups=groups or [],
            roles=roles or [],
            permissions=permissions or [],
            superadmin=superadmin or False,
            authenticated=not anonymous,
        )

        # Save to cache
        await uvicore.cache.put(cache_key, user)

        # Return to user
        return user

    async def create_user(self, request: HTTPConnection, **kwargs):
        """Create new user in backend"""
        # Pop groups from kwargs
        groups = kwargs.pop('groups')

        # Set other kwargs values
        kwargs['disabled'] = False
        kwargs['login_at'] = datetime.now()

        # Translate avatar
        kwargs['avatar_url'] = kwargs.pop('avatar')

        # Build user model
        user = UserModel(**kwargs)

        # Get actual groups in backend from groups array
        real_groups = await Group.query().where('name', 'in', groups).get()

        # Save user
        await user.save()

        # Link real_groups
        await user.link('groups', real_groups)

        # Return new backend user (not actual Auth user class)
        return user

    async def sync_user(self, request: HTTPConnection, **kwargs):
        # Get username
        username = kwargs['username']

        # Get actual backend user
        user = await UserModel.query().show_writeonly(['password']).find(username=username)

        # If we have successfully logged in, we are not disabled
        user.disabled = False
        user.login_at = datetime.now()

        # Pop groups from kwargs
        groups = kwargs.pop('groups')

        # Remove other kwargs items
        del kwargs['creator_id']

        # Translate avatar
        kwargs['avatar_url'] = kwargs.pop('avatar')

        # Add all other kwargs to user
        for key, value in kwargs.items():
            setattr(user, key, value)

        # Save user
        await user.save()

        # Return new backend user (not actual Auth user class)
        return user
