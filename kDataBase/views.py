import json

from django.http import JsonResponse
from django.shortcuts import render

from Users.models import User
from create_dataBase import create_db
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