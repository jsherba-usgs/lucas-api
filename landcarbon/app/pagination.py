from spillway import pagination


class FeaturePagination(pagination.FeaturePagination):
    page_size = 10
    page_size_query_param = 'pagesize'
