from rest_framework import exceptions, status


class LoginFailException(exceptions.APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "No active account found with the given credentials."
    code = "no_active_account"
