from rest_framework import exceptions, status

from prismvio.users.enums import IntervalLockTime


class LoginFailException(exceptions.APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "No active account found with the given credentials."
    code = "no_active_account"


class ExpiredOTPException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Expired OTP."
    code = "expired_otp"


class InvalidOTPException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid OTP."
    code = "invalid_otp"


class OTPRequestLimitedException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = f"Request was throttled. Expected available in {IntervalLockTime.CHECK} seconds."
    code = "otp_request_limited"
