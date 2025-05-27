from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .main_function import predict_enzyme_from_sequence, find_top5_similar_proteins
import pandas as pd
import os
from pathlib import Path
from index.models import VisitLog, FastaFile


# 辅助函数:记录访问日志
def record_visit(request, viewed_file_id=None, operation_type='page_view', request_data=None):
    """记录用户访问日志

    参数:
        request: HTTP请求对象
        viewed_file_id: 查看的文件ID (可选)
        operation_type: 操作类型，默认为'page_view'
        request_data: 请求数据，可以是字符串描述或字典 (可选)
    """
    ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    page_url = request.path

    viewed_file = None
    if viewed_file_id:
        try:
            viewed_file = FastaFile.objects.get(id=viewed_file_id)
        except FastaFile.DoesNotExist:
            pass

    # 如果请求数据是字典，将其转换为JSON字符串
    if request_data and isinstance(request_data, dict):
        try:
            import json
            request_data = json.dumps(request_data, ensure_ascii=False)
        except:
            # 如果JSON转换失败，则使用字符串描述
            request_data = str(request_data)

    visit_log = VisitLog.objects.create(
        ip_address=ip_address,
        user_agent=user_agent,
        viewed_file=viewed_file,
        page_url=page_url,
        operation_type=operation_type,
        request_data=request_data
    )
    return visit_log


# 创建视图函数用于渲染类似酶搜索页面
def similarenzyme_view(request):
    # 记录访问日志
    # record_visit(request, operation_type='page_view')
    return render(request, "mainsrc/similarenzyme.html")


