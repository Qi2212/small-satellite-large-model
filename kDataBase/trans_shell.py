# 创建人：QI-BRO
# 开发时间：2024-08-18  22:58
import argparse
import os
import datetime
from trans_embeddings import get_text_from_file, get_embedding
from pymilvus import connections, Collection
import pymysql
from pymysql import cursors

def main(args):
    connections.connect("default", host="", port="", user='', password='')
    # replace your config of MySQL
    config = {
        'host': '',
        'user': '',
        'port':3306,
        'password': '',
        'db': '',
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

    try:
        input_path = "./ssl_chat/ssl_model/userfile/psl/"
        output_path = "./ssl_chat/ssl_model/textFile/"

        if get_text_from_file(os.path.join(input_path, args.filename), os.path.join(output_path, args.filename)):

            embedding, texts = get_embedding(os.path.join(output_path, args.filename))
            collection = Collection(args.cname)
            res = collection.insert([embedding, texts], partition_name=args.pname)
            collection.flush()

            if args.type == 'admin' and args.share == 'True':
                share_status = "shared"
            else:
                share_status = "pending"

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
                    scollection = cursor.fetchone()

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
                        with connection.cursor() as cursor2:
                            status = 'Uknow'
                            check = 'pending'
                            sql_insert2 = "INSERT INTO kDataBase_pub_share_record (uid_id,file_name,is_upload,status,collection_id_id,local_filename,file_id_id,upload_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

                            cursor2.execute(sql_insert2, (
                            uid, args.ufilename, status, check, scollection['id'], local_filename, file_id,
                            datetime.datetime.now()))
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


            with connection.cursor() as cursor4:
                sql_update4 = "UPDATE kDataBase_knowledgebase SET file_nums = file_nums + 1 WHERE uid_id = %s AND partition_name = %s"
                cursor4.execute(sql_update4, (uid, partition_name))
                connection.commit()
            connection.close()

    except Exception as e:
        print(f"trans_shell 遇到错误:{e}")
        connection = pymysql.connect(**config)
        with connection.cursor() as cursor_error:
            # 更新SQL语句
            share_status = 'error'
            status = 'error'
            milvus_id_head = None
            milvus_id_tail = None
            milvus_id_list = None
            print((status, share_status, milvus_id_head, milvus_id_tail, milvus_id_list, filename))
            sql_update3 = "UPDATE kDataBase_psl_file_record SET status = %s,share_status = %s," \
                          " milvus_id_head = %s, milvus_id_tail = %s, milvus_id_list = %s WHERE local_filename = %s"
            cursor_error.execute(sql_update3,
                            (status, share_status, milvus_id_head, milvus_id_tail, milvus_id_list, args.filename))
            connection.commit()

        if args.share == 'True':
            with connection.cursor() as cursor_e1:
                sql_query = "SELECT * FROM kDataBase_knowledgebase WHERE partition_name = %s AND collection_type = %s"
                collection_type = "public"
                cursor_e1.execute(sql_query, (sid, collection_type))
                scollection = cursor.fetchone()


            with connection.cursor() as cursor_e2:
                status = 'error'
                check = 'approved'

                sql_insert2 = "INSERT INTO kDataBase_pub_share_record (uid_id,file_name,is_upload,status,collection_id_id,local_filename,file_id_id,upload_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

                cursor_e2.execute(sql_insert2, (
                    uid, args.ufilename, status, check, scollection['id'], local_filename, file_id,
                    datetime.datetime.now()))
                connection.commit()

        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="excute for transform txt and mysql update/insert")
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
    args = parser.parse_args()

    main(args)