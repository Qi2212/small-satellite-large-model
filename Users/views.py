import re

from django.db.models import Q
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
        username = json_obj.get('username')
        account = json_obj.get('account')
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')

        if username == "":
            result = {'code': 11401, 'msg': '请输入用户名'}
            return JsonResponse(result)
        if account == "":
            result = {'code': 11402, 'msg': '请输入账号'}
            return JsonResponse(result)
        if password_1 == "":
            result = {'code': 11403, 'msg': '请输入密码'}
            return JsonResponse(result)
        if password_2 == "":
            result = {'code': 11404, 'msg': '请再次输入密码'}
            return JsonResponse(result)

        # 两个密码要保持一致，判断并作出响应
        if password_1 != password_2:
            result = {'code': 11405, 'msg': '两次密码输入不一致'}
            return JsonResponse(result)

        #检查用户账号是否可用
        if re.match(r'^((13[0-9])|(14[0-9])|(15[0-9])|(17[0-9])|(18[0-9]))\d{8}$',account) == None:
            result = {'code':11406, 'msg': '用户账号格式有误'}
            return JsonResponse(result)

        #检查用户名是否可用
        old_users = User.objects.filter(account=account)
        if old_users:
            result = {'code': 11407, 'msg': '账号已经存在'}
            return JsonResponse(result)

        #Users插入数据（密码md5存储）
        m = hashlib.md5()
        m.update(password_1.encode())

        User.objects.create(account=account,username = username,password= m.hexdigest())

        result = {'code': 200, 'msg':'注册成功'}
        return JsonResponse(result)

class LoginView(View):
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        account = json_obj.get('account')
        password = json_obj.get('password')

        try:
            user = User.objects.get(Q(account=account))
        except User.DoesNotExist:
            result = {'code': 11405, 'msg': '账号或密码错误'}
            return JsonResponse(result)

        m = hashlib.md5()
        m.update(password.encode())

        user = User.objects.get(account=account)

        if m.hexdigest() != user.password:
            result = {'code': 11405,'msg': '账号或密码错误'}
            return JsonResponse(result)

        result = {'code': 200,'msg': '登录成功','type':user.type,'account':user.account,'username':user.username}
        return JsonResponse(result)