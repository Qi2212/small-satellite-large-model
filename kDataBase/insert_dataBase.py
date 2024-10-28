# 创建人：QI-BRO
# 开发时间：2024-08-18  2:50
from pymilvus import connections, Collection
import torch


def share_updateInsert(collection_name1,partition_name1,head,tail,collection_name2,partition_name2):
    torch.manual_seed(0)
    # add your info of milvus
    connections.connect("default", host="", port="19530", user='', password='')
    try:
        collection1 = Collection(collection_name1)
        collection1.load(partition_names=[partition_name1])
        expr=f"{head} <= id <= {tail}"
        res = collection1.query(expr, output_fields=["embedding","text"],partition_name=partition_name1)
        print(res)
        embeddings=[]
        texts=[]
        for item in res:
            embeddings.append(item['embedding'])
            texts.append(item['text'])
        data=[embeddings,texts]
        collection1.release()
        
        collection2=Collection(collection_name2)
        collection2.load(partition_names=[partition_name2])
        res = collection2.insert(data, partition_name=partition_name2)
        collection2.flush()
        print(f'本次文件上传共传入数据库{res.insert_count}条语料')
        collection2.release()
        return res.primary_keys
    except Exception as e:
        print(f"insert_dataBase.share_updateInsert 遇到问题：{e}")
        return False
