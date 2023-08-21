from rest_framework import exceptions, status


class StaffDoesNotExists(exceptions.APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Staff does not exists.'
