from .retrieve import retrieve_chunks
from .semantic import search_semantic





def reciprocal_rank_fusion(lexical, semantic, k0=60, limit=5):
    fused = {}
    rankings = [
        ("bm25", lexical),
        ("semantic", semantic),
    ]

    for method, res in rankings:
        







def search_hybrid(query: str, k: int = 5):
    if not query.strip() or k  <= 0:
        return []

   candidate_k = max(20, k)

   lexical_search = retrieve_chunks(query, candidate_k)
   semantic_search = search_semantic(query, candidate_k)
    
    return reciprocal_rank_fusion(
        lexical_search,
        semantic_search,
        k0=60,
        limit=k,
    )



