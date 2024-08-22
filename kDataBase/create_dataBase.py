# 创建人：QI-BRO
# 开发时间：2024-08-04  17:20

from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import torch
from datetime import datetime

torch.manual_seed(0)

connections.connect("default", host="47.100.166.210", port="19530", user='root', password='')

def check_collection(collection_name):
    connections.connect("default", host="47.100.166.210", port="19530", user='root', password='')
    if utility.has_collection(collection_name):
        return False
    else:
        return True



#新建知识数据库
def my_create_collection(collection_name):
    connections.connect("default", host="47.100.166.210", port="19530", user='root', password='')
    if not utility.has_collection(collection_name):
        try:
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2000)
            ]
            schema = CollectionSchema(fields, collection_name)
            collection = Collection(collection_name, schema)
            index_params = {
                "index_type": "IVF_FLAT",
                "metric_type": "IP",
                "params": {"nlist": 1024},
            }
            collection.create_index(field_name="embedding", index_params=index_params)
            collection.release()
            print("success Create collection: ", collection_name)
        except Exception as e:
            print(f"新建知识库遇到错误:{e}")


#创建知识库->创建分区
def my_creat_partition(collection_name,account,partition_name='_default'):
    connections.connect("default", host="47.100.166.210", port="19530", user='root', password='')
    if not utility.has_collection(collection_name):
        print(f"集合 {collection_name} 不存在")
        return False
    else:
        collection = Collection(collection_name)
        if collection_name=="pub_kdb":
            partition_name=rename_partition_name(account,type="admin")
        else:
            partition_name = rename_partition_name(account)
        try:
            collection.create_partition(partition_name)
            print(f"分区 {partition_name} 创建成功")
            collection.load()
            collection.release()
            return partition_name
        except Exception as e:
            print(f"创建分区时发生错误: {e}")
            return False


def rename_partition_name(account,type="personal"):
    if type=="personal":
        now = datetime.now()
        time_str = now.strftime("%m%d%H%M%S")
        rename=f"psl_{account[-4:]}_{time_str}"
        return rename
    else:
        now = datetime.now()
        time_str = now.strftime("%m%d%H%M%S")
        rename=f"pub_{time_str}"
        return rename