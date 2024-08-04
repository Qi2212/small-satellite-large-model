# 创建人：QI-BRO
# 开发时间：2024-08-04  17:20

from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import torch

torch.manual_seed(0)


def create_db(collection_name):
    if utility.has_collection(collection_name):
        return False
    try:
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2000)
        ]
        schema = CollectionSchema(fields, collection_name)
        collection = Collection(collection_name, schema)
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "IP",
            "params": {"nlist": 1536},
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        collection.load()
        print("success Create collection: ", collection_name)
        return True
    except Exception as e:
        print(f"新建知识库遇到错误:{e}")
        return False
