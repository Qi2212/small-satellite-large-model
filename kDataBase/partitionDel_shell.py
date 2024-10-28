# 创建人：QI-BRO
# 开发时间：2024-08-20  19:23
# 创建人：QI-BRO
# 开发时间：2024-08-18  22:58
import argparse
from pymilvus import connections, Collection


def main(args):
    # add your info of milvus
    connections.connect("default", host="", port="19530", user='', password='')
    collection=Collection(args.cname)
    #确认删除操作是否需要 release()
    collection.drop_partition(args.pname)
    if not collection.has_partition(args.pname):
        print(f"分区 {args.pname} 删除成功")
    else:
        print(f"分区 {args.pname} 删除失败")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="excute for delfile-> milvus id in partition")
    parser.add_argument("--cname", type=str, required=True, help="The name of the user's uploaded collection in milvus")
    parser.add_argument("--pname", type=str, required=True,help="The name of the user's uploaded partition in collection")

    args = parser.parse_args()

    main(args)