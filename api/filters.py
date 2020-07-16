from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import filters


class CustomSearch(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        self.search_param = 'search[value]'
        return super(CustomSearch, self).filter_queryset(request, queryset, view)


class CustomOrdering(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = []
        i = 0
        while True:
            try:
                orderable = request.query_params[f'order[{i}][column]']

                ordering.append(int(orderable))
                i += 1
            except MultiValueDictKeyError:
                break

        order_dir = [f'order[{number}][dir]' for number in range(0, len(ordering))]
        order_mode = ['-' if request.query_params[mode] == 'desc' else '' for mode in order_dir]
        order_data = [f'columns[{number}][data]' for number in ordering]
        self.ordering_fields = [request.query_params[data] for data in order_data]
        self.ordering_param = [mode + self.ordering_fields[x] for x, mode in enumerate(order_mode)]
        self.ordering_param = ','.join(self.ordering_param)

        if not self.ordering_param:
            return super(CustomOrdering, self).filter_queryset(request, queryset, view)
        return queryset.order_by(self.ordering_param)
