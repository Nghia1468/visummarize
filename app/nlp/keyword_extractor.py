"""
Trích xuất từ khóa: tận dụng lại ma trận TF-IDF đã tính cho việc tóm tắt,
lấy ra các từ/cụm từ có tổng trọng số TF-IDF cao nhất trên toàn văn bản.
"""
import numpy as np
from app.nlp.vectorizer import build_tfidf_matrix


def extract_keywords(sentences: list[str], top_k: int = 8) -> list[str]:
    """
    Args:
        sentences: danh sách câu đã tách (dùng chung input với summarizer)
        top_k:     số từ khóa muốn lấy

    Returns:
        Danh sách từ khóa, sắp theo độ quan trọng giảm dần.
    """
    if not sentences:
        return []

    vectorizer, tfidf_matrix, _ = build_tfidf_matrix(sentences)
    if tfidf_matrix is None:
        return []

    # Tổng trọng số TF-IDF của mỗi từ trên toàn bộ văn bản
    term_scores = np.array(tfidf_matrix.sum(axis=0)).flatten()
    terms = vectorizer.get_feature_names_out()

    top_indices = np.argsort(term_scores)[::-1][:top_k]
    keywords = [terms[i].replace('_', ' ') for i in top_indices if term_scores[i] > 0]

    return keywords