# 创建 API 视图类，处理酶搜索请求
class EnzymeSearchAPIView(APIView):
    def post(self, request, *args, **kwargs):
        sequence = request.data.get('sequence')
        search_types = request.data.get('types', [])
        file_id = request.data.get('file_id')

        if not sequence:
            return Response({
                "success": False,
                "message": "蛋白质序列不能为空"
            }, status=status.HTTP_400_BAD_REQUEST)

        if not search_types:
            return Response({
                "success": False,
                "message": "请至少选择一种分析类型"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 记录访问日志
        # record_visit(
        #     request,
        #     file_id,
        #     operation_type='similar_search',
        #     request_data={
        #         'sequence_length': len(sequence),
        #         'search_types': search_types
        #     }
        # )

        try:
            results = {}

            # 判断是否为酶
            if "isEnzyme" in search_types:
                enzyme_result = predict_enzyme_from_sequence(sequence)
                if enzyme_result["status"] == "success":
                    results["isEnzyme"] = enzyme_result["prediction"] == "酶"
                    results["enzyme_confidence"] = enzyme_result["confidence"]

                    # 添加相似蛋白质的额外信息（如果有）
                    if "similar_info" in enzyme_result:
                        results["enzyme_similar_info"] = enzyme_result["similar_info"]
                else:
                    return Response({
                        "success": False,
                        "message": f"酶预测失败: {enzyme_result.get('message', '未知错误')}"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 寻找相似蛋白质
            if "similarProtein" in search_types:
                similar_result = find_top5_similar_proteins(sequence)
                if similar_result["status"] == "success":
                    # 获取相似蛋白质的详细信息
                    protein_ids = [protein["id"] for protein in similar_result["similar_proteins"]]

                    # 从similar_result中提取已经包含的额外信息
                    similar_proteins_with_info = similar_result["similar_proteins"]

                    # 获取蛋白质详细信息
                    protein_details = self.get_protein_details(protein_ids)

                    # 合并已有的详细信息和从数据库获取的信息
                    for i, detail in enumerate(protein_details):
                        if i < len(similar_proteins_with_info):
                            # 确保相似度信息被保留
                            detail['similarity'] = similar_proteins_with_info[i]['similarity']

                            # 添加额外信息（如果相似蛋白质结果中包含）
                            for key, value in similar_proteins_with_info[i].items():
                                if key not in ['id', 'similarity'] and key not in detail:
                                    detail[key] = value

                    results["results"] = protein_details
                else:
                    return Response({
                        "success": False,
                        "message": f"相似蛋白质搜索失败: {similar_result.get('message', '未知错误')}"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 设置成功标志
            results["success"] = True

            return Response(results)

        except Exception as e:
            print(f"处理蛋白质序列时出错: {str(e)}")
            return Response({
                "success": False,
                "message": f"处理失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_protein_details(self, protein_ids):
        """获取蛋白质详细信息"""
        try:
            # 从CSV文件加载蛋白质详细信息
            base_dir = Path(__file__).resolve().parent
            data_path = base_dir / 'data' / 'raw' / 'protein_data.csv'
            extra_info_path = base_dir / 'data' / 'raw' / 'protein_embedding_extra_info.csv'

            # 检查基本数据文件是否存在
            if not os.path.exists(data_path):
                # 如果找不到文件，使用示例数据
                return self.get_sample_protein_details(protein_ids)

            # 读取CSV文件
            df = pd.read_csv(data_path)

            # 尝试读取额外信息文件
            extra_info_df = None
            if os.path.exists(extra_info_path):
                extra_info_df = pd.read_csv(extra_info_path)
                print(f"成功加载额外蛋白质信息文件，包含 {len(extra_info_df)} 条记录")

            # 收集找到的蛋白质的详细信息
            protein_details = []
            for pid in protein_ids:
                # 在数据框中查找蛋白质
                protein_row = df[df['Protein_ID'] == pid]

                if not protein_row.empty:
                    # 将第一个匹配行转换为字典
                    protein_data = protein_row.iloc[0].to_dict()
                    # 将 Protein_ID 转换为 uniport_id（前端期望的格式）
                    protein_data['uniport_id'] = protein_data.pop('Protein_ID', pid)

                    # 添加额外信息（如果存在）
                    if extra_info_df is not None:
                        extra_row = extra_info_df[extra_info_df['ID'] == pid]
                        if not extra_row.empty:
                            # 添加额外信息中的所有列
                            for col in extra_row.columns:
                                if col != 'ID' and col not in protein_data:  # 避免覆盖已有信息
                                    protein_data[col] = extra_row.iloc[0][col]
                            print(f"为蛋白质 {pid} 添加了额外信息")

                    protein_details.append(protein_data)
                else:
                    # 如果在主数据文件中找不到蛋白质，尝试在额外信息文件中查找
                    extra_data = {'uniport_id': pid}
                    if extra_info_df is not None:
                        extra_row = extra_info_df[extra_info_df['ID'] == pid]
                        if not extra_row.empty:
                            # 添加额外信息中的所有列
                            for col in extra_row.columns:
                                if col != 'ID':  # 避免重复ID
                                    extra_data[col] = extra_row.iloc[0][col]
                            print(f"在额外信息文件中找到蛋白质 {pid}")

                    protein_details.append(extra_data)

            return protein_details

        except Exception as e:
            print(f"获取蛋白质详细信息时出错: {str(e)}")
            # 出错时返回示例数据
            return self.get_sample_protein_details(protein_ids)

    def get_sample_protein_details(self, protein_ids):
        """返回示例蛋白质详情，用于演示或测试"""
        sample_functions = [
            "催化碳水化合物的代谢过程，对于生物体能量供应至关重要",
            "催化蛋白质和氨基酸的合成和降解，参与细胞信号传导",
            "参与脂质代谢，控制细胞膜的组成和功能",
            "催化核酸的合成和修复，对于遗传信息的传递至关重要",
            "参与氧化还原反应，维持细胞内部的稳态"
        ]

        sample_ec = [
            ["1.1.1.1", "2.3.1.9"],
            ["3.4.21.4", "3.4.24.3"],
            ["2.7.1.1", "2.7.7.7"],
            ["4.1.1.1", "4.2.1.1"],
            ["1.14.13.1", "1.14.14.1"]
        ]

        sample_go = [
            ["GO:0016491", "GO:0004022"],
            ["GO:0008233", "GO:0004252"],
            ["GO:0016301", "GO:0005524"],
            ["GO:0003677", "GO:0003676"],
            ["GO:0016705", "GO:0020037"]
        ]

        protein_details = []
        for i, pid in enumerate(protein_ids):
            idx = i % 5  # 循环使用示例数据
            protein_data = {
                'uniport_id': pid,
                'Representation': f"[{idx * 0.1}, {idx * 0.2}, ...]",  # 省略大部分表征
                'Function': sample_functions[idx],
                'EC': sample_ec[idx],
                'GO': sample_go[idx],
                'Domain': [f"Domain{idx + 1}", f"Domain{idx + 2}"],
                'SubcellularLocation': ["细胞质", "细胞膜"][idx % 2],
                'SequenceFeature': f"活性位点: 第{100 + idx * 50}位氨基酸",
                'InterProFamily': f"IPR{10000 + idx}"
            }
            protein_details.append(protein_data)

        return protein_details 