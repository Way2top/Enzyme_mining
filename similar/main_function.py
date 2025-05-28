# 功能1和功能2的传参均为：蛋白质序列号
# 功能1：判断该蛋白质是否为酶，直接调用predict_enzyme_from_sequence(sequence: str)，返回"酶"或者"非酶"
# 功能2：找出库中top5相似的蛋白质，find_top5_similar_proteins(sequence: str)，返回一个列表（包含5个蛋白质的Uniport_ID）

import torch
import numpy as np
from pathlib import Path
import os
import pandas as pd
from .src.model import ProteinClassifier
from .src.utils import load_model, compute_similarity
from .src.data_loader import load_data
from transformers import AutoTokenizer, AutoModelForMaskedLM

# 获取当前文件所在目录
BASE_DIR = Path(__file__).resolve().parent

# 设置模型路径
ESM_MODEL_PATH = BASE_DIR / "esm2_t12_35M_UR50D"  # 使用本地模型路径
CLASSIFIER_PATH = os.path.join(BASE_DIR, "models/protein_classifier.pth")
LIBRARY_FEATURES_PATH = os.path.join(BASE_DIR, "data/processed/library_features.npy")
DATA_PATH = os.path.join(BASE_DIR, "data/raw/protein_data.csv")
EXTRA_INFO_PATH = os.path.join(BASE_DIR, "data/raw/protein_embedding_extra_info.csv")

# 全局初始化
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"当前使用设备: {device}")

# 初始化ESM模型和分类器
try:
    # 使用本地模型路径
    esm_tokenizer = AutoTokenizer.from_pretrained(str(ESM_MODEL_PATH))
    esm_model = AutoModelForMaskedLM.from_pretrained(str(ESM_MODEL_PATH)).to(device)
    print("成功加载ESM模型")
except Exception as e:
    print(f"加载ESM模型失败: {str(e)}")
    raise

# 创建分类器实例
classifier = ProteinClassifier(input_dim=480, hidden_dim1=512, hidden_dim2=256).to(device)

# 加载分类器模型权重
try:
    # 使用更新后的load_model函数，并传入device参数
    load_model(classifier, CLASSIFIER_PATH, device)
    classifier.eval()
    print("成功加载分类器模型")
except Exception as e:
    print(f"加载分类器模型失败: {str(e)}")
    raise


def get_embedding_from_sequence(sequence: str, max_length=1024) -> np.ndarray:
    """
    将蛋白质序列转换为480维表征向量（基于ESM模型）
    """
    if not sequence:
        raise ValueError("输入序列不能为空")

    # 预处理序列（自动补全批次维度）
    inputs = esm_tokenizer(
        [sequence],
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=max_length
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # 推理并提取[CLS]标记的嵌入（第12层）
    with torch.no_grad():
        outputs = esm_model(**inputs, output_hidden_states=True)
        embedding = outputs.hidden_states[12][0, 0, :]

    # 清理GPU内存
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    return embedding.cpu().numpy()


def predict_enzyme_from_sequence(sequence: str) -> dict:
    """
    输入蛋白质序列，返回是否为酶的判断结果
    """
    try:
        representation = get_embedding_from_sequence(sequence)
        input_tensor = torch.tensor(representation, dtype=torch.float32).unsqueeze(0).to(device)

        with torch.no_grad():
            output, feature = classifier(input_tensor)
            probabilities = torch.softmax(output, dim=1)
            prediction = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][prediction].item()

        # 清理GPU内存
        if device.type == 'cuda':
            torch.cuda.empty_cache()

        # 使用特征向量查找最相似的蛋白质，用于获取额外信息
        feature_np = feature.cpu().numpy()
        similar_info = None

        try:
            # 加载库特征和ID
            library_features = np.load(LIBRARY_FEATURES_PATH)
            data = load_data(DATA_PATH)
            library_ids = data['Protein_ID'].tolist()

            # 计算相似度并找到最相似的蛋白质
            similarities = compute_similarity(feature_np, library_features)
            top_index = np.argmax(similarities)
            top_similarity = float(similarities[top_index])
            top_protein_id = library_ids[top_index]

            # 尝试从额外信息文件获取信息
            if os.path.exists(EXTRA_INFO_PATH):
                extra_df = pd.read_csv(EXTRA_INFO_PATH)
                extra_row = extra_df[extra_df['ID'] == top_protein_id]
                if not extra_row.empty:
                    similar_info = {
                        'most_similar_protein': top_protein_id,
                        'similarity': round(top_similarity * 100, 2)
                    }
                    # 添加额外信息
                    for key, value in extra_row.iloc[0].to_dict().items():
                        if key != 'ID':  # 避免重复ID
                            similar_info[key] = value
        except Exception as e:
            print(f"获取相似蛋白质额外信息时出错: {str(e)}")

        result = {
            "prediction": "酶" if prediction == 1 else "非酶",
            "confidence": round(confidence * 100, 2),
            "status": "success"
        }

        # 如果找到了相似蛋白质的额外信息，添加到结果中
        if similar_info:
            result["similar_info"] = similar_info

        print(result)
    except Exception as e:
        result = {
            "status": "error",
            "message": str(e)
        }

    return result


