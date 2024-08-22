# 创建人：QI-BRO
# 开发时间：2024-08-12  14:22
from django.urls import path

from kDataBase import views
urlpatterns = [
    #个人新建知识库
    path('psl/create_db', views.psl_create_knowledge_views),
    #公共新建知识库
    path('pub/create_db', views.pub_create_knowledge_views),
    #删除个人知识库
    path('psl/del_db', views.psl_create_knowledge_views),
    #个人数据库上传
    path('psl/upload', views.psl_upload),
    #公共数据库上传
    path('pub/upload', views.pub_upload),
    #个人数据库上传记录
    path('psl/records', views.psl_upload_records),
    #个人知识库信息
    path('psl/info', views.psl_partition_info),
    #公共知识库信息
    path('pub/info', views.pub_partition_info),
    #共享审核
    path('pub/check', views.psl_share_records),
    #操作共享
    path('pub/operate', views.share_operate),
    #公共数据库上传记录
    path('pub/records', views.pub_upload_records),
    #个人数据库文件记录
    path('psl/filerecords', views.psl_file_records),
    #个人+公共数据库
    path('both/kdbrecords',views.partition_info),
    #全部知识库选择
    path('all/kdbs',views.partition_base_info),
    #admin的个人+公共知识库上传文件记录
    path('adm/filerecords',views.admin_file_records),
    #个人知识库的文件上传记录
    path('psl/kbasefiles',views.psl_pid_filerecord),
    #公共知识库的文件上传记录
    path('pub/kbasefiles',views.pub_pid_filerecord),
    #重命名知识库
    path('both/renamekbase',views.rename_kbase),
    #删除文件语料
    path('both/delfilerecord',views.file_delete),
    #删除知识库
    path('both/delpartition',views.delete_kbase),

]