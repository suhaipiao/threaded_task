import datetime
import json
import time
import base64
import gzip
import requests
from typing import Any
from common import RetValue


class HttpHelper:
    UnpackType_Nothing = 0       # 不做任何处理
    UnpackType_UnZipBase64 = 1   # Base64解码后再解压
    UnpackType_UnBase64 = 2      # Base64解码

    @staticmethod
    def post(url: str, data: Any, timeout: int = 60) -> RetValue:
        result = RetValue()
        try:
            res = requests.post(url, data=data, headers={'Content-Type': "application/json"}, timeout=timeout)
            if res.status_code == 200:
                result.set_success(value=res.text, err_msg='ok', bytes_value=res.content)
            else:
                result.set_failed(value='', err_msg='request failed, http code={res.status_code}')
        except Exception as e:
            result.set_failed(value='', err_msg='{e}')
        finally:
            return result

    @staticmethod
    def post_binary(url: str, byte_data: bytes, token, unpack_type=UnpackType_Nothing, timeout: int = 60) -> RetValue:
        result = RetValue()
        try:
            res = requests.post(url, data=byte_data, headers={
                'Content-Type': "application/octet-stream",
                'bot-token': token,
            }, timeout=timeout)
            if res.status_code == 200:
                raw_str = ""
                raw_bytes = res.content
                if unpack_type == HttpHelper.UnpackType_Nothing:
                    raw_str = res.text
                if unpack_type == HttpHelper.UnpackType_UnZipBase64:
                    raw_str = ZipBase64Helper.unzip_base64_gzip_string_to_string(res.text)
                if unpack_type == HttpHelper.UnpackType_UnBase64:
                    raw_str = ZipBase64Helper.base64_string_to_string(res.text)
                result.set_success(value=raw_str, err_msg='ok', bytes_value=raw_bytes)
            else:
                result.set_failed(value='', err_msg=f'request failed, http code={res.status_code}')
        except Exception as e:
            result.set_failed(value='', err_msg=f'{e}')
        finally:
            return result


class LogHelper:
    @staticmethod
    def log_debug(title: str, content: str):
        now_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f'[{now_time_str}] [DEBUG] <{title}> {content}')

    @staticmethod
    def log_info(title: str, content: str):
        now_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f'[{now_time_str}] [INFO] <{title}> {content}')

    @staticmethod
    def log_warn(title: str, content: str):
        now_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f'[{now_time_str}] [WARN] <{title}> {content}')

    @staticmethod
    def log_error(title: str, content: str):
        now_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f'[{now_time_str}] [ERROR] <{title}> {content}')


class ZipBase64Helper:
    @staticmethod
    def string_to_base64_string(str_data: str, encoding: str = 'utf8'):
        return base64.encodebytes(str_data.encode(encoding)).decode()

    @staticmethod
    def bytes_to_base64_string(bytes_data: bytes, encoding: str = 'utf8'):
        return base64.encodebytes(bytes_data).decode(encoding)

    @staticmethod
    def bytes_to_base64_bytes(bytes_data: bytes):
        return base64.encodebytes(bytes_data)

    @staticmethod
    def string_to_bytes(str_data: str, encoding: str = 'utf8'):
        return str_data.encode(encoding=encoding)

    @staticmethod
    def bytes_to_string(bytes_data: bytes, encoding: str = 'utf8'):
        return bytes_data.decode(encoding=encoding)

    @staticmethod
    def base64_string_to_string(base64_str: str, encoding: str = 'utf8'):
        return base64.decodebytes(base64_str.encode()).decode(encoding=encoding)

    @staticmethod
    def base64_string_to_bytes(base64_str: str, encoding: str = 'utf8'):
        return base64.decodebytes(base64_str.encode(encoding))

    @staticmethod
    def zip_string_to_gzip_bytes(str_data: str, encoding: str = 'utf8'):
        return gzip.compress(str_data.encode(encoding))

    @staticmethod
    def zip_string_to_gzip_and_base64_string(str_data: str, encoding: str = 'utf8'):
        return ZipBase64Helper.bytes_to_base64_string(gzip.compress(str_data.encode(encoding)))

    @staticmethod
    def zip_string_to_gzip_and_base64_bytes(str_data: str, encoding: str = 'utf8'):
        return ZipBase64Helper.bytes_to_base64_bytes(gzip.compress(str_data.encode(encoding)))

    @staticmethod
    def unzip_base64_gzip_string_to_string(base64_zipped_str: str, encoding: str = 'utf8'):
        s = ZipBase64Helper.base64_string_to_bytes(base64_zipped_str)
        return gzip.decompress(s).decode(encoding)
