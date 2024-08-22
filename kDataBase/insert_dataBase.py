# 创建人：QI-BRO
# 开发时间：2024-08-18  2:50
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import torch

torch.manual_seed(0)
# [449259043596557363, 449259043596557364, 449259043596557365, 449259043596557366, 449259043596557367, 449259043596557368,
# 449259043596557369, 449259043596557370, 449259043596557371, 449259043596557372, 449259043596557373, 449259043596557374]
connections.connect("default", host="47.100.166.210", port="19530", user='root', password='')


def share_updateInsert(collection_name1, partition_name1, head, tail, collection_name2, partition_name2):
    print("==============================================================\n"
          "=================  share_updateInsert start ===============")
    try:
        connections.connect("default", host="47.100.166.210", port="19530", user='root', password='')
        collection1 = Collection(collection_name1)
        collection1.load(partition_names=[partition_name1])
        expr = f"{head} <= id <= {tail}"
        res = collection1.query(expr, output_fields=["embedding", "text"], partition_name=partition_name1)
        print(res)
        embeddings = []
        texts = []
        for item in res:
            embeddings.append(item['embedding'])
            texts.append(item['text'])
        data = [embeddings, texts]

        # 释放查询完成的知识库
        collection1.release()

        collection2 = Collection(collection_name2)
        collection2.load(partition_names=[partition_name2])
        res = collection2.insert(data, partition_name=partition_name2)
        collection2.flush()
        print(f'本次文件上传共传入数据库{res.insert_count}条语料')
        collection2.release()
        print("==============================================================\n"
              "=================  share_updateInsert end ===============")
        return res.primary_keys
    except Exception as e:
        print(f"insert_dataBase.share_updateInsert 遇到问题：{e}")
        return False

# share_updateInsert(collection_name1="psl_13326442858",partition_name1="psl_2858_0816165751",head="449259043596557363",tail="449259043596557374",
#                    collection_name2="pub_kdb", partition_name2="pub_0816213908")