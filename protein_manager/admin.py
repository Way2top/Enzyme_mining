from django.contrib import admin
from .models import (
    ProteinBasicInfo, ProteinStructureInfo, ProteinSubcellularLocation,
    ProteinFunctionAnnotation, ProteinComprehensiveInfo, ProteinComprehensiveFunctionInfo,
    ProteinFunctionDomainRelation, ProteinStructureFunctionRelation, ProteinLocationSequenceRelation
)
from django.utils.html import format_html
import json


class ProteinBasicInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'IDName', 'display_sequence_features')
    search_fields = ('IDName',)
    
    def display_sequence_features(self, obj):
        features = obj.get_sequence_features()
        if not features:
            return "无特征信息"
        # 限制显示的特征数量，防止页面过长
        if len(features) > 5:
            return format_html("<br>".join(features[:5]) + f"<br>...(共{len(features)}项)")
        return format_html("<br>".join(features))
    
    display_sequence_features.short_description = "序列特征"


class ProteinStructureInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'IDName', 'display_embedding_preview', 'display_domains')
    search_fields = ('IDName',)
    
    def display_embedding_preview(self, obj):
        if not obj.Embedding:
            return "无嵌入向量"
        # 嵌入向量太长，只显示前面一部分
        preview = obj.Embedding[:100] + "..." if len(obj.Embedding) > 100 else obj.Embedding
        return preview
    
    def display_domains(self, obj):
        domains = obj.get_domains()
        if not domains:
            return "无结构域信息"
        return format_html("<br>".join(domains))
    
    display_embedding_preview.short_description = "嵌入向量预览"
    display_domains.short_description = "结构域"


class ProteinSubcellularLocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'IDName', 'SubcellularLocation')
    search_fields = ('IDName', 'SubcellularLocation')
    list_filter = ('SubcellularLocation',)


class ProteinFunctionAnnotationAdmin(admin.ModelAdmin):
    list_display = ('id', 'IDName', 'Function', 'EC', 'GO')
    search_fields = ('IDName', 'Function', 'EC', 'GO')
    list_filter = ('Function',)


class ProteinComprehensiveInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'IDName', 'Function', 'SubcellularLocation', 'display_sequence_features')
    search_fields = ('IDName', 'Function', 'SubcellularLocation')
    
    def display_sequence_features(self, obj):
        if not obj.SequenceFeature:
            return "无序列特征"
        preview = obj.SequenceFeature[:150] + "..." if len(obj.SequenceFeature) > 150 else obj.SequenceFeature
        return preview
    
    display_sequence_features.short_description = "序列特征预览"


class ProteinComprehensiveFunctionInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'IDName', 'display_function_preview', 'EC', 'GO', 'SubcellularLocation')
    search_fields = ('IDName', 'Function', 'EC', 'GO', 'SubcellularLocation')
    
    def display_function_preview(self, obj):
        if not obj.Function:
            return "无功能信息"
        preview = obj.Function[:150] + "..." if len(obj.Function) > 150 else obj.Function
        return preview
    
    display_function_preview.short_description = "功能信息预览"


class ProteinFunctionDomainRelationAdmin(admin.ModelAdmin):
    list_display = ('id', 'IDName', 'Function', 'Domain')
    search_fields = ('IDName', 'Function', 'Domain')
    list_filter = ('Function', 'Domain')


class ProteinStructureFunctionRelationAdmin(admin.ModelAdmin):
    list_display = ('id', 'IDName', 'display_embedding_preview', 'Function', 'Domain')
    search_fields = ('IDName', 'Function', 'Domain')
    list_filter = ('Function', 'Domain')
    
    def display_embedding_preview(self, obj):
        if not obj.Embedding:
            return "无嵌入向量"
        preview = obj.Embedding[:100] + "..." if len(obj.Embedding) > 100 else obj.Embedding
        return preview
    
    display_embedding_preview.short_description = "嵌入向量预览"


class ProteinLocationSequenceRelationAdmin(admin.ModelAdmin):
    list_display = ('id', 'IDName', 'SubcellularLocation', 'display_sequence_features')
    search_fields = ('IDName', 'SubcellularLocation')
    list_filter = ('SubcellularLocation',)
    
    def display_sequence_features(self, obj):
        if not obj.SequenceFeature:
            return "无序列特征"
        preview = obj.SequenceFeature[:100] + "..." if len(obj.SequenceFeature) > 100 else obj.SequenceFeature
        return preview
    
    display_sequence_features.short_description = "序列特征预览"


# 注册所有模型到管理界面
admin.site.register(ProteinBasicInfo, ProteinBasicInfoAdmin)
admin.site.register(ProteinStructureInfo, ProteinStructureInfoAdmin)
admin.site.register(ProteinSubcellularLocation, ProteinSubcellularLocationAdmin)
admin.site.register(ProteinFunctionAnnotation, ProteinFunctionAnnotationAdmin)
admin.site.register(ProteinComprehensiveInfo, ProteinComprehensiveInfoAdmin)
admin.site.register(ProteinComprehensiveFunctionInfo, ProteinComprehensiveFunctionInfoAdmin)
admin.site.register(ProteinFunctionDomainRelation, ProteinFunctionDomainRelationAdmin)
admin.site.register(ProteinStructureFunctionRelation, ProteinStructureFunctionRelationAdmin)
admin.site.register(ProteinLocationSequenceRelation, ProteinLocationSequenceRelationAdmin)
