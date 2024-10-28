# 创建人：QI-BRO
# 开发时间：2024-08-20  3:13
import argparse
import os
import datetime
from trans_embeddings import get_text_from_file, get_embedding
from pymilvus import connections, Collection
import pymysql
from pymysql import cursors


def main(args):
    connections.connect("default", host="", port="19530", user='', password='')
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
        #add/replace your local path of pub & psl file
        input_path = "./ssl_chat/ssl_model/userfile/pub/"
        output_path = "./ssl_chat/ssl_model/textFile/"
        if get_text_from_file(os.path.join(input_path, args.filename), os.path.join(output_path, args.filename)):

            embedding, texts = get_embedding(os.path.join(output_path, args.filename))
            collection = Collection(args.cname)
            res = collection.insert([embedding, texts], partition_name=args.pname)
            collection.flush()


            data_to_insert = []
            uid = args.uid
            filename = args.ufilename
            status = 'success'
            collection_name = args.cname
            partition_name = args.pname
            local_filename = args.filename
            partition_id = args.pid
            file_id = args.fid

            connection = pymysql.connect(**config)
            for id in res.primary_keys:
                upload_time = datetime.datetime.now()
                data = (uid, filename, str(id), status, collection_name,
                        partition_name,  local_filename, partition_id,file_id,upload_time)
                data_to_insert.append(data)

            print(f"data: {data_to_insert}")
            with connection.cursor() as cursor:
                sql_insert1 = "INSERT INTO kDataBase_pub_upload_record (uid_id,file_name,milvus_id,status,collection_name," \
                              "partition_name,local_filename, partition_id_id, file_id_id,upload_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

                cursor.executemany(sql_insert1, data_to_insert)
                print("ok 104")
            connection.commit()

            print(f"文件：{args.filename} 已经转换完成并插入数据库 {len(data_to_insert)} 条上传记录 ")

            with connection.cursor() as cursor3:
                status = 'success'
                milvus_id_head = str(res.primary_keys[0])
                milvus_id_tail = str(res.primary_keys[-1])
                milvus_id_list = str(res.primary_keys)
                print((status, milvus_id_head, milvus_id_tail, milvus_id_list, filename))
                sql_update3 = "UPDATE kDataBase_pub_file_record SET status = %s," \
                              "milvus_id_head = %s, milvus_id_tail = %s, milvus_id_list = %s WHERE local_filename = %s"
                cursor3.execute(sql_update3,
                                (status,milvus_id_head, milvus_id_tail, milvus_id_list, args.filename))
                connection.commit()


            with connection.cursor() as cursor4:
                sql_update4 = "UPDATE kDataBase_knowledgebase SET file_nums = file_nums + 1 WHERE uid_id = %s AND partition_name = %s"
                cursor4.execute(sql_update4, (uid, partition_name))

                connection.commit()

            connection.close()
        print("trans_shell 脚本执行完毕")
    except Exception as e:
        print(f"遇到错误:{e}")
        connection = pymysql.connect(**config)
        with connection.cursor() as cursor_e1:
            status = 'error'
            milvus_id_head = None
            milvus_id_tail = None
            milvus_id_list = None
            print((status, milvus_id_head, milvus_id_tail, milvus_id_list, args.ufilename))
            sql_update3 = "UPDATE kDataBase_pub_file_record SET status = %s," \
                          "milvus_id_head = %s, milvus_id_tail = %s, milvus_id_list = %s WHERE local_filename = %s"
            cursor_e1.execute(sql_update3,
                            (status, milvus_id_head, milvus_id_tail, milvus_id_list, args.filename))
            connection.commit()



        connection.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="excute for transform txt and mysql update/insert")

    parser.add_argument("--account", type=str, required=True, help="The account of uploading user")
    parser.add_argument("--type", type=str, required=True, help="The type of account admin/normal")
    parser.add_argument("--uid", type=str, required=True, help="The id of user in mysql")
    parser.add_argument("--pid", type=str, required=True,help="The partition_object of file_record in kDataBase_knowledgebase")
    parser.add_argument("--fid", type=str, required=True, help="The type of account admin/normal")
    parser.add_argument("--filename", type=str, required=True, help="fileid of file_record in mysql")
    parser.add_argument("--ufilename", type=str, required=True, help="fileid of file_record in mysql")
    parser.add_argument("--cname", type=str, required=True, help="The name of the user's uploaded collection in milvus")
    parser.add_argument("--pname", type=str, required=True,help="The name of the user's uploaded partition in collection")

    args = parser.parse_args()

    main(args)