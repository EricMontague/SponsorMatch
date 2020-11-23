"""This package contains classes which provide a more object-oriented
interface over the low level elasticsearch client.
"""

from app.search.middleware import FlaskSQLAlchemyMiddleware
from app.search.client import ElasticsearchClient
from app.search.query import MatchQuery, BooleanQuery
from app.search.constants import QueryType, BooleanClause
