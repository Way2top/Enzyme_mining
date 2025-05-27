import torch
import torch.nn as nn
import torch.nn.functional as F


class ProteinClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim1, hidden_dim2):
        super(ProteinClassifier, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim1)
        self.fc2 = nn.Linear(hidden_dim1, hidden_dim2)
        self.fc3 = nn.Linear(hidden_dim2, 2)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        feature = x  # 保存特征向量
        x = self.fc3(x)
        return x, feature
