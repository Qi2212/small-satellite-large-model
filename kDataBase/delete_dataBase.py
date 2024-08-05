# 创建人：QI-BRO
# 开发时间：2024-08-05  17:41
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import torch

torch.manual_seed(0)

def delete_db(collection_name):
    connections.connect("default", host="47.100.166.210", port="19530", user='root', password='')
    if utility.has_collection(collection_name):
        try:
            utility.drop_collection(collection_name)
            return True
        except Exception as e:
            print(f"遇到错误{e}")
            return False
    else:
        return False

