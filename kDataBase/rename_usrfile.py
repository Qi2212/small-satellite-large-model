# 创建人：QI-BRO
# 开发时间：2024-08-06  14:10
import hashlib
import random
import string
from datetime import datetime
def generate_timestamp_hash():
    """
    生成当前时间的MD5哈希值
    """
    current_time_str = datetime.now().strftime('%Y%m%d%H%M%S')
    return hashlib.md5(current_time_str.encode()).hexdigest()


def generate_filename(username, file_extension,user_type):
    """
    生成文件名，包括前缀、时间哈希和用户名
    """

    timestamp_hash = generate_timestamp_hash()
    characters = string.ascii_letters + string.digits
    # string.ascii_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    # 生成一个5位长的随机字符串
    random_string = ''.join(random.choice(characters) for _ in range(5))
    if user_type=="normal":
        filename = f'psl_{random_string}_{timestamp_hash}.{file_extension}'
    else:
        filename = f'pub_{random_string}_{timestamp_hash}.{file_extension}'
    return filename