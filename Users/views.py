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


def login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        try:
            session_key = request.COOKIES.get('sessionid')
            session_id=Session.objects.get(session_key=session_key)
            if session_id:
                return view_func(request, *args, **kwargs)
            else:
                result = {'code': 11401, 'msg': '未登录'}
                return JsonResponse(result)
        except Exception as e:
            print(f"{e}")
            result = {'code': 11401, 'msg': '未登录'}
            return JsonResponse(result)
    return _wrapped_view
    
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
        if password_1 != password_2:
            result = {'code': 11405, 'msg': '两次密码输入不一致'}
            return JsonResponse(result)

        if re.match(r'^[1][3-9]\d{9}$|^([6|9])\d{7}$|^[0][9]\d{8}$|^[6]([8|6])\d{5}$',account) == None:
            result = {'code':11406, 'msg': '用户账号格式有误'}
            return JsonResponse(result)
        old_users = User.objects.filter(account=account)
        if old_users:
            result = {'code': 11407, 'msg': '账号已经存在'}
            return JsonResponse(result)
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

        request.session['account'] = account
        request.session.save()
        result = {'code': 200,'msg': '登录成功','type':user.type,'account':user.account,'username':user.username}
        return JsonResponse(result)


class Logoutview(View):
    def post(self, request):
        session_key = request.COOKIES.get('sessionid')
        if session_key:
            session_id=Session.objects.get(session_key=session_key)
            session_id.delete()
            result = {'code': 200, 'msg': '退出成功'}
            response=JsonResponse(result)
            response.delete_cookie('sessionid')
            return response
        else:
            result = {'code': 11401, 'msg': '未知错误'}
            return JsonResponse(result)