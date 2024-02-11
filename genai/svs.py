import torch
import pandas as pd
import json
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('distilbert-multilingual-nli-stsb-quora-ranking')
f = open('../models/mimic-iii/qqdict.json')
qqdict = json.load(f)
corpus_embedding = torch.tensor(pd.read_csv("../models/mimic-iii/corpus.csv").values).to(torch.float32)


def SVS(query, k=10, corpus_path="../models/mimic-iii/corpus.csv"):
    if corpus_path != "../models/mimic-iii/corpus.csv":
        corpus_embedding = torch.tensor(pd.read_csv("../models/mimic-iii/corpus.csv").values).to(torch.float32)
        
    top_k = k # min(k, len(corpus))

    query_embedding = model.encode(query, convert_to_tensor=True).to('cpu').to(torch.float32)

    # We use cosine-similarity and torch.topk to find the highest k scores
    cos_scores = util.cos_sim(query_embedding, corpus_embedding)[0]
    top_results = torch.topk(cos_scores, k=top_k)

    return [qqdict[i] for i in top_results.indices.tolist()]