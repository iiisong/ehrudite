import torch
import pandas as pd
import json
from sentence_transformers import SentenceTransformer, util

# model = SentenceTransformer('distilbert-multilingual-nli-stsb-quora-ranking')
# f = open('../models/mimic-iii/qqdict.json')
# qqdict = json.load(f)
# corpus_embedding = torch.tensor(pd.read_csv("../models/mimic-iii/corpus.csv").values).to(torch.float32)

def SVS(question, k=10, corpus=None, model=None, corpus_path="../models/mimic-iii/corpus.csv"):
    if corpus_path != "../models/mimic-iii/corpus.csv" and corpus == None:
        corpus_embedding = torch.tensor(pd.read_csv("../models/mimic-iii/corpus.csv").values).to(torch.float32)
    
    if corpus != None:
        corpus_embedding = corpus

    if model == None:
        model = SentenceTransformer('distilbert-multilingual-nli-stsb-quora-ranking')
        
    top_k = k # min(k, len(corpus))

    query_embedding = model.encode(question, convert_to_tensor=True).to('cpu').to(torch.float32)

    # We use cosine-similarity and torch.topk to find the highest k scores
    cos_scores = util.cos_sim(query_embedding, corpus_embedding)[0]
    top_results = torch.topk(cos_scores, k=top_k)

    return top_results.indices.tolist()
    # return [qqdict[i] for i in top_results.indices.tolist()]