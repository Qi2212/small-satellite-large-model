from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
import hashlib
import json
from django.http import JsonResponse
from django.views import View
from user.models import UserProfile
from djangoProject import settings
from django.contrib.sessions.models import Session



class LoginView(View):
    def post(self, request):
        json_obj = json.loads(request.body)
        username = json_obj.get('username')
        password = json_obj.get('password')
        #11开头 11401 11402
        if username == "":
            result = {'code': 11401, 'msg': '请输入用户名'}
            return JsonResponse(result)
        if password == "":
            result = {'code': 11402, 'error': '请输入密码'}
            return JsonResponse(result)
        try:
            user = UserProfile.objects.get(username=username)
        except Exception as e:
            result = {'code': 11403, 'error': '用户名不存在'}
            return JsonResponse(result)
        m = hashlib.md5()
        m.update(password.encode())
        password_m = m.hexdigest()
        if password_m != user.password:
            result = {'code': 403, 'error': '用户名或密码错误','type':'','account':''}
            return JsonResponse(result)


