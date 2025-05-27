from django.db import models
from django.utils import timezone
from django.conf import settings
import os

# Create your models here.

# 存储FASTA文件信息的模型
class FastaFile(models.Model):
    name = models.CharField(max_length=255, verbose_name='文件名称')
    description = models.TextField(blank=True, null=True, verbose_name='文件描述')
    file_path = models.CharField(max_length=255, verbose_name='文件路径')
    upload_date = models.DateTimeField(default=timezone.now, verbose_name='上传时间')
    
    def __str__(self):
        return self.name
    
    def get_absolute_path(self):
        """获取文件的绝对路径"""
        if os.path.isabs(self.file_path):
            return self.file_path
        return os.path.join(settings.BASE_DIR, self.file_path)
    
    class Meta:
        verbose_name = 'FASTA文件'
        verbose_name_plural = 'FASTA文件'

# 访问记录模型
class VisitLog(models.Model):
    OPERATION_CHOICES = [
        ('page_view', '页面访问'),
        ('protein_embedding', '蛋白质嵌入'),
        ('matrix_view', '矩阵查看'),
        ('data_analysis', '数据分析'),
        ('similar_search', '相似酶搜索'),
        ('upload_file', '文件上传'),
        ('other', '其他操作'),
    ]
    
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.TextField(verbose_name='用户代理')
    visit_time = models.DateTimeField(default=timezone.now, verbose_name='访问时间')
    viewed_file = models.ForeignKey(FastaFile, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='查看的文件')
    page_url = models.CharField(max_length=255, blank=True, null=True, verbose_name='访问页面URL')
    operation_type = models.CharField(max_length=50, choices=OPERATION_CHOICES, default='page_view', verbose_name='操作类型')
    request_data = models.TextField(blank=True, null=True, verbose_name='请求数据')
    
    def __str__(self):
        return f"{self.ip_address} - {self.operation_type} - {self.visit_time}"
    
    class Meta:
        verbose_name = '访问记录'
        verbose_name_plural = '访问记录'
        indexes = [
            models.Index(fields=['visit_time']),
            models.Index(fields=['operation_type']),
        ]

