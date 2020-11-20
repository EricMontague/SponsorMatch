"""This package contains classes which provide a more object-oriented
interface over the low level elasticsearch client.
"""

from app.search.middleware import sqlalchemy_search_middleware
from app.search.query import MatchQuery, BooleanQuery
from app.search.constants import QueryType, BooleanClause
