from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import filters
from rest_framework.pagination import  LimitOffsetPagination
from rest_framework.response import Response


class CustomPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100
    limit_query_param = "length"
    offset_query_param = "start"

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previously': self.get_previous_link()
            },
            'draw': int(self.request.GET.get("draw", 0)),
            'recordsTotal': self.count,
            'recordsFiltered': self.count,
            'data': data
        })


