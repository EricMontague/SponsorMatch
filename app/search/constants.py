"""This module contains constants to be used when
interacting with Elasticsearch.
"""


class QueryType:
    """Class that contains constants that represent
    different types of Elasticsearch queries.
    """

    MATCH = "match"
    BOOL = "bool"
    TERM = "term"
    RANGE = "range"


class BooleanClause:
    """Class that contains constants that
    represent difference types of clauses
    in a Boolean query.
    """

    MUST = "must"
    MUST_NOT = "must_not"
    FILTER = "filter"
    SHOULD = "should"
