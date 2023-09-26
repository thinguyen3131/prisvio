from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions


class GCSUploadSignedUrlException(exceptions.APIException):
    status_code = 400
    default_code = "gcs_signed_url_fail"
    default_detail = _("Generate gcs signed url failed.")


class GCSMissingFilenameException(exceptions.APIException):
    status_code = 400
    default_code = "gcs_signed_url_missing_file_name"
    default_detail = _("Missing file name.")


class GCSMissingFileTypeException(exceptions.APIException):
    status_code = 400
    default_code = "gcs_signed_url_missing_file_type"
    default_detail = _("Missing file type.")
