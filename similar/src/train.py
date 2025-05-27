import torch
import torch.nn as nn
from torch.optim import Adam
from .model import ProteinClassifier
from .data_loader import load_data, split_data, get_dataloaders
from .utils import save_model
import matplotlib.pyplot as plt


def train(model, train_loader, criterion, optimizer, device):
    model.train()
    total_loss = 0
    for data, target in train_loader:
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output, _ = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(train_loader)


def main_train(config):
    # 加载数据
    data = load_data(config['data_path'])
    train_data, test_data = split_data(data)
    train_loader, test_loader = get_dataloaders(train_data, test_data, config['batch_size'])

    # 初始化模型
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ProteinClassifier(config['input_dim'], config['hidden_dim1'], config['hidden_dim2']).to(device)

    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()  # 使用交叉熵损失函数
    optimizer = Adam(model.parameters(), lr=config['learning_rate'])

    loss_history = []  # 存储每个 epoch 的损失值

    for epoch in range(config['num_epochs']):
        loss = train(model, train_loader, criterion, optimizer, device)
        loss_history.append(loss)  # 记录损失
        print(f"Epoch {epoch + 1}/{config['num_epochs']}, Loss: {loss:.4f}")

    save_model(model, config['model_path'])

    # 绘制并保存 loss 曲线
    plt.figure()  # 创建新的图像窗口
    plt.plot(range(1, config['num_epochs'] + 1), loss_history, marker='o')  # 绘制 loss 曲线，带标记点
    plt.title('Changes in losses during training')  # 设置图标题
    plt.xlabel('Epoch')  # 设置横轴标签
    plt.ylabel('Loss')  # 设置纵轴标签
    plt.grid(True)  # 显示网格线
    plt.savefig('loss_curve.png')  # 保存图像到文件
    plt.show()  # 显示图像窗口

    return model, data
