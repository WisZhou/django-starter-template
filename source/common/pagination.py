# coding: utf-8

from collections import OrderedDict

from rest_framework import pagination
from rest_framework.response import Response


class Pagination(pagination.PageNumberPagination):

    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        page_size = self.get_page_size(self.request)

        total_page = self.page.paginator.count / page_size
        if self.page.paginator.count % page_size:
            total_page += 1

        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('page_size', page_size),
            ('total_page', total_page),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
