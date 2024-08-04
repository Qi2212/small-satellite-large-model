from django.db import models

# Create your models here.

class User(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='序号')  # 序号，主键自增
    type = models.CharField(max_length=10, choices=(('normal', '普通用户'), ('admin', '超级管理员')), default='normal',
                            verbose_name='用户类型')  # 用户类型，普通用户/超级管理员
    username = models.CharField(max_length=100, verbose_name='用户名')  # 用户名，登录成功返回用户名
    account = models.CharField(max_length=20, unique=True, verbose_name='用户账号')  # 用户账号-手机号-注意校验
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 创建时间
    status = models.BooleanField(default=True, verbose_name='用户状态')  # 用户状态-伪删除  ，布尔类型
    password = models.CharField(max_length=32, editable=False, verbose_name='密码')  # 密码，实际应用中应存储密码的哈希值

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'