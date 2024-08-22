# 创建人：QI-BRO
# 开发时间：2024-08-20  19:23
# 创建人：QI-BRO
# 开发时间：2024-08-18  22:58
"""

1.修改文件名
2.读取文件进行转换
3.数据库更新
4.完脚本命令
"""

import argparse
import os
import datetime
from trans_embeddings import get_text_from_file, get_embedding
from pymilvus import connections, Collection

connections.connect("default", host="47.100.166.210", port="19530", user='root', password='')



def main(args):
    collection=Collection(args.cname)
    #确认删除操作是否需要 release()
    collection.delete(partition_names=args.pname,expr=f"id in {args.milvusList}")



if __name__ == "__main__":
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="excute for delfile-> milvus id in partition")

    # 添加参数
    parser.add_argument("--cname", type=str, required=True, help="The name of the user's uploaded collection in milvus")
    parser.add_argument("--pname", type=str, required=True,help="The name of the user's uploaded partition in collection")
    parser.add_argument("--milvusList", type=str, required=True,help="The milvusList（todelID） of deleted file ")
    # 解析命令行参数
    args = parser.parse_args()

    # 调用 main 函数
    main(args)