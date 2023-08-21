from drf_yasg.inspectors import CoreAPICompatInspector


class NoPaginatorInspector(CoreAPICompatInspector):
    def get_paginator_parameters(self, paginator):
        return []


class NoFilterInspector(CoreAPICompatInspector):
    def get_filter_parameters(self, filter_backend):
        return []
