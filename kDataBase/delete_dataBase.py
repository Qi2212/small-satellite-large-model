# 创建人：QI-BRO
# 开发时间：2024-08-05  17:41
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import torch

torch.manual_seed(0)

def delete_db(collection_name,partition_name):
    connections.connect("default", host="47.100.166.210", port="19530", user='root', password='')
    collection = Collection(collection_name)
    try:
        status = collection.drop_partition(partition_name)
        if status.OK():
            print(f"分区 {partition_name} 删除成功")
            return True
        else:
            print(f"分区 {partition_name} 删除失败: {status.message}")
            return False
    except Exception as e:
        print(f"删除分区时发生错误: {e}")
        return False