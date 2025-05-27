from django.contrib import admin
from .models import User, Protein
from django.contrib import admin
from .models import Protein, ProteinCategory

# Register your models here.

@admin.register(User)
class User(admin.ModelAdmin):
    # 设置页面可以展示的字段
    # get_image_tag 是在模型中设置的显示图片函数，一定要添加上 不然后台不会显示
    list_display = ('username', 'head_img', 'get_image_tag')
    # 默认不配置的话，第一个字段会存在链接到记录编辑页面
    # list_display_links = None
    list_display_links = ('username',)


class ProteinAdmin(admin.ModelAdmin):
    # 后台展示的字段
    list_display = ('name', 'sequence', 'function', 'category', 'created_at')

    # 可以过滤蛋白质的类别和创建时间
    list_filter = ('created_at', 'category')

    # 搜索字段，可以搜索蛋白质的名称和功能
    search_fields = ('name', 'function')

    # 批量操作
    actions = ['mark_as_antibody']

    def mark_as_antibody(self, request, queryset):
        queryset.update(category=Protein.ANTIBODY)

    mark_as_antibody.short_description = "标记为抗体"  # 批量操作的描述


# 注册模型到后台
admin.site.register(Protein, ProteinAdmin)



class ProteinAdmin(admin.ModelAdmin):
    list_display = ('name', 'sequence', 'function', 'category', 'created_at')
    list_filter = ('created_at', 'category')  # 根据蛋白质分类过滤
    search_fields = ('name', 'function')
    actions = ['mark_as_antibody']

    def mark_as_antibody(self, request, queryset):
        queryset.update(category=ProteinCategory.objects.get(name='Antibody'))
    mark_as_antibody.short_description = "标记为抗体"

class ProteinCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

# 注册模型到后台

admin.site.register(ProteinCategory, ProteinCategoryAdmin)