def find_top5_similar_proteins(sequence: str) -> dict:
    """
    找出库中top5相似的蛋白质
    """
    try:
        # 获取序列表征
        new_representation = get_embedding_from_sequence(sequence)

        # 加载库特征和ID
        library_features = np.load(LIBRARY_FEATURES_PATH)
        data = load_data(DATA_PATH)
        library_ids = data['Protein_ID'].tolist()

        # 计算特征并找出相似蛋白质
        new_rep_tensor = torch.tensor(new_representation, dtype=torch.float32).unsqueeze(0).to(device)
        with torch.no_grad():
            _, new_feature = classifier(new_rep_tensor)
        new_feature = new_feature.cpu().numpy()

        # 清理GPU内存
        if device.type == 'cuda':
            torch.cuda.empty_cache()

        similarities = compute_similarity(new_feature, library_features)
        top_indices = np.argsort(similarities)[::-1][:5]
        top_protein_ids = [library_ids[i] for i in top_indices]
        top_similarities = [float(similarities[i]) for i in top_indices]

        # 尝试加载额外信息
        extra_info = {}
        try:
            if os.path.exists(EXTRA_INFO_PATH):
                extra_df = pd.read_csv(EXTRA_INFO_PATH)
                for pid in top_protein_ids:
                    extra_row = extra_df[extra_df['ID'] == pid]
                    if not extra_row.empty:
                        extra_info[pid] = extra_row.iloc[0].to_dict()
        except Exception as e:
            print(f"加载额外信息时出错: {str(e)}")

        similar_proteins = []
        for i, pid in enumerate(top_protein_ids):
            protein_info = {"id": pid, "similarity": round(top_similarities[i] * 100, 2)}
            # 如果有额外信息，添加到结果中
            if pid in extra_info:
                for key, value in extra_info[pid].items():
                    if key != 'ID' and key not in protein_info:  # 避免覆盖已有信息
                        protein_info[key] = value
            similar_proteins.append(protein_info)

        result = {
            "status": "success",
            "similar_proteins": similar_proteins
        }
    except Exception as e:
        result = {
            "status": "error",
            "message": str(e)
        }

    return result


if __name__ == "__main__":
    test_sequence = "MDSPEVTFTLAYLVFAVCFVFTPNEFHAAGLTVQNLLSGWLGSEDAAFVPFHLRRTAATLLCHSLLPLGYYVGMCLAASEKRLHALSQAPEAWRLFLLLAVTLPSIACILIYYWSRDRWACHPLARTLALYALPQSGWQAVASSVNTEFRRIDKFATGAPGARVIVTDTWVMKVTTYRVHVAQQQDVHLTVTESRQHELSPDSNLPVQLLTIRVASTNPAVQAFDIWLNSTEYGELCEKLRAPIRRAAHVVIHQSLGDLFLETFASLVEVNPAYSVPSSQELEACIGCMQTRASVKLVKTCQEAATGECQQCYCRPMWCLTCMGKWFASRQDPLRPDTWLASRVPCPTCRARFCILDVCTVR"

    # 测试酶预测功能
    result = predict_enzyme_from_sequence(test_sequence)
    print("酶预测结果:", result)

    # 测试相似蛋白质查找功能
    similar_result = find_top5_similar_proteins(test_sequence)
    print("相似蛋白质结果1:", similar_result)
