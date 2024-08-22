import json
import os
from django.db.models import Q
from django.core.paginator import Paginator
from django.db.models import F
from django.http import JsonResponse
from pymilvus import connections, Collection
import threading
from Users.models import User
from kDataBase.create_dataBase import my_create_collection, my_creat_partition, check_collection
from kDataBase.delete_dataBase import delete_db
from kDataBase.models import KnowledgeBase, psl_upload_record, pub_share_record, pub_upload_record, pub_file_record, \
    psl_file_record
from kDataBase.rename_usrfile import generate_filename
from kDataBase.trans_embeddings import get_embedding, get_text_from_file, get_text_from_localfile
from kDataBase.insert_dataBase import share_updateInsert

connections.connect("default", host="47.100.166.210", port="19530", user='root', password='')
from django.db import close_old_connections
import time
import subprocess


# 初始创建集群
def psl_create_knowledge_views(request):
    # post提交新建知识库的基本信息
    """
    kname:用户自定义的数据库名称
    ksynopsis:用户输入的数据库简介
    account:创建数据库的账号
    """
    if request.method == "POST":
        json_str = request.body
        json_obj = json.loads(json_str)
        partition_synopsis = json_obj.get('partition_synopsis')
        account = json_obj.get('account')
        # 用户起的数据库名 这里需要合法性检验
        partition_nickname = json_obj.get('partition_nickname')

        user = User.objects.get(account=account)
        # 集群名=用户唯一账号
        collection_name = user.account
        if user.type == 'normal' or "admin":
            print(user.type)
            collection_name = f"psl_{account}"
            # 校验集群下的分区是否已经存在
            if KnowledgeBase.objects.filter(collection_name=collection_name,
                                            partition_nickname=partition_nickname, p_status='True').exists():
                return JsonResponse(
                    {'code': 12404, 'msg': '存在重命名的知识库', 'partition_nickname': partition_nickname})

            else:
                if len(KnowledgeBase.objects.filter(collection_name=collection_name)) == 0:
                    # 初始创建集群默认创建一个  '_default'分区
                    try:
                        my_create_collection(collection_name)
                        model_instance = KnowledgeBase(uid=user, collection_name=collection_name,
                                                       partition_synopsis=partition_synopsis,
                                                       partition_nickname="_default"
                                                       , partition_name='_default', collection_type='personal')
                        model_instance.save()
                    except Exception as e:
                        print(f"遇到错误：{e}")
                        return JsonResponse({"code": 12099, "msg": "遇到错误"})

                try:
                    partition_name = my_creat_partition(collection_name, account)

                    model_instance = KnowledgeBase(uid=user, collection_name=collection_name,
                                                   partition_synopsis=partition_synopsis
                                                   , partition_name=partition_name, collection_type='personal',
                                                   partition_nickname=partition_nickname)
                    model_instance.save()
                    return JsonResponse({"code": 200, "msg": "创建成功", 'partition_nickname': partition_nickname,
                                         'pid': partition_name})
                except Exception as e:
                    print(f"遇到错误：{e}")
                    return JsonResponse({"code": 12099, "msg": "遇到错误"})


def pub_create_knowledge_views(request):
    if request.method == "POST":
        json_str = request.body
        json_obj = json.loads(json_str)
        partition_synopsis = json_obj.get('partition_synopsis', '')
        account = json_obj.get('account')
        partition_nickname = json_obj.get('partition_nickname')
        user = User.objects.get(account=account)

        # 所有的公共知识库公用一个集群：“pub_kdb"
        collection_name = "pub_kdb"
        if user.type == 'admin':
            # 校验公共知识库的分区是否已经存在
            if KnowledgeBase.objects.filter(collection_name=collection_name,
                                            partition_nickname=partition_nickname, p_status='True').exists():
                return JsonResponse(
                    {'code': 12404, 'msg': '存在重命名的知识库', 'partition_nickname': partition_nickname})

            else:
                # 公共数据库->collection还没创建 创建完就注释这段代码
                if len(KnowledgeBase.objects.filter(collection_name=collection_name)) == 0:
                    try:
                        my_create_collection(collection_name)
                        model_instance = KnowledgeBase(uid=user, collection_name=collection_name,
                                                       partition_synopsis=partition_synopsis,
                                                       partition_nickname="_default"
                                                       , partition_name='_default', collection_type='public')
                        model_instance.save()
                    except Exception as e:
                        print(f"遇到错误：{e}")
                        return JsonResponse({"code": 12099, "msg": "遇到错误"})

                try:
                    # 新建知识库分区
                    partition_name = my_creat_partition(collection_name, account)

                    model_instance = KnowledgeBase(uid=user, collection_name=collection_name,
                                                   partition_synopsis=partition_synopsis
                                                   , partition_name=partition_name, collection_type='public',
                                                   partition_nickname=partition_nickname)
                    model_instance.save()
                    return JsonResponse({"code": 200, "msg": "创建成功", 'partition_nickname': partition_nickname,
                                         'pid': partition_name})
                except Exception as e:
                    print(f"遇到错误：{e}")
                    return JsonResponse({"code": 12099, "msg": "遇到错误"})


        else:
            return JsonResponse({'code': 12401, 'msg': '不具备操作权限'})


