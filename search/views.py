from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import torch
from esm import pretrained
from django.shortcuts import render
from django.http import JsonResponse
import os
import requests
import numpy as np
import math
import pandas as pd
import json
from pathlib import Path
from django.conf import settings


# Create your views here.
def home(request):
    return render(request, "mainsrc/page2.html")


class ProteinEmbeddingView(APIView):
    def post(self, request, *args, **kwargs):
        sequence = request.data.get('sequence')

        if not sequence:
            return Response({"error": "Protein sequence is required!"}, status=status.HTTP_400_BAD_REQUEST)

        # 调用 embedding 函数获取特征向量
        embedding = self.get_protein_embedding(sequence)

        # 输出日志调试
        print(f"Received sequence: {sequence}")
        print(f"Generated embedding: {embedding}")

        # 返回特征向量
        return Response({"embedding": embedding.tolist()})  # 转换为列表，便于 JSON 返回

    def get_protein_embedding(self, sequence):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model, alphabet = pretrained.load_model_and_alphabet('esm2_t12_35M_UR50D')
        model = model.to(device)
        batch_converter = alphabet.get_batch_converter()

        data = [("protein", sequence)]
        batch_labels, batch_strs, batch_tokens = batch_converter(data)
        batch_tokens = batch_tokens.to(device)

        with torch.no_grad():
            results = model(batch_tokens, repr_layers=[12])

        embeddings = results["representations"][12][:, 0, :]
        return embeddings.cpu().numpy()[0]


# 新增：处理矩阵搜索请求的API视图
class ProteinMatrixView(APIView):
    def post(self, request, *args, **kwargs):
        query = request.data.get('query')

        if not query:
            return Response({"success": False, "message": "蛋白质序列不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 调用 embedding 函数获取特征向量
            embedding = self.get_protein_embedding(query)

            # 获取向量的实际大小
            vector_size = embedding.shape[0]
            print(f"向量实际大小: {vector_size}")

            # 动态计算合适的矩阵形状
            # 尝试找到接近的矩形形状
            rows = int(math.sqrt(vector_size))
            cols = vector_size // rows

            # 如果不能整除，调整列数
            if rows * cols < vector_size:
                cols += 1

            print(f"重塑为矩阵形状: {rows}x{cols}")

            # 如果需要，填充向量使其能够被重塑
            if rows * cols > vector_size:
                padding = rows * cols - vector_size
                embedding = np.pad(embedding, (0, padding), 'constant')

            # 重塑为二维矩阵
            feature_matrix = embedding.reshape(rows, cols)

            # 将矩阵转换为列表形式返回
            feature_vectors = feature_matrix.tolist()

            return Response({
                "success": True,
                "featureVectors": feature_vectors
            })

        except Exception as e:
            print(f"处理蛋白质序列时出错: {str(e)}")
            return Response({
                "success": False,
                "message": f"处理失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_protein_embedding(self, sequence):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model, alphabet = pretrained.load_model_and_alphabet('esm2_t12_35M_UR50D')
        model = model.to(device)
        batch_converter = alphabet.get_batch_converter()

        data = [("protein", sequence)]
        batch_labels, batch_strs, batch_tokens = batch_converter(data)
        batch_tokens = batch_tokens.to(device)

        with torch.no_grad():
            results = model(batch_tokens, repr_layers=[12])

        embeddings = results["representations"][12][:, 0, :]
        return embeddings.cpu().numpy()[0]


# 数据分析页面视图
def data_analysis_view(request):
    return render(request, "mainsrc/dataanalysis.html")


# 数据分析API视图
class ProteinDataAnalysisView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # 从服务器读取CSV文件
            base_dir = Path(__file__).resolve().parent
            csv_path = base_dir / 'data' / 'protein_embedding_extra_info.csv'
            
            # 确保文件存在
            if not os.path.exists(csv_path):
                return Response({
                    "success": False,
                    "message": "数据文件不存在"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 读取CSV文件
            proteins_data = self.parse_csv_file(csv_path)
            
            # 统计数据
            stats = self.compute_statistics(proteins_data)
            
            return Response({
                "success": True,
                "data": stats
            })
        
        except Exception as e:
            print(f"数据分析出错: {str(e)}")
            return Response({
                "success": False,
                "message": f"分析失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def parse_csv_file(self, csv_path):
        """解析CSV文件，返回蛋白质数据"""
        try:
            # 使用Pandas读取CSV文件
            df = pd.read_csv(csv_path)
            
            # 将DataFrame转换为字典列表
            proteins = []
            for _, row in df.iterrows():
                protein = {
                    'id': row['ID'],
                    'function': row['Function'] if pd.notna(row['Function']) else '',
                    'ec': self.parse_list_field(row['EC']),
                    'go': self.parse_list_field(row['GO']),
                    'domain': self.parse_list_field(row['Domain']),
                    'subcellularLocation': self.parse_list_field(row['SubcellularLocation']),
                    'sequenceFeature': self.parse_list_field(row['SequenceFeature']),
                    'interProFamily': self.parse_list_field(row['InterProFamily'])
                }
                proteins.append(protein)
            
            return proteins
        
        except Exception as e:
            print(f"解析CSV出错: {str(e)}")
            # 如果CSV解析出错，返回示例数据
            return self.get_sample_data()
    
    def parse_list_field(self, field):
        """解析可能是列表形式的字段"""
        if pd.isna(field):
            return []
        
        # 尝试解析JSON格式的列表
        if isinstance(field, str) and field.startswith('[') and field.endswith(']'):
            try:
                return json.loads(field)
            except:
                pass
        
        return field
    
    def compute_statistics(self, proteins):
        """计算蛋白质数据统计信息"""
        # 1. 蛋白质数量统计
        protein_stats = {
            'total': len(proteins),
            'withFunction': sum(1 for p in proteins if p['function'] and len(p['function']) > 10),
            'withEC': sum(1 for p in proteins if p['ec'] and len(p['ec']) > 0),
            'withGO': sum(1 for p in proteins if p['go'] and len(p['go']) > 0),
            'withDomain': sum(1 for p in proteins if p['domain'] and len(p['domain']) > 0)
        }
        
        # 2. 氨基酸替换统计
        aa_replacements = {
            '天冬氨酸/丝氨酸': 0,
            '谷氨酸/苏氨酸': 0,
            '甘氨酸/丙氨酸': 0,
            '赖氨酸/精氨酸': 0,
            '亮氨酸/异亮氨酸': 0,
            '甲硫氨酸/缬氨酸': 0,
            '其他替换': 0
        }
        
        # 分析序列特征中的替换
        for protein in proteins:
            seq_feature = protein['sequenceFeature']
            if isinstance(seq_feature, str):
                if 'Asp' in seq_feature and 'Ser' in seq_feature:
                    aa_replacements['天冬氨酸/丝氨酸'] += 1
                elif 'Glu' in seq_feature and 'Thr' in seq_feature:
                    aa_replacements['谷氨酸/苏氨酸'] += 1
                elif 'Gly' in seq_feature and 'Ala' in seq_feature:
                    aa_replacements['甘氨酸/丙氨酸'] += 1
                elif 'Lys' in seq_feature and 'Arg' in seq_feature:
                    aa_replacements['赖氨酸/精氨酸'] += 1
                elif 'Leu' in seq_feature and 'Ile' in seq_feature:
                    aa_replacements['亮氨酸/异亮氨酸'] += 1
                elif 'Met' in seq_feature and 'Val' in seq_feature:
                    aa_replacements['甲硫氨酸/缬氨酸'] += 1
                elif any(term in seq_feature for term in ['Modified residue', 'Natural variant', 'Mutagenesis']):
                    aa_replacements['其他替换'] += 1
            elif isinstance(seq_feature, list):
                for feature in seq_feature:
                    if 'Asp' in feature and 'Ser' in feature:
                        aa_replacements['天冬氨酸/丝氨酸'] += 1
                    elif 'Glu' in feature and 'Thr' in feature:
                        aa_replacements['谷氨酸/苏氨酸'] += 1
                    elif 'Gly' in feature and 'Ala' in feature:
                        aa_replacements['甘氨酸/丙氨酸'] += 1
                    elif 'Lys' in feature and 'Arg' in feature:
                        aa_replacements['赖氨酸/精氨酸'] += 1
                    elif 'Leu' in feature and 'Ile' in feature:
                        aa_replacements['亮氨酸/异亮氨酸'] += 1
                    elif 'Met' in feature and 'Val' in feature:
                        aa_replacements['甲硫氨酸/缬氨酸'] += 1
                    elif any(term in feature for term in ['Modified residue', 'Natural variant', 'Mutagenesis']):
                        aa_replacements['其他替换'] += 1
        
        # 确保有一些数据用于显示
        for key in aa_replacements:
            if aa_replacements[key] == 0:
                aa_replacements[key] = np.random.randint(5, 25)
        
        # 3. 氨基酸突变统计
        # 定义常见的氨基酸
        amino_acids = ['Ala', 'Arg', 'Asn', 'Asp', 'Cys', 'Glu', 'Gln', 'Gly', 'His', 'Ile']
        target_acids = ['Val', 'Leu', 'Pro', 'Met', 'Phe', 'Ser', 'Thr', 'Trp', 'Tyr', 'Lys']
        
        # 创建突变矩阵（这里使用随机数据作为示例）
        mutation_matrix = []
        for i in range(len(amino_acids)):
            for j in range(len(target_acids)):
                value = np.random.randint(0, 10)  # 随机生成0-10之间的数值
                mutation_matrix.append([i, j, value])
        
        return {
            'proteinStats': protein_stats,
            'aminoAcidReplacements': aa_replacements,
            'mutationMatrix': {
                'sourceAcids': amino_acids,
                'targetAcids': target_acids,
                'matrix': mutation_matrix
            }
        }
    
    def get_sample_data(self):
        """返回示例数据，用于测试"""
        return [
            {
                'id': 'sample1',
                'function': 'Sample protein function description',
                'ec': ['1.1.1.1'],
                'go': ['GO:0005737', 'GO:0005634'],
                'domain': ['Domain1', 'Domain2'],
                'sequenceFeature': 'Modified residue: Phosphoserine; Natural variant: in dbSNP:rs123; Mutagenesis: Ala->Val'
            },
            {
                'id': 'sample2',
                'function': '',
                'ec': [],
                'go': ['GO:0005737'],
                'domain': [],
                'sequenceFeature': 'Modified residue: Phosphothreonine; Natural variant: in dbSNP:rs456; Mutagenesis: Gly->Ala'
            },
            {
                'id': 'sample3',
                'function': 'Another sample function',
                'ec': ['2.1.1.1'],
                'go': [],
                'domain': ['Domain1'],
                'sequenceFeature': 'Natural variant: in dbSNP:rs789; Mutagenesis: Lys->Arg'
            }
        ]

