# 创建人：QI-BRO
# 开发时间：2024-08-20  19:23
# 创建人：QI-BRO
# 开发时间：2024-08-18  22:58
"""
    传参 pname cname
    1.删除分区
    2.分区删除状态校验
    3.完脚本命令
"""

import argparse
from pymilvus import connections, Collection

connections.connect("default", host="47.100.166.210", port="19530", user='root', password='')



def main(args):
    print("==============================================================\n"
          "=================  partitionDel_shell.py start ===============")
    collection=Collection(args.cname)
    #确认删除操作是否需要 release()
    collection.drop_partition(args.pname)
    if not collection.has_partition(args.pname):
        print(f"分区 {args.pname} 删除成功")
        print("==============================================================\n"
              "=================  partitionDel_shell.py end ===============")
    else:
        print(f"分区 {args.pname} 删除失败")
        print("==============================================================\n"
              "=================  partitionDel_shell.py end ===============")


if __name__ == "__main__":
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="excute for delfile-> milvus id in partition")
    # 添加参数
    parser.add_argument("--cname", type=str, required=True, help="The name of the user's uploaded collection in milvus")
    parser.add_argument("--pname", type=str, required=True,help="The name of the user's uploaded partition in collection")
    # 解析命令行参数
    args = parser.parse_args()

    # 调用 main 函数
    main(args)