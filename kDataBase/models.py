from django.db import models
from Users.models import User






#数据库记录表（个人+公共）
class KnowledgeBase(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='序号')  # 序号，主键自增
    kname = models.CharField(max_length=255, verbose_name='知识库名称')  # 知识库名称
    KTYPE_CHOICES = (
        ('personal', '个人'),
        ('public', '公共'),
    )
    ktype = models.CharField(max_length=10, choices=KTYPE_CHOICES, default='personal',
                             verbose_name='数据库类型')  # 数据库类型，个人、公共
    ksynopsis = models.CharField(max_length=255, verbose_name='知识库简介',default='None')  # 知识库名称
    uid = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所属用户id',
                            related_name='kbases')  # Foreign Key（User表的account），公共知识库也可以通过这个字段指定
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 创建时间

    class Meta:
        verbose_name = '知识库'
        verbose_name_plural = '知识库'







#个人数据库的上传记录表
class psl_upload_record(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='序号')  # 序号，主键自增
    file_name = models.CharField(max_length=255, verbose_name='文档名称')  # 文档名称
    file_type = models.CharField(max_length=50, default='未知', verbose_name='文件类别')  # 文件类别，默认未知
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')  # 上传时间
    status = models.CharField(max_length=10, choices=(('success', '成功'), ('failure', '失败')), default='success',
                              verbose_name='文件上传状态')  # 文件上传状态，成功/失败
    milvus_id = models.IntegerField(verbose_name='向量数据库id',blank=True)
    is_share = models.BooleanField(default=False, verbose_name='是否共享')  # 是否共享到公共知识库 是/否
    SHARE_STATUS_CHOICES = (
        ('pending', '待审核'),
        ('shared', '已共享'),
        ('failed', '审核失败'),
    )

    share_status = models.CharField(max_length=10, choices=SHARE_STATUS_CHOICES, default='pending', verbose_name='共享状态')
    kname = models.CharField(max_length=255, blank=True, verbose_name='公共知识库')
    kid = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, verbose_name='所属知识库id',
                            related_name='psl_records_k')
    uid = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所属用户id', related_name='psl_records_u')  # Foreign Key（User表的account）
    local_filename = models.CharField(max_length=255, unique=True, verbose_name='本地文件名')


    class Meta:
        verbose_name = '上传记录'
        verbose_name_plural = '上传记录'






#公共数据库的共享表
class pub_share_record(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='序号')
    file_name = models.CharField(max_length=255, verbose_name='文档名称')
    file_type = models.CharField(max_length=100, default='未知', verbose_name='文件类别')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    kname = models.CharField(max_length=255, verbose_name='公共知识库名称')
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已审核'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='审核状态')
    is_upload = models.BooleanField(default=False, verbose_name='是否上传')
    local_filename = models.CharField(max_length=255, verbose_name='本地存储文件名')
    uid = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='共享用户id', related_name='shares')
    kid = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, verbose_name='共享知识库id',
                            related_name='pub_share_record')

    class Meta:
        verbose_name = '公共知识库共享记录'
        verbose_name_plural = '公共知识库共享记录'



#公共数据库的上传记录表
class pub_upload_record(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='序号')
    file_name = models.CharField(max_length=255, verbose_name='文档名称')
    file_type = models.CharField(max_length=100, default='未知', verbose_name='文件类别')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    status = models.CharField(max_length=10, choices=(('success', '成功'), ('failure', '失败')), default='success',
                              verbose_name='文件上传状态')
    milvus_id = models.IntegerField(verbose_name='向量数据库id',blank=True)
    kid = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, verbose_name='所属知识库id',
                            related_name='pub_records_k')
    uid = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='上传用户的id', related_name='pub_records_u')

    class Meta:
        verbose_name = '公共知识库上传记录'
        verbose_name_plural = '公共知识库上传记录'