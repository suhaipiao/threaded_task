import json


class RetValue:
    def __init__(self, is_ok: bool = False, err_msg: str = 'failed', value: str = '', bytes_value: bytes = ''):
        """
        初始化
        :param is_ok: 是否成功
        :param err_msg: 错误消息
        :param value: 返回值
        """
        self.__is_ok = is_ok
        self.__err_msg = err_msg
        self.__value = value
        self.__bytes_value = bytes_value

    @property
    def is_ok(self) -> bool:
        """
        是否成功
        :return: True:成功，False:失败
        """
        return self.__is_ok

    @property
    def err_msg(self) -> str:
        """
        错误消息
        :return:错误消息
        """
        return self.__err_msg

    @property
    def value(self) -> str:
        """
        返回值
        :return: 返回值
        """
        return self.__value

    @property
    def bytes_value(self) -> bytes:
        """
        返回Bytes类型值
        :return: 返回值
        """
        return self.__bytes_value

    def set_success(self, value: str, err_msg: str = 'ok', bytes_value: bytes = ''):
        """
        设置成功结果
        :param value: 结果值
        :param err_msg: 提示消息
        :param bytes_value: Bytes格式结果值
        :return: 无
        """
        self.__is_ok = True
        self.__err_msg = err_msg
        self.__value = value
        self.__bytes_value = bytes_value

    def set_failed(self, value: str, err_msg: str = 'failed', bytes_value: bytes = ''):
        """
        设置失败结果
        :param value: 失败结果值
        :param err_msg: 失败消息
        :param bytes_value: Bytes格式结果值
        :return: 无
        """
        self.__is_ok = False
        self.__err_msg = err_msg
        self.__value = value
        self.__bytes_value = bytes_value

    def to_object(self):
        """
        将结果值JSON反序列化成对象实例
        :return:
        """
        return json.loads(self.value)

