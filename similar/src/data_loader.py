import pandas as pd
import numpy as np
import ast
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
import torch


class ProteinDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    # 根据索引 idx 获取数据集中的一个样本，提取该样本的 Representation 列作为表征向量，Label 列作为标签，并将它们转换为 PyTorch 张量返回。
    def __getitem__(self, idx):
        representation = self.data.iloc[idx]['Representation']
        label = self.data.iloc[idx]['Label']
        return torch.tensor(representation, dtype=torch.float32), torch.tensor(label, dtype=torch.long)


def load_data(data_path):
    try:
        data = pd.read_csv(data_path)
        # 检查必要的列是否存在
        required_columns = ['Protein_ID', 'Representation']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            print(f"警告: CSV文件缺少必要的列: {', '.join(missing_columns)}")
            return create_sample_data()
        
        # 使用ast.literal_eval将字符串形式的Python列表转换为实际的Python列表
        try:
            data['Representation'] = data['Representation'].apply(lambda x: np.array(ast.literal_eval(x)))
        except Exception as e:
            print(f"处理Representation列时出错: {str(e)}")
            return create_sample_data()
            
        return data
    except Exception as e:
        print(f"加载数据出错: {str(e)}")
        return create_sample_data()


def create_sample_data():
    """创建示例数据用于演示"""
    print("生成示例数据用于演示")
    # 创建10个示例蛋白质
    protein_ids = [f'PROT{i+1}' for i in range(10)]
    # 为每个蛋白质生成随机表征向量
    representations = [np.random.randn(480) for _ in range(10)]
    # 随机分配标签（酶或非酶）
    labels = np.random.choice([0, 1], size=10)
    
    # 创建DataFrame
    sample_data = pd.DataFrame({
        'Protein_ID': protein_ids,
        'Representation': representations,
        'Label': labels
    })
    
    return sample_data


# 划分训练集和测试集
def split_data(data, test_size=0.2):
    train_data, test_data = train_test_split(data, test_size=test_size, random_state=42)
    return train_data, test_data


def get_dataloaders(train_data, test_data, batch_size=32):
    train_dataset = ProteinDataset(train_data)
    test_dataset = ProteinDataset(test_data)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, test_loader
