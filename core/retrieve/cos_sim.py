

import utils.api as api
import numpy as np
import torch
import torch.nn.functional as F


def similarity(v1, v2):
    if not isinstance(v1, list):
        v1 = list(v1)
    if not isinstance(v2, list):
        v2 = list(v2)
    vec1 = torch.FloatTensor(v1)
    vec2 = torch.FloatTensor(v2)
    cos_sim = F.cosine_similarity(vec1, vec2, dim=0)
    return cos_sim


def get_related_dialog_score(query: str, history, top_k: int = 2):
    return None


if __name__ == '__main__':
    pass