# 删除个人知识库
def psl_delete_knowledgeBase(request):
    if request.method == "Delete":
        json_str = request.body
        json_obj = json.loads(json_str)
        account = json_obj.get('account')
        partition_name = json_obj.get('partition_name')
        # 校验账号权限
        usr = User.objects.get(account=account)

        # 校验要删除的分区是否存在
        try:
            kbase = KnowledgeBase.objects.get(collection_name=account, uid=usr.id, partition_name=partition_name)
        except Exception as e:
            print(f"遇到错误{e}")
            return JsonResponse({"code": 12402, 'msg': "数据库遇到错误！"})
        # 删除知识库
        if delete_db(account, partition_name):
            # 删除KnowledgeBase的记录
            kbase.delete()
            # psl_upload_record外键 -> 级联删除psl_upload_record/pub_upload_record/pub_upload_record的关联记录
            return JsonResponse({"code": 200, "msg": "知识库删除成功"})


# 删除公共知识库


# 个人数据库上传
def psl_upload(request):
    if request.method == 'POST' or "OPTIONS":
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        file_extension = file_name.split('.')[-1]  # 扩展名

        # “是”/"否"
        is_share = request.POST.get('is_share')
        account = request.POST.get('account')
        partition_name = request.POST.get('pid')

        sid = request.POST.get('sid', '无')

        usr = User.objects.get(account=account)
        # 存储用户上传的文件
        local_filename = generate_filename(usr.username, file_extension, usr.type)
        # 绝对路径
        save_path = '/home/zhengwen/xiashuqi/ssl_model/userfile/psl/'
        full_path = os.path.join(save_path, local_filename)
        # 保存文件
        with open(full_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
                # 本地存储用户上传文件
        print(" 上传成功")
        collection_name = f"psl_{account}"
        kbase = KnowledgeBase.objects.get(collection_name=collection_name, partition_name=partition_name, uid=usr.id)
        # 校验登录权限、数据库
        file_record = psl_file_record(file_name=file_name, collection_name=collection_name,
                                      status='middle',
                                      partition_name=partition_name, uid=usr, partition_id=kbase,
                                      local_filename=local_filename, is_share=is_share, sid=sid,
                                      milvus_id_list="Unknow",
                                      milvus_id_head="Unknow",
                                      milvus_id_tail="Unknow"
                                      )
        file_record.save()
        # 定义要传递给trans_shell的参数
        params = [
            '--account', account,
            '--type', usr.type,
            '--uid', str(usr.id),
            '--pid', str(kbase.id),
            '--sid', sid,
            '--fid', str(file_record.id),
            '--filename', local_filename,
            '--ufilename', file_name,
            '--share', is_share,
            '--cname', collection_name,
            '--pname', partition_name
        ]
        # subprocess.Popen启动子进程
        subprocess.Popen(['python', '/home/zhengwen/xiashuqi/ssl_model/kDataBase/trans_shell.py'] + params)
        print("主进程继续执行")
        return JsonResponse({'code': 200, 'msg': '文件上传成功！已经存储'})


# 公共数据库上传
def pub_upload(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        file_extension = file_name.split('.')[-1]  # 扩展名

        account = request.POST.get('account')
        partition_name = request.POST.get('pid')

        usr = User.objects.get(account=account)
        # 存储用户上传的文件
        local_filename = generate_filename(usr.username, file_extension, usr.type)
        # 绝对路径
        save_path = '/home/zhengwen/xiashuqi/ssl_model/userfile/pub/'
        full_path = os.path.join(save_path, local_filename)
        # 保存文件
        with open(full_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        collection_name = "pub_kdb"
        # 校验登录权限、数据库
        kcollection = KnowledgeBase.objects.get(collection_name=collection_name, partition_name=partition_name)
        file_record = pub_file_record(uid=usr, file_name=file_name, status='middle',
                                      collection_name=collection_name,
                                      partition_name=partition_name,
                                      partition_id=kcollection,
                                      local_filename=local_filename,
                                      milvus_id_list="Unknow",
                                      milvus_id_head="Unknow",
                                      milvus_id_tail="Unknow")
        file_record.save()
        # 定义要传递给trans_shell的参数
        params = [
            '--account', account,
            '--type', usr.type,
            '--uid', str(usr.id),
            '--pid', str(kcollection.id),
            '--fid', str(file_record.id),
            '--filename', local_filename,
            '--ufilename', file_name,
            '--cname', collection_name,
            '--pname', partition_name
        ]
        # subprocess.Popen启动子进程
        subprocess.Popen(['python', '/home/zhengwen/xiashuqi/ssl_model/kDataBase/trans_pub_shell.py'] + params)
        print("主进程继续执行")
        return JsonResponse({'code': 200, 'msg': '文件上传成功！已经存储'})


def share_check(record):
    if record.is_share == 'False':
        share_conllection = 'Unknow'
        return share_conllection
    else:
        return KnowledgeBase.objects.get(partition_name=record.sid).partition_nickname


# 个人数据库上传记录
def psl_upload_records(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        account = request.GET.get('account')
        collection_name = f"psl_{account}"

        psl_records = psl_upload_record.objects.filter(collection_name=collection_name)
        records = [{
            "name": record.partition_id.partition_nickname,  # 这个含义是知识库名称
            "file_name": record.file_name,
            'upload_time': record.upload_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字符串
            "status": record.status,
            "milvus_id": record.milvus_id,
            "is_share": share_check(record),
            "share_collection": 'None',
            "sid": 'None',
            "share_status": record.share_status

        } for record in psl_records]

        paginator = Paginator(records, 10)
        page_obj = paginator.get_page(page)
        return JsonResponse({'code': 200, "msg": "查询成功", "total_num": len(psl_records), 'data': list(page_obj)})


def success_check(record, filetype):
    if filetype == 'personal':
        p_root = "/userfile/psl/"
    else:
        p_root = "/userfile/pub/"
    if record.status == 'failure':
        f_null = "None"
        return f_null
    else:
        base_url = "http://433f1ca3.r29.cpolar.top"
        f_url = base_url + p_root + record.local_filename
        return f_url

    # 个人文件上传记录


def psl_file_records(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        account = request.GET.get('account')
        collection_name = f"psl_{account}"

        psl_f_records = psl_file_record.objects.filter(collection_name=collection_name)
        records = [{
            "name": record.partition_id.partition_nickname,  # 这个含义是知识库名称
            "file_name": record.file_name,
            'upload_time': record.upload_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字符串
            "status": record.status,
            "is_share": record.is_share,
            "share_collection": share_check(record),
            "share_status": record.share_status,
            "sid": record.sid,
            "fid": record.local_filename,
            "f_url": success_check(record, "personal")
        } for record in psl_f_records]
        if psl_file_record.objects.filter(collection_name=collection_name, status='middle').exists():
            transforming = 'True'
        else:
            transforming = 'False'

        paginator = Paginator(records, 10)
        page_obj = paginator.get_page(page)
        return JsonResponse({'code': 200, "msg": "查询成功", "total_num": len(records), 'data': list(page_obj),
                             'transforming': transforming})


# 个人知识库信息


def partition_info(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        account = request.GET.get('account')
        collection_name = f"psl_{account}"
        psl_kdbs = KnowledgeBase.objects.filter(
            Q(collection_name=collection_name, p_status='True') & ~Q(partition_name='_default')
        )
        if psl_kdbs.exists():
            db_data1 = [{
                "type": db.collection_type,
                'create_time': db.create_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字符串
                "name": db.partition_nickname,
                "pid": db.partition_name,
                "synopsis": db.partition_synopsis,
                "file_num": len(db.psl_records_k2.filter(status='success'))
            } for db in psl_kdbs]
        else:
            db_data1 = []

        pub_kdbs = KnowledgeBase.objects.filter(
            Q(collection_name="pub_kdb", p_status='True') & ~Q(partition_name='_default')
        )
        if pub_kdbs.exists():
            # file_objs=
            db_data2 = [{
                "type": db.collection_type,
                'create_time': db.create_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字符串
                "name": db.partition_nickname,
                "pid": db.partition_name,
                "synopsis": db.partition_synopsis,
                "file_num": len(db.pub_file_records.filter(status='success'))
            } for db in pub_kdbs]
        else:
            db_data2 = []

        db_data = db_data1 + db_data2
        # 分页
        paginator = Paginator(db_data, 10)
        page_obj = paginator.get_page(page)
        return JsonResponse({'code': 200, "msg": "查询成功", "total_num": len(db_data), 'data': list(page_obj)})


def sort_key(record):
    # 自定义排序逻辑：'pending' 排在前面，'approved' 排在后面
    if record.status == 'pending':
        return 0
    else:
        return 1

    # 超级管理员端查看个人数据库的共享记录:


def psl_share_records(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        account = request.GET.get('account')

        usr = User.objects.get(account=account)
        if usr.type != 'admin':
            return JsonResponse({'code': 12401, 'msg': '不具备操作权限'})

        share_records = pub_share_record.objects.all()
        sorted_records = sorted(share_records, key=sort_key)
        records = [{
            "username": record.uid.username,
            'upload_time': record.upload_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字符串
            "file_name": record.file_name,
            "status": record.status,
            "share_collection": record.collection_id.partition_nickname,
            "pid": record.collection_id.partition_name,
            "is_upload": record.is_upload,
            "fid": record.local_filename,
            "f_url": success_check(record, "personal"),
        } for record in sorted_records]

        paginator = Paginator(records, 10)
        page_obj = paginator.get_page(page)
        return JsonResponse({'code': 200, "msg": "查询成功", "total_num": len(records), 'data': list(page_obj)})


# 公共数据库文件上传记录
def pub_upload_records(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        account = request.GET.get('account')

        usr = User.objects.get(account=account)
        if usr.type != 'admin':
            return JsonResponse({'code': 12401, 'msg': '不具备操作权限'})

        share_records = pub_file_record.objects.all()
        records = [{
            "username": record.uid.username,
            'upload_time': record.createTime.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字符串
            "file_name": record.file_name,
            "status": record.status,
            "collection_name": record.collection_name,
        } for record in share_records]

        paginator = Paginator(records, 10)
        page_obj = paginator.get_page(page)
        return JsonResponse({'code': 200, 'data': list(page_obj)})


def share_operate(request):
    if request.method == 'PATCH':
        json_str = request.body
        json_obj = json.loads(json_str)

        # 审核的结果 True/False
        operate = json_obj.get('operate')
        account = json_obj.get('account')
        pid = json_obj.get('pid')
        fid = json_obj.get('fid')
        # 校验超管权限
        print(account)
        usr = User.objects.get(account=account)
        if usr.type != 'admin':
            return JsonResponse({'code': 12401, 'msg': '不具备操作权限'})

        # 查找共享数据库 给share校验
        share_collection = KnowledgeBase.objects.get(collection_type="public", collection_name='pub_kdb',
                                                     partition_name=pid)
        # 查询这条共享记录
        share = pub_share_record.objects.get(local_filename=fid, collection_id=share_collection.id)
        psl_file_object = psl_file_record.objects.get(id=share.file_id.id)
        psl_upload_objects = psl_file_record.objects.filter(id=share.file_id.id)

        # 如果不上传
        if operate == 'False':
            share.status = 'approved'
            share.is_upload = 'False'
            share.save()
            # 更新 psl_file_record 的状态
            psl_file_object.share_status = 'failed'
            psl_file_object.save()
            psl_upload_objects.update(share_status='failed')
            return JsonResponse({'code': 200, 'msg': '操作成功'})

        # 如果决定上传执行下面代码
        keys = share_updateInsert(collection_name1=psl_file_object.collection_name,
                                  partition_name1=psl_file_object.partition_name,
                                  head=psl_file_object.milvus_id_head,
                                  tail=psl_file_object.milvus_id_tail,
                                  collection_name2="pub_kdb",
                                  partition_name2=share.collection_id.partition_name)
        if keys:
            print(keys)
            share.status = 'approved'
            share.is_upload = 'True'
            share.save()
            # 更新 psl_file_record 的状态
            psl_file_object.share_status = 'shared'
            psl_file_object.save()
            psl_upload_objects.update(share_status='shared')

            # 获取上传者
            upload_usrid = User.objects.get(id=psl_file_object.uid.id)
            # 新增文件上传记录
            new_pubfile = pub_file_record(
                collection_name="pub_kdb",
                partition_name=pid,
                uid=upload_usrid,
                file_name=psl_file_object.file_name,
                local_filename=psl_file_object.local_filename,
                status='success',
                partition_id=share_collection,
                milvus_id_head=str(keys[0]),
                milvus_id_tail=str(keys[-1]),
                milvus_id_list=str(keys)
            )
            new_pubfile.save()

            # 更新上传细目记录
            for key in keys:
                new_pubupload = pub_upload_record(
                    collection_name="pub_kdb",
                    partition_name=pid,
                    uid=upload_usrid,
                    file_name=psl_file_object.file_name,
                    local_filename=psl_file_object.local_filename,
                    status='success',
                    partition_id=share_collection,
                    milvus_id=str(key),
                    file_id=new_pubfile
                )
                new_pubupload.save()

            # 审核上传以后公共知识库的文件数+1
            share_collection.file_nums = share_collection.file_nums + 1
            share_collection.save()

            return JsonResponse({'code': 200, 'msg': '操作成功'})


        else:
            # share.update(status='approved',is_upload='error')
            # psl_file_object.update(share_status='error')
            share.status = 'approved'
            share.is_upload = 'error'
            share.save()
            # 更新 psl_file_record 的状态
            psl_file_object.share_status = 'error'
            psl_file_object.save()
            psl_upload_objects.update(share_status='error')
            return JsonResponse({"code": 12403, 'msg': "遇到错误"})

    else:
        return JsonResponse({"code": 12498, 'msg': "method is not allowed!"})


def partition_base_info(request):
    if request.method == 'GET':
        account = request.GET.get('account')
        collection_name = f"psl_{account}"
        psl_kdbs = KnowledgeBase.objects.filter(
            Q(collection_name=collection_name, p_status='True') & ~Q(partition_name='_default')
        )
        pub_kdb = KnowledgeBase.objects.filter(
            Q(collection_name="pub_kdb", p_status='True') & ~Q(partition_name='_default')
        )
        combined_queryset = psl_kdbs.union(pub_kdb)
        combined_queryset = combined_queryset.order_by('collection_type')
        db_data = [{
            "type": db.collection_type,
            "name": db.partition_nickname,
            "pid": db.partition_name,
        } for db in combined_queryset]

        return JsonResponse({'code': 200, "msg": "查询成功", "total_num": len(db_data), 'data': db_data})


def psl_partition_info(request):
    if request.method == 'GET':
        # page = request.GET.get('page', 1)
        account = request.GET.get('account')
        collection_name = f"psl_{account}"
        kdbs = KnowledgeBase.objects.filter(collection_name=collection_name, p_status='True').exclude(
            partition_name='_default')

        # db_data = [{
        #     "type": db.collection_type,
        #     'create_time': db.create_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字符串
        #     "name": db.partition_nickname,
        #     "pid": db.partition_name,
        #     "synopsis": db.partition_synopsis,
        #     "file_num": db.file_nums
        # } for db in kdbs]

        db_data = [{
            "type": db.collection_type,
            "name": db.partition_nickname,
            "pid": db.partition_name
        } for db in kdbs]

        # 分页
        # paginator = Paginator(db_data, 10)
        # page_obj = paginator.get_page(page)
        return JsonResponse({'code': 200, "msg": "查询成功", "total_num": len(db_data), 'data': db_data})


# 公共知识库信息
def pub_partition_info(request):
    if request.method == 'GET':
        # page = request.GET.get('page', 1)
        account = request.GET.get('account')
        collection_name = "pub_kdb"
        kdbs = KnowledgeBase.objects.filter(collection_name=collection_name, collection_type="public",
                                            p_status='True').exclude(
            partition_name='_default')
        usr = User.objects.get(account=account)
        db_data = [{
            "type": db.collection_type,
            "name": db.partition_nickname,
            "pid": db.partition_name,
        } for db in kdbs]

        # 分页
        # paginator = Paginator(db_data, 10)
        # page_obj = paginator.get_page(page)
        return JsonResponse({'code': 200, "msg": "查询成功", "total_num": len(db_data), 'data': db_data})


# admin的个人+公共知识库上传文件记录
def admin_file_records(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        account = request.GET.get('account')
        usr = User.objects.get(account=account)
        if usr.type != 'admin':
            return JsonResponse({'code': 12401, 'msg': '不具备操作权限'})

        psl_f_records = psl_file_record.objects.filter(collection_name=f"psl_{account}")
        pub_f_records = pub_file_record.objects.filter(collection_name="pub_kdb", uid=usr.id)

        psl_records = [{
            "name": record.partition_id.partition_nickname,  # 这个含义是知识库名称
            "file_name": record.file_name,
            'upload_time': record.upload_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字符串
            "status": record.status,
            "is_share": record.is_share,
            "share_collection": share_check(record),
            "sid": record.sid,
            "type": "personal",
            "fid": record.local_filename,
            "f_url": success_check(record, "personal")
        } for record in psl_f_records]

        pub_records = [{
            "name": record.partition_id.partition_nickname,  # 这个含义是知识库名称
            "file_name": record.file_name,
            'upload_time': record.upload_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字符串
            "status": record.status,
            "type": "public",
            "fid": record.local_filename,
            "f_url": success_check(record, "public")
        } for record in pub_f_records]

        if psl_file_record.objects.filter(collection_name="psl_{account}",
                                          status='middle').exists() or pub_file_record.objects.filter(
                collection_name="pub_kdb", status='middle').exists():
            transforming = 'True'
        else:
            transforming = 'False'
        records = psl_records + pub_records
        # 按时间排序
        sorted_records = sorted(records, key=lambda x: x['upload_time'])
        paginator = Paginator(sorted_records, 10)
        page_obj = paginator.get_page(page)
        return JsonResponse({'code': 200, "msg": "查询成功", "total_num": len(sorted_records), 'data': list(page_obj),
                             'transforming': transforming})


def psl_pid_filerecord(request):
    if request.method == "GET":
        page = request.GET.get('page', 1)
        account = request.GET.get("account")
        pid = request.GET.get("pid", 'all')
        print(pid)
        collection_name = f"psl_{account}"

        if pid != "all":

            partition_files = (
                KnowledgeBase.objects.get(collection_name=collection_name, partition_name=pid)).psl_records_k2.filter(
                status='success')
            # psl_records_k2

            p_files = [{
                "name": record.partition_id.partition_nickname,  # 这个含义是知识库名称
                "file_name": record.file_name,
                'upload_time': record.upload_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字符串
                "status": record.status,
                "is_share": record.is_share,
                "share_collection": share_check(record),
                "sid": record.sid,
                "type": "personal",
                "fid": record.local_filename,
                "f_url": success_check(record, "personal")
            } for record in partition_files]
            paginator = Paginator(p_files, 10)
            page_obj = paginator.get_page(page)
            return JsonResponse({'code': 200, "msg": "查询成功", "total_num": len(p_files), 'data': list(page_obj)})
        elif pid == 'all':
            partition_files = (KnowledgeBase.objects.get(collection_name=collection_name)).psl_records_k2.filter(
                status='success')
            # psl_records_k2

            p_files = [{
                "name": record.partition_id.partition_nickname,  # 这个含义是知识库名称
                "file_name": record.file_name,
                'upload_time': record.upload_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字符串
                "status": record.status,
                "is_share": record.is_share,
                "share_collection": share_check(record),
                "sid": record.sid,
                "type": "personal",
                "fid": record.local_filename,
                "f_url": success_check(record, "personal")
            } for record in partition_files]
            paginator = Paginator(p_files, 10)
            page_obj = paginator.get_page(page)
            return JsonResponse({'code': 200, "msg": "查询成功", "total_num": len(p_files), 'data': list(page_obj)})


def pub_pid_filerecord(request):
    if request.method == "GET":
        page = request.GET.get('page', 1)
        account = request.GET.get("account")
        pid = request.GET.get("pid", 'all')
        print(pid)
        usr = User.objects.get(account=account)
        # if usr.type != 'admin':
        #     return JsonResponse({'code': 12401, 'msg': '不具备操作权限'})

        collection_name = "pub_kdb"

        if pid != "all":

            partition_files = (KnowledgeBase.objects.get(collection_name=collection_name, partition_name=pid,
                                                         p_status='True')).pub_file_records.filter(status='success')
            # psl_records_k2

            p_files = [{
                "name": record.partition_id.partition_nickname,  # 这个含义是知识库名称
                "file_name": record.file_name,
                'upload_time': record.upload_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字符串
                "status": record.status,
                "type": "public",
                "fid": record.local_filename,
                "f_url": success_check(record, "public"),
                "upload_user": record.uid.username
            } for record in partition_files]
            paginator = Paginator(p_files, 10)
            page_obj = paginator.get_page(page)
            return JsonResponse({'code': 200, "msg": "查询成功", "total_num": len(p_files), 'data': list(page_obj)})
        elif pid == 'all':
            partition_files = pub_file_record.objects.filter(status='success')
            # psl_records_k2

            p_files = [{
                "name": record.partition_id.partition_nickname,  # 这个含义是知识库名称
                "file_name": record.file_name,
                'upload_time': record.upload_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字符串
                "status": record.status,
                "type": "public",
                "fid": record.local_filename,
                "f_url": success_check(record, "public"),
                "upload_user": record.uid.username
            } for record in partition_files]
            paginator = Paginator(p_files, 10)
            page_obj = paginator.get_page(page)
            return JsonResponse({'code': 200, "msg": "查询成功", "total_num": len(p_files), 'data': list(page_obj)})


def rename_kbase(request):
    if request.method == 'PATCH':
        json_str = request.body
        json_obj = json.loads(json_str)

        print(json_obj)
        # 审核的结果 True/False
        account = json_obj.get('account')
        pid = json_obj.get('pid')
        # 要修改的知识库名称的知识库的类型
        ktype = json_obj.get('type')
        new_nickname = json_obj.get('new_nickname')

        # 校验用户权限
        usr = User.objects.get(account=account)
        if usr.type == 'normal' and ktype == 'public':
            return JsonResponse({"code": 12401, 'msg': '不具备操作权限'})

        # 校验是否为空
        if new_nickname.strip() == '':
            return JsonResponse({"code": 12479, 'msg': '知识库名称不能为空'})

        if usr.type == 'normal':
            collection_name = f"psl_{account}"
            try:
                partition_object = KnowledgeBase.objects.get(collection_name=collection_name, partition_name=pid,
                                                             uid=usr.id, p_status='True')
            except:
                return JsonResponse({"code": 124088, 'msg': '不具备该知识库重命名操作权限'})
        elif usr.type == "admin":
            if ktype == "personal":
                collection_name = f"psl_{account}"
                try:
                    partition_object = KnowledgeBase.objects.get(collection_name=collection_name, partition_name=pid,
                                                                 uid=usr.id, p_status='True')
                except:
                    return JsonResponse({"code": 124088, 'msg': '不具备该知识库重命名操作权限'})
            elif ktype == "public":
                collection_name = f"pub_kdb"
                try:
                    partition_object = KnowledgeBase.objects.get(collection_name=collection_name, partition_name=pid,
                                                                 p_status='True')
                except:
                    return JsonResponse({"code": 124088, 'msg': '不具备该知识库重命名操作权限'})
        try:
            partition_object.partition_nickname = new_nickname
            partition_object.save()
            return JsonResponse({"code": 200, "msg": "重命名成功"})
        except Exception as e:
            print(f"重命名数据库遇到问题:{e}")
            return JsonResponse({"code": 12099, "msg": "遇到错误"})


def file_delete(request):
    if request.method == "DELETE":
        json_str = request.body
        json_obj = json.loads(json_str)

        # 审核的结果 True/False
        account = json_obj.get('account')
        # 文件所在的知识库
        pid = json_obj.get('pid')
        # 要删除的文件所在的知识库类型
        ktype = json_obj.get('type')
        fid = json_obj.get('fid')
        """
            查询文件记录
            校验文件的状态是否为success
            找到要删除的milvus id 范围
            文件状态转换为 false
            后台脚本删除
        """
        usr = User.objects.get(account=account)
        if ktype == 'personal':
            collection_name = f"psl_{account}"
            del_obj = psl_file_record.objects.get(uid=usr.id, local_filename=fid, status='success', partition_name=pid)
            params = [
                '--cname', collection_name,
                '--pname', pid,
                '--milvusList', del_obj.milvus_id_list
            ]
            subprocess.Popen(['python', '/home/zhengwen/xiashuqi/ssl_model/kDataBase/fileDel_shell.py'] + params)
            del_obj.status = 'false'
            del_obj.save()
            # 详细记录的更新
            upload_obj = (del_obj.psl_file_milvusid).all()
            upload_obj.update(status='false')
            # 更新文件数量
            kbase = KnowledgeBase.objects.get(collection_name=collection_name, partition_name=pid, uid=usr.id)
            kbase.file_nums = len(kbase.psl_records_k2.filter(status='success'))
            kbase.save()
            print("主进程继续执行")
            return JsonResponse({'code': 200, 'msg': '文件删除成功'})


        elif ktype == 'public':
            collection_name = f"pub_kdb"
            del_obj = pub_file_record.objects.get(local_filename=fid, status='success', partition_name=pid)
            params = [
                '--cname', collection_name,
                '--pname', pid,
                '--milvusList', del_obj.milvus_id_list
            ]
            subprocess.Popen(['python', '/home/zhengwen/xiashuqi/ssl_model/kDataBase/fileDel_shell.py'] + params)
            del_obj.status = 'false'
            del_obj.save()
            # 详细记录的更新
            upload_obj = (del_obj.pub_file_milvusid).all()
            upload_obj.update(status='false')

            kbase = KnowledgeBase.objects.get(collection_name=collection_name, partition_name=pid)
            kbase.file_nums = len(kbase.pub_file_records.filter(status='success'))
            kbase.save()
            print("主进程继续执行")
            return JsonResponse({'code': 200, 'msg': '文件删除成功'})


""""
    1.数据库校验
    2.权限校验
    3.找到数据库对应的所有 文件上传记录 全部转换为false
    4.脚本drop分区
"""


def delete_kbase(request):
    if request.method == "DELETE":

        json_str = request.body
        json_obj = json.loads(json_str)

        # 审核的结果 True/False
        account = json_obj.get('account')
        pid = json_obj.get('pid')
        # 要修改的知识库名称的知识库的类型
        ktype = json_obj.get('type')
        print(json_obj)
        usr = User.objects.get(account=account)
        if ktype == 'personal':
            collection_name = f"psl_{account}"
            del_obj = KnowledgeBase.objects.get(uid=usr.id, partition_name=pid, p_status='True',
                                                collection_name=collection_name)
            params = [
                '--cname', collection_name,
                '--pname', pid,
            ]
            subprocess.Popen(['python', '/home/zhengwen/xiashuqi/ssl_model/kDataBase/partitionDel_shell.py'] + params)
            del_obj.p_status = 'False'
            del_obj.save()
            # psl_file_record 、psl_upload_record更新状态为 false
            # psl_file_record
            file_obj = (del_obj.psl_records_k2).all()
            file_obj.update(status='false')

            # psl_upload_record
            for obj in file_obj:
                upload_obj = (obj.psl_file_milvusid).all()
                upload_obj.update(status='false')

            print("主进程继续执行")
            return JsonResponse({'code': 200, 'msg': '知识库删除成功'})


        elif ktype == 'public':
            if usr.type != 'admin':
                return JsonResponse({'code': 12401, 'msg': '不具备操作权限'})

            else:

                collection_name = f"pub_kdb"
                del_obj = KnowledgeBase.objects.get(partition_name=pid, p_status='True',
                                                    collection_name=collection_name)
                params = [
                    '--cname', collection_name,
                    '--pname', pid,
                ]
                subprocess.Popen(
                    ['python', '/home/zhengwen/xiashuqi/ssl_model/kDataBase/partitionDel_shell.py'] + params)
                del_obj.p_status = 'False'
                del_obj.save()
                # pub_file_record 、pub_upload_record更新状态为 false
                # pub_file_record
                file_obj = (del_obj.pub_file_records).all()
                file_obj.update(status='false')

                # pub_upload_record
                for obj in file_obj:
                    upload_obj = (obj.pub_file_milvusid).all()
                    upload_obj.update(status='false')

                print("主进程继续执行")
                return JsonResponse({'code': 200, 'msg': '知识库删除成功'})