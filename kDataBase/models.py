from django.db import models
from Users.models import User


# 数据库记录表（个人+公共）
class KnowledgeBase(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='序号')  # 序号，主键自增
    collection_name = models.CharField(max_length=255, verbose_name='集群名称')  # 集群名称
    TYPE_CHOICES = (
        ('personal', '个人'),
        ('public', '公共'),
    )
    collection_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='personal',
                                       verbose_name='集群类型')  # 集群类型，个人、公共
    partition_synopsis = models.CharField(max_length=255, verbose_name='知识库简介', default='暂无相关介绍')  # 知识库名称
    # 集群分区->不同的知识库->不同用户的partition_name可以重复 同一个用户的partition_name不能重复
    partition_nickname = models.CharField(max_length=255, verbose_name='用户的分区名称', default='未知知识库')
    partition_name = models.CharField(max_length=255, verbose_name='系统分区名称',
                                      default='_default')  # 知识库名称=分区名称 初始创建milvus默认一个'_default'分区
    uid = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所属用户id',
                            related_name='collection')  # Foreign Key（User表的account），公共知识库也可以通过这个字段指定
    file_nums = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 创建时间

    Partition_Status = (
        ('True', '激活'),
        ('False', '失效'),
    )
    p_status = models.CharField(max_length=10, choices=Partition_Status, default='True',
                                       verbose_name='知识库的状态')  # 集群类型，个人、公共

    class Meta:
        verbose_name = '知识库'
        verbose_name_plural = '知识库'


# 个人数据库文件上传记录

class psl_file_record(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='序号')  # 序号，主键自增
    file_name = models.CharField(max_length=255, verbose_name='文档名称')  # 文档名称
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')  # 上传时间
    status = models.CharField(max_length=10, choices=(('success', '成功'), ('failure', '失败'), ('middle', '存储中断'), ('false', '已失效')),
                              default='success',
                              verbose_name='文件上传状态')  # 文件上传状态，成功/失败
    collection_name = models.CharField(max_length=255, verbose_name='集群名称')
    partition_name = models.CharField(max_length=255, verbose_name='分区名称', default='_default')
    BOOLEAN_CHOICES = (
        ('True', '共享'),
        ('False', '不共享'),
    )
    is_share = models.CharField(max_length=10, choices=BOOLEAN_CHOICES, default='False',
                                verbose_name='是否共享')
    SHARE_STATUS_CHOICES = (
        ('pending', '待审核'),
        ('shared', '审核通过'),
        ('failed', '审核未通过'),
        ('False', '无需审核'),
        ('error', '审核出错'),

    )
    share_status = models.CharField(max_length=10, choices=SHARE_STATUS_CHOICES, default='False',
                                    verbose_name='共享状态')
    sid = models.CharField(max_length=255, verbose_name='共享集群', default='None')
    uid = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所属用户id',
                            related_name='psl_file_u')  # Foreign Key（User表的account）
    local_filename = models.CharField(max_length=255, blank=True, verbose_name='本地文件名')

    partition_id = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, verbose_name='分区id',
                                     related_name='psl_records_k2')
    # milvus_id_list 向量数据库单文件存储的全部id
    milvus_id_list = models.TextField(verbose_name='milvus返回id', null=True)
    milvus_id_head = models.CharField(max_length=100, verbose_name='milvus返回起始id', null=True)
    milvus_id_tail = models.CharField(max_length=100, verbose_name='milvus返回结尾id', null=True)

    Partition_Status = (
        ('True', '激活'),
        ('False', '失效'),
    )

    class Meta:
        verbose_name = '个人数据库文件记录'
        verbose_name_plural = '个人数据库文件记录'


# 个人数据库的上传记录表
class psl_upload_record(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='序号')  # 序号，主键自增
    file_name = models.CharField(max_length=255, verbose_name='文档名称')  # 文档名称
    # file_type = models.CharField(max_length=50, default='未知', verbose_name='文件类别')  # 文件类别，默认未知
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')  # 上传时间
    status = models.CharField(max_length=10, choices=(('success', '成功'), ('failure', '失败'), ('middle', '存储中断'),('false', '已失效')),
                              default='success',
                              verbose_name='文件上传状态')  # 文件上传状态，成功/失败
    collection_name = models.CharField(max_length=255, verbose_name='集群名称')  # 集群名称
    partition_name = models.CharField(max_length=255, verbose_name='分区名称', default='_default')

    milvus_id = models.CharField(max_length=255, verbose_name='向量数据库id', blank=True)
    BOOLEAN_CHOICES = (
        ('True', '共享'),
        ('False', '不共享'),
    )
    is_share = models.CharField(max_length=10, choices=BOOLEAN_CHOICES, default='False',
                                verbose_name='是否共享')  # 集群类型，个人、公共
    SHARE_STATUS_CHOICES = (
        ('pending', '待审核'),
        ('shared', '审核通过'),
        ('failed', '审核未通过'),
        ('False', '无需审核'),
        ('error', '审核出错'),

    )
    sid = models.CharField(max_length=255, verbose_name='共享集群ID', default='None')  # 要共享的集群名称
    share_status = models.CharField(max_length=10, choices=SHARE_STATUS_CHOICES, default='False',
                                    verbose_name='共享状态')
    partition_id = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, verbose_name='分区id',
                                     related_name='psl_records_k1')
    uid = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所属用户id',
                            related_name='psl_records_u')  # Foreign Key（User表的account）
    local_filename = models.CharField(max_length=255, blank=True, verbose_name='本地文件名')

    file_id = models.ForeignKey(psl_file_record, on_delete=models.CASCADE, verbose_name='个人文件id',
                                related_name='psl_file_milvusid', null=True)

    class Meta:
        verbose_name = '上传记录'
        verbose_name_plural = '上传记录'


