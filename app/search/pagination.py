"""This module contains a class that mimics the interface of
SQLAlchemy's pagination object.
"""


class ElasticsearchPagination:
    """Class that mimics the interface of Flask-SQLAlchemy's
    Pagination object. This is needed to overcome the fact that you
    cannot create a proper Pagination object when returning search results
    from Elasticsearch
    """

    def __init__(self, has_prev, has_next, prev_num, next_num, page, total, per_page, items):
        self.has_prev = has_prev
        self.has_next = has_next
        self.prev_num = prev_num
        self.next_num = next_num
        self.page = page
        self.total = total
        self.items = items
        self.per_page = per_page

    def iter_pages(self):
        current_page = 1
        total_pages = self.total
        while total_pages > 0:
            yield current_page
            current_page += 1
            total_pages -= self.per_page

    @classmethod
    def create(cls, has_prev, has_next, total, current_page, per_page,items):
        prev_num = 1
        if has_prev:
            prev_num = current_page - 1
        next_num = 1
        if has_next:
            next_num = current_page + 1
        return cls(has_prev, has_next, prev_num, next_num, current_page, total, per_page, items)