from rest_framework.exceptions import APIException


class CustomAPIException(APIException):

    def __init__(self, p_status_code, p_default_detail):
        self.status_code = p_status_code
        self.default_detail = p_default_detail
        super(CustomAPIException, self).__init__()
