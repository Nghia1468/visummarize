import numpy as np
from app.nlp.vectorizer import build_tfidf_matrix, sentence_similarity_matrix


def tfidf_summarize(sentences: list[str], ratio: float = 0.3,
                     use_mmr: bool = True, diversity: float = 0.7) -> list[str]:
    """
    Tóm tắt văn bản bằng TF-IDF.

    Quy trình:
    1. Tiền xử lý từng câu → chuỗi token, tính ma trận TF-IDF
    2. Điểm câu = tổng TF-IDF các từ trong câu
    3. Chọn top N câu (mặc định qua MMR để giảm trùng lặp), giữ thứ tự gốc
    """
    if len(sentences) == 0:
        return []

    n_select = max(1, round(len(sentences) * ratio))
    n_select = min(n_select, len(sentences))

    vectorizer, tfidf_matrix, _ = build_tfidf_matrix(sentences)
    if tfidf_matrix is None:
        return sentences[:n_select]

    scores = np.array(tfidf_matrix.sum(axis=1)).flatten()

    if use_mmr:
        from app.nlp.mmr import mmr_select
        sim_matrix = sentence_similarity_matrix(tfidf_matrix)
        top_indices = mmr_select(scores, sim_matrix, n_select, diversity=diversity)
    else:
        top_indices = list(np.argsort(scores)[::-1][:n_select])

    top_indices = sorted(top_indices)
    return [sentences[i] for i in top_indices]
