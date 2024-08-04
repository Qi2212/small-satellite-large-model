import re

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
import hashlib
import json
from django.http import JsonResponse
from django.views import View
from .models import User
from django.contrib.sessions.models import Session

class RegisterView(View):
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        account = json_obj.get('account')
        password = json_obj.get('password')

        if account == "":
            result = {'code': 11401, 'msg': '请输入账号'}
            return JsonResponse(result)
        if password == "":
            result = {'code': 11402, 'msg': '请输入密码'}
            return JsonResponse(result)
        #检查用户账号是否可用
        if re.match(r'^((13[0-9])|(14[0-9])|(15[0-9])|(17[0-9])|(18[0-9]))\d{8}$',account) == None:
            result = {'code':11403, 'msg': '格式有误'}
            return JsonResponse(result)

        #检查用户名是否可用
        old_users = User.objects.filter(account=account)
        if old_users:
            result = {'code': 11404, 'msg': '账号已经存在'}
            return JsonResponse(result)
        #Users插入数据（密码md5存储）
        m = hashlib.md5()
        m.update(password.encode())

        User.objects.create(account=account,password= m.hexdigest())

        result = {'code': 200, 'msg':'注册成功'}
        return JsonResponse(result)