# 公共数据库的共享表
class pub_share_record(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='序号')
    file_name = models.CharField(max_length=255, verbose_name='文档名称')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    collection_id = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, verbose_name='共享分区对象',
                                      related_name='pub_share_record')
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已审核'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='审核状态')
    local_filename = models.CharField(max_length=255, verbose_name='本地存储文件名')
    UPLOAD_CHOICES = (
        ('True', '同意上传'),
        ('False', '未通过'),
        ('Unknow', '未知'),
        ('error', '审核出错'),
    )
    is_upload = models.CharField(max_length=10, verbose_name='是否上传', default='Unknow')
    uid = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='共享用户id', related_name='shares')
    file_id = models.ForeignKey(psl_file_record, on_delete=models.CASCADE, verbose_name='个人文件id',
                                related_name='share_file_milvusid', null=True)

    class Meta:
        verbose_name = '公共知识库共享记录'
        verbose_name_plural = '公共知识库共享记录'


# 公共数据库文件上传记录
class pub_file_record(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='序号')  # 序号，主键自增
    file_name = models.CharField(max_length=255, verbose_name='文档名称')  # 文档名称
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')  # 上传时间
    status = models.CharField(max_length=10, choices=(('success', '成功'), ('failure', '失败'), ('middle', '存储中断'),('false', '已失效')),
                              default='success',
                              verbose_name='文件上传状态')  # 文件上传状态，成功/失败
    collection_name = models.CharField(max_length=255, verbose_name='集群名称', default="pub_kdb")
    uid = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所属用户id',
                            related_name='pub_file_u')  # Foreign Key（User表的account）
    local_filename = models.CharField(max_length=255, blank=True, verbose_name='本地文件名')
    partition_name = models.CharField(max_length=255, verbose_name='分区名称', default='_default')
    partition_id = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, verbose_name='分区id',
                                     related_name='pub_file_records', default='')
    # milvus_id_list 向量数据库单文件存储的全部id
    milvus_id_list = models.TextField(verbose_name='milvus返回id', null=True)

    milvus_id_head = models.CharField(max_length=100, verbose_name='milvus返回起始id', null=True)
    milvus_id_tail = models.CharField(max_length=100, verbose_name='milvus返回结尾id', null=True)

    class Meta:
        verbose_name = '公共数据库文件记录'
        verbose_name_plural = '公共数据库文件记录'


# 公共数据库的上传记录表
class pub_upload_record(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='序号')
    file_name = models.CharField(max_length=255, verbose_name='文档名称')
    # file_type = models.CharField(max_length=100, default='未知', verbose_name='文件类别')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    collection_name = models.CharField(max_length=255, verbose_name='集群名称', default='pub_kdb')
    # milvus里面的分区id
    partition_name = models.CharField(max_length=255, verbose_name='分区名称', default='_default')
    status = models.CharField(max_length=10,
                              choices=(('success', '成功'), ('failure', '失败'), ('milddle', '存储中断'),('false', '已失效')),
                              default='success',
                              verbose_name='文件上传状态')
    milvus_id = models.CharField(max_length=255, verbose_name='向量数据库id', blank=True)
    # 公共知识库没有分区 直接指向collection_name即可
    uid = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='上传用户的id', related_name='pub_records_u')
    local_filename = models.CharField(max_length=255, blank=True, verbose_name='本地文件名')
    partition_id = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, verbose_name='分区id',
                                     related_name='pub_records_k', default='')

    file_id = models.ForeignKey(pub_file_record, on_delete=models.CASCADE, verbose_name='公共文件id',
                                related_name='pub_file_milvusid', null=True)

    class Meta:
        verbose_name = '公共知识库上传记录'
        verbose_name_plural = '公共知识库上传记录'




