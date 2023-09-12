from rest_framework import exceptions, status


class BookingDoesNotExists(exceptions.APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "The booking does not exists."
