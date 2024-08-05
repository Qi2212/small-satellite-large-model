import json
from django.http import JsonResponse
from Users.models import User
from create_dataBase import create_db
from kDataBase.delete_dataBase import delete_db
from kDataBase.models import KnowledgeBase


# Create your views here.
#新建知识库
def create_knowledgeBase(request):
    #post提交新建知识库的基本信息
    """
    kname:用户自定义的数据库名称
    ksynopsis:用户输入的数据库简介
    account:创建数据库的账号
    """
    if request.method=="POST":
        json_str = request.body
        json_obj = json.loads(json_str)
        kname = json_obj.get('kname')
        ksynopsis = json_obj.get('ksynopsis','')
        account = json_obj.get('account')
        #检验当前用户的知识数据库是否存在重名数据库





        if create_db(kname):
            try:
                user=User.objects.get(account=account)
                model_instance = KnowledgeBase(uid=user, kname=kname,ksynopsis=ksynopsis)
                model_instance.save()
                return JsonResponse({"code": 200, "msg": "创建成功"})
            except Exception as e:
                print(f"遇到错误:{e}")
                return JsonResponse({"code": 12401, "msg": "创建失败"})
        else:
            return JsonResponse({"code": 12401, "msg": "创建失败"})


#删除知识库
def delete_knowledgeBase(request):
    if request.method == "Delete":
        json_str = request.body
        json_obj = json.loads(json_str)
        kname = json_obj.get('kname')
        account = json_obj.get('account')
        #校验账号权限
        usr=User.objects.get(account=account)

        try:
            kbase=KnowledgeBase.objects.get(kname=kname,uid=usr.id)
        except Exception as e:
            print(f"遇到错误{e}")
            return JsonResponse({"code":12402,'msg':"数据库遇到错误！"})
        #删除知识库
        if delete_db(kname):
            #删除KnowledgeBase的记录
            kbase.delete()
            #psl_upload_record外键 -> 级联删除psl_upload_record/pub_upload_record/pub_upload_record的关联记录
            return JsonResponse({"code":200,"msg":"知识库删除成功"})


#清空知识库->保留milvus集群 但清空所有记录

#个人数据库上传
def psl_upload(request):
    if request.method=="POST":
        pass
    """
    1.接受前端文件->需要一个给用户文件重命名的功能
    2.
    filename
    filetype
    """


#公共数据库上传
def pub_upload(request):
    if request.method=="POST":
        pass
    """
    1.接受前端文件->需要一个给用户文件重命名的功能
    2.
    filename
    filetype
    """

#返回res->固定格式
"""
try 
except
文件失败:record=psl_upload_record(filname=filename,file_type=file_type,milvus_id=null,status='failure')  ...save
return {12xxx "msg":"文件还"
res=client.insert(
    collection_name="quick_setup",
    data=data,
    partition_name="partitionA"
)#插入操作
res字典 dict
res['ids']
for id in res['ids']:
    record=psl_upload_record(filname=filename,file_type=file_type,milvus_id=id....)
    record.save()

return 
"""



#删一次->删一个文件 多个文件
#文件对应的所有id找到 filter 上传时间 唯一 id ->很多个记录
#13，14，15，16   ids=[13,14,15,16]
#存一个要删除的id的列表


####删除


###删除mysql的对应记录

# Output
#
# res={
#     "insert_count": 10,
#     "ids": [
#         10,
#         11,
#         12,
#         13,
#         14,
#         15,
#         16,
#         17,
#         18,
#         19
#     ]
# }