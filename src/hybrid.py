from .retrieve import retrieve_chunks
from .semantic import search_semantic


def reciprocal_rank_fusion(lexical, semantic, k0=60, limit=5):
    fused = {}
    rankings = [
        ("bm25", lexical),
        ("semantic", semantic),
    ]

    for method, res in rankings:
        for rank, chunk in enumerate(res, start=1):
            key = (
                chunk["file_path"],
                chunk["start"],
                chunk["end"],
            )

            if key not in fused:
                fused[key] = {
                        **chunk,
                        "score": 0.0,
                        "bm25_rank": None,
                        "semantic_rank": None,
                    }
    
            #calculate rrf
            fused[key]["score"] += 1 / (k0 + rank) 
            #remember its position in each retrieval system
            fused[key][f"{method}_rank"] = rank


        results = sorted(
            fused.values(),
            key=lambda chunk: chunk["score"],
            reverse = True,
        )

        return results[:limit]


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



