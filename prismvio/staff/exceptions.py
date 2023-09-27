from rest_framework import exceptions, status


class StaffDoesNotExists(exceptions.APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Staff does not exists."


class MerchantIDAndUserIDNullException(exceptions.APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "The merchant_id and user_id are not null."
