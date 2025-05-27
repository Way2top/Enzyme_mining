import torch
import numpy as np
from .model import ProteinClassifier
from .utils import load_model, extract_features, compute_similarity
from .data_loader import load_data


def find_similar_proteins(new_representation, model, library_features, library_ids, device, top_k=5):
    model.eval()
    new_representation = torch.tensor(new_representation, dtype=torch.float32).unsqueeze(0).to(device)
    with torch.no_grad():
        _, new_feature = model(new_representation)
    new_feature = new_feature.cpu().numpy()
    similarities = compute_similarity(new_feature, library_features)
    top_indices = np.argsort(similarities)[::-1][:top_k]
    top_proteins = [library_ids[i] for i in top_indices]
    top_similarities = [similarities[i] for i in top_indices]
    return top_proteins, top_similarities


def main_inference(config, new_representation):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("main_inference device:", device)
    model = ProteinClassifier(config['input_dim'], config['hidden_dim1'], config['hidden_dim2']).to(device)
    # load_model(model, config['model_path'])
    load_model(model, config['model_path'], device)
    library_features = np.load(config['library_features_path'])
    library_ids = load_data(config['data_path'])['Protein_ID'].tolist()

    top_proteins, top_similarities = find_similar_proteins(new_representation, model, library_features, library_ids,
                                                           device)
    print(f"Top 5 相似的蛋白质: {top_proteins}")
    print(f"相似度: {top_similarities}")