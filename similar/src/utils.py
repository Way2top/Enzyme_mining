import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def save_model(model, path):
    torch.save(model.state_dict(), path)


def load_model(model, path, device=None):
    try:
        model.load_state_dict(torch.load(path))
    except Exception:
        # 如果上面的加载失败（比如在CPU上加载GPU模型），尝试使用map_location参数
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.load_state_dict(torch.load(path, map_location=device))


def extract_features(model, data_loader, device):
    model.eval()
    features = []
    with torch.no_grad():
        for data, _ in data_loader:
            data = data.to(device)
            _, feature = model(data)
            features.append(feature.cpu().numpy())
    return np.vstack(features)


def compute_similarity(new_feature, library_features):
    return cosine_similarity(new_feature, library_features)[0]
