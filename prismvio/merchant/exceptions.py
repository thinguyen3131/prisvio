from rest_framework import exceptions, status


class MerchantDoesNotExistsException(exceptions.APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Merchant does not exists."


class MerchantAlreadyExistsException(exceptions.APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "You already have a merchant."
