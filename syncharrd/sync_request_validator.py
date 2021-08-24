from os import path
from http import HTTPStatus


def is_valid_add_sync_request(sub_file_path, media_file_path, synched_sub_file_path):
    if not sub_file_path:
        return False, __missing_query_param_error("sub")
    elif not media_file_path:
        return False, __missing_query_param_error("media")
    elif not synched_sub_file_path:
        return False, __missing_query_param_error("synchedSub")
    elif not path.exists(str(sub_file_path)):
        return False, __bad_request_error("Sub file does not exist: '{}'".format(str(sub_file_path)))
    elif not path.exists(str(media_file_path)):
        return False, __bad_request_error("Media file does not exist:  '{}'".format(str(media_file_path)))

    return True, None, None


def __missing_query_param_error(param_name):
    return __bad_request_error("Missing query parm: '{}'".format(param_name))


def __bad_request_error(message):
    return message, HTTPStatus.BAD_REQUEST
