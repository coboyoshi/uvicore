import uvicore
import sqlalchemy as sa
from uvicore.database.table import Schema, SchemaOLD
from uvicore.support.dumper import dump, dd


class _Groups(Schema):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'groups'

    # Connection for this database from your config file
    connection = 'auth'

    # SQLAlchemy Table definition as a list (exclude name and metadata)
    # This will be converted into an actual SQLAlchemy Table() instance
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema = [
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(length=100))
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {}


# IoC Class Instance
Groups: _Groups = uvicore.ioc.make('uvicore.auth.database.tables.Groups.Groups', _Groups, singleton=True)
