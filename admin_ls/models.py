from django.db import models

# Create your models here.
# Create your models here.

from django.db import models
from stdimage import StdImageField
from django.utils.safestring import mark_safe


# 用户表
class User(models.Model):
    username = models.CharField(verbose_name='用户名', unique=True, max_length=64)
    head_img = StdImageField(upload_to='path/to/', blank=True, delete_orphans=True,
                             verbose_name=u'url')

    class Meta:
        db_table = 'user_info'
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'

    # 在后台列表显示图片
    def get_image_tag(self):
        if self.head_img:
            return mark_safe('<img src="%s" width="60" height="75" />' % self.head_img.url)
        else:
            return ' '

    get_image_tag.short_description = 'Photo'
    get_image_tag.admin_order_field = 'name'

    def __str__(self):
        return self.username



class ProteinCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)  # 分类名称
    description = models.TextField(null=True, blank=True)  # 分类描述

    def __str__(self):
        return self.name



class Protein(models.Model):
    ENZYME = 'enzyme'
    ANTIBODY = 'antibody'
    PROTEIN_TYPE_CHOICES = [
        (ENZYME, 'Enzyme'),
        (ANTIBODY, 'Antibody'),
    ]

    name = models.CharField(max_length=255)
    sequence = models.TextField()  # 蛋白质序列
    function = models.TextField()  # 功能描述
    source = models.CharField(max_length=255, null=True, blank=True)  # 来源
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(ProteinCategory, on_delete=models.SET_NULL, null=True, blank=True)  # 关联分类

    def __str__(self):
        return self.name



