from django.db import models
from django.utils.html import format_html
import json

class ProteinBasicInfo(models.Model):
    """蛋白质基本信息表"""
    id = models.AutoField(primary_key=True)
    IDName = models.TextField("蛋白质ID", blank=True, null=True)
    SequenceFeature = models.TextField("序列特征", blank=True, null=True)
    
    def get_sequence_features(self):
        """将JSON格式的序列特征转换为列表"""
        if not self.SequenceFeature:
            return []
        try:
            # 处理数据中的单引号，确保它可以被解析为JSON
            cleaned_data = self.SequenceFeature.replace("'", '"')
            return json.loads(cleaned_data)
        except json.JSONDecodeError:
            return []
    
    def __str__(self):
        return self.IDName or str(self.id)
    
    class Meta:
        verbose_name = "蛋白质基本信息"
        verbose_name_plural = "蛋白质基本信息"
        db_table = "protein_basic_info"


class ProteinStructureInfo(models.Model):
    """蛋白质结构信息表"""
    id = models.AutoField(primary_key=True)
    IDName = models.TextField("蛋白质ID", blank=True, null=True)
    Embedding = models.TextField("嵌入向量", blank=True, null=True)
    Domain = models.TextField("结构域", blank=True, null=True)
    
    def get_domains(self):
        """将JSON格式的域信息转换为列表"""
        if not self.Domain:
            return []
        try:
            cleaned_data = self.Domain.replace("'", '"')
            return json.loads(cleaned_data)
        except json.JSONDecodeError:
            return []
    
    def __str__(self):
        return self.IDName or str(self.id)
    
    class Meta:
        verbose_name = "蛋白质结构信息"
        verbose_name_plural = "蛋白质结构信息"
        db_table = "protein_structure_info"


class ProteinSubcellularLocation(models.Model):
    """蛋白质亚细胞定位表"""
    id = models.AutoField(primary_key=True)
    IDName = models.TextField("蛋白质ID", blank=True, null=True)
    SubcellularLocation = models.TextField("亚细胞定位", blank=True, null=True)
    
    def __str__(self):
        return f"{self.IDName or str(self.id)} - {self.SubcellularLocation or '未知'}"
    
    class Meta:
        verbose_name = "蛋白质亚细胞定位"
        verbose_name_plural = "蛋白质亚细胞定位"
        db_table = "protein_subcellular_location"


class ProteinFunctionAnnotation(models.Model):
    """蛋白质功能注释表"""
    id = models.AutoField(primary_key=True)
    IDName = models.TextField("蛋白质ID", blank=True, null=True)
    Function = models.TextField("功能", blank=True, null=True)
    EC = models.TextField("EC号", blank=True, null=True)
    GO = models.TextField("GO注释", blank=True, null=True)
    
    def __str__(self):
        return f"{self.IDName or str(self.id)} - {self.Function or '未知功能'}"
    
    class Meta:
        verbose_name = "蛋白质功能注释"
        verbose_name_plural = "蛋白质功能注释"
        db_table = "protein_function_annotation"


class ProteinComprehensiveInfo(models.Model):
    """蛋白质综合信息表"""
    id = models.AutoField(primary_key=True)
    IDName = models.TextField("蛋白质ID", blank=True, null=True)
    Function = models.TextField("功能", blank=True, null=True)
    SubcellularLocation = models.TextField("亚细胞定位", blank=True, null=True)
    SequenceFeature = models.TextField("序列特征", blank=True, null=True)
    
    def __str__(self):
        return self.IDName or str(self.id)
    
    class Meta:
        verbose_name = "蛋白质综合信息"
        verbose_name_plural = "蛋白质综合信息"
        db_table = "protein_comprehensive_info"


class ProteinComprehensiveFunctionInfo(models.Model):
    """蛋白质综合功能信息表"""
    id = models.AutoField(primary_key=True)
    IDName = models.TextField("蛋白质ID", blank=True, null=True)
    Function = models.TextField("功能信息", blank=True, null=True)
    EC = models.TextField("EC号", blank=True, null=True)
    GO = models.TextField("GO注释", blank=True, null=True)
    SubcellularLocation = models.TextField("亚细胞定位", blank=True, null=True)
    
    def __str__(self):
        return self.IDName or str(self.id)
    
    class Meta:
        verbose_name = "蛋白质综合功能信息"
        verbose_name_plural = "蛋白质综合功能信息"
        db_table = "protein_comprehensive_function_info"


class ProteinFunctionDomainRelation(models.Model):
    """蛋白质功能-结构域关系表"""
    id = models.AutoField(primary_key=True)
    IDName = models.TextField("蛋白质ID", blank=True, null=True)
    Function = models.TextField("功能", blank=True, null=True)
    Domain = models.TextField("结构域", blank=True, null=True)
    
    def __str__(self):
        return f"{self.IDName or str(self.id)} - {self.Function or '未知'} - {self.Domain or '未知'}"
    
    class Meta:
        verbose_name = "蛋白质功能-结构域关系"
        verbose_name_plural = "蛋白质功能-结构域关系"
        db_table = "protein_function_domain_relation"


class ProteinStructureFunctionRelation(models.Model):
    """蛋白质结构-功能关系表"""
    id = models.AutoField(primary_key=True)
    IDName = models.TextField("蛋白质ID", blank=True, null=True)
    Embedding = models.TextField("嵌入向量", blank=True, null=True)
    Function = models.TextField("功能", blank=True, null=True)
    Domain = models.TextField("结构域", blank=True, null=True)
    
    def __str__(self):
        return f"{self.IDName or str(self.id)} - {self.Function or '未知功能'}"
    
    class Meta:
        verbose_name = "蛋白质结构-功能关系"
        verbose_name_plural = "蛋白质结构-功能关系"
        db_table = "protein_structure_function_relation"


class ProteinLocationSequenceRelation(models.Model):
    """蛋白质定位-序列关系表"""
    id = models.AutoField(primary_key=True)
    IDName = models.TextField("蛋白质ID", blank=True, null=True)
    SubcellularLocation = models.TextField("亚细胞定位", blank=True, null=True)
    SequenceFeature = models.TextField("序列特征", blank=True, null=True)
    
    def __str__(self):
        return f"{self.IDName or str(self.id)} - {self.SubcellularLocation or '未知位置'}"
    
    class Meta:
        verbose_name = "蛋白质定位-序列关系"
        verbose_name_plural = "蛋白质定位-序列关系"
        db_table = "protein_location_sequence_relation"
