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

import pymysql
from pymysql import cursors


def main(args):
    # 文件内容提取
    config = {
        'host': '47.100.198.147',
        'user': 'root',
        'port': 4406,
        'password': 'tyut123456',
        'db': 'ssl_model',
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

    print("trans_shell 脚本开始执行")
    try:
        input_path = "/home/zhengwen/xiashuqi/ssl_model/userfile/psl/"
        output_path = "/home/zhengwen/xiashuqi/ssl_model/textFile/"

        if get_text_from_file(os.path.join(input_path, args.filename), os.path.join(output_path, args.filename)):

            embedding, texts = get_embedding(os.path.join(output_path, args.filename))
            # 加载用户上传的集群名称
            collection = Collection(args.cname)
            # 插入数据到数据库
            res = collection.insert([embedding, texts], partition_name=args.pname)
            collection.flush()

            if args.type == 'admin' and args.share == 'True':
                share_status = "shared"
            else:
                share_status = "pending"

            # data_to_insert=[]
            # for id in res.primary_keys:
            #     uid=args.uid
            #     filename=args.ufilename
            #     milvus_id=id
            #     status='success'
            #     collection_name=args.cname
            #     partition_name=args.pname
            #     is_share=args.share
            #     local_filename=args.filename
            #     partition_id=args.pid
            #     sid=args.sid
            #     file_id=args.fid
            #     upload_time=datetime.datetime.now()
            #     data=(uid,filename,milvus_id,status,collection_name,
            #     partition_name,is_share,local_filename, partition_id, sid,file_id,share_status,upload_time)

            #     data_to_insert.append(data)

            data_to_insert = []
            uid = args.uid
            filename = args.ufilename
            status = 'success'
            collection_name = args.cname
            partition_name = args.pname
            is_share = args.share
            local_filename = args.filename
            partition_id = args.pid
            sid = args.sid
            file_id = args.fid

            connection = pymysql.connect(**config)
            for id in res.primary_keys:
                upload_time = datetime.datetime.now()
                data = (uid, filename, str(id), status, collection_name,
                        partition_name, is_share, local_filename, partition_id, sid, file_id, share_status, upload_time)
                data_to_insert.append(data)

            print(f"data: {data_to_insert}")
            with connection.cursor() as cursor:
                # 构造SQL插入语句，注意%s是占位符，用于executemany()中的每个数据项
                sql_insert1 = "INSERT INTO kDataBase_psl_upload_record (uid_id,file_name,milvus_id,status,collection_name," \
                              "partition_name,is_share,local_filename, partition_id_id, sid,file_id_id,share_status,upload_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

                # 使用executemany()执行批量插入
                cursor.executemany(sql_insert1, data_to_insert)
                print("ok 104")
                # 提交事务
            connection.commit()

            print(f"文件：{args.filename} 已经转换完成并插入数据库 {len(data_to_insert)} 条上传记录 ")

            if args.share == 'True':
                with connection.cursor() as cursor:
                    sql_query = "SELECT * FROM kDataBase_knowledgebase WHERE partition_name = %s AND collection_type = %s"
                    collection_type = "public"
                    cursor.execute(sql_query, (sid, collection_type))
                    scollection = cursor.fetchone()  # fetchone() 返回单个匹配项

                    print("ok 94")
                    if args.type == 'admin':
                        with connection.cursor() as cursor2:
                            status = 'True'
                            check = 'approved'

                            sql_insert2 = "INSERT INTO kDataBase_pub_share_record (uid_id,file_name,is_upload,status,collection_id_id,local_filename,file_id_id,upload_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

                            cursor2.execute(sql_insert2, (
                            uid, args.ufilename, status, check, scollection['id'], local_filename, file_id,
                            datetime.datetime.now()))  # 假设id是自增的
                            connection.commit()

                    else:
                        print("ok 106开始执行！")
                        print(uid)
                        with connection.cursor() as cursor2:
                            status = 'Uknow'
                            check = 'pending'
                            sql_insert2 = "INSERT INTO kDataBase_pub_share_record (uid_id,file_name,is_upload,status,collection_id_id,local_filename,file_id_id,upload_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

                            cursor2.execute(sql_insert2, (
                            uid, args.ufilename, status, check, scollection['id'], local_filename, file_id,
                            datetime.datetime.now()))  # 假设id是自增的
                            connection.commit()
                print(f"文件：{args.filename} 已经转换完成共享数据库的 insert操作 ")

            with connection.cursor() as cursor3:
                # 更新SQL语句
                share_status = 'pending'
                status = 'success'
                milvus_id_head = str(res.primary_keys[0])
                milvus_id_tail = str(res.primary_keys[-1])
                milvus_id_list = str(res.primary_keys)
                print((status, share_status, milvus_id_head, milvus_id_tail, milvus_id_list, filename))
                sql_update3 = "UPDATE kDataBase_psl_file_record SET status = %s,share_status = %s," \
                              " milvus_id_head = %s, milvus_id_tail = %s, milvus_id_list = %s WHERE local_filename = %s"
                cursor3.execute(sql_update3,
                                (status, share_status, milvus_id_head, milvus_id_tail, milvus_id_list, args.filename))
                connection.commit()

            print("ok  129")
            with connection.cursor() as cursor4:
                # 构造SQL语句
                sql_update4 = "UPDATE kDataBase_knowledgebase SET file_nums = file_nums + 1 WHERE uid_id = %s AND partition_name = %s"

                # 执行SQL语句
                cursor4.execute(sql_update4, (uid, partition_name))

                # 提交事务
                connection.commit()

            connection.close()
        print("trans_shell 脚本执行完毕")
    except Exception as e:
        print(f"遇到错误:{e}")


# def re_update(res):
#     config = {
#     'host': '47.100.198.147',
#     'user': 'root',
#     'port':4406,
#     'password': 'tyut123456',
#     'db': 'ssl_model',
#     'charset': 'utf8mb4',
#     'cursorclass': pymysql.cursors.DictCursor
# }

#     connection = pymysql.connect(**config)


if __name__ == "__main__":
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="excute for transform txt and mysql update/insert")

    # 添加参数
    parser.add_argument("--account", type=str, required=True, help="The account of uploading user")
    parser.add_argument("--type", type=str, required=True, help="The type of account admin/normal")
    parser.add_argument("--uid", type=str, required=True, help="The id of user in mysql")
    parser.add_argument("--pid", type=str, required=True,
                        help="The partition_object of file_record in kDataBase_knowledgebase")
    parser.add_argument("--sid", type=str, required=True, help="The share_collection id in mysql")
    parser.add_argument("--fid", type=str, required=True, help="The type of account admin/normal")
    parser.add_argument("--filename", type=str, required=True, help="fileid of file_record in mysql")
    parser.add_argument("--ufilename", type=str, required=True, help="fileid of file_record in mysql")
    parser.add_argument("--share", type=str, required=True, help="The slection of share True/False")
    parser.add_argument("--cname", type=str, required=True, help="The name of the user's uploaded collection in milvus")
    parser.add_argument("--pname", type=str, required=True,
                        help="The name of the user's uploaded partition in collection")
    # 解析命令行参数
    args = parser.parse_args()

    # 调用 main 函数
    main(args)