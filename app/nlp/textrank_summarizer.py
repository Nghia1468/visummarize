"""
Tóm tắt văn bản bằng TextRank — thuật toán đồ thị lấy cảm hứng từ PageRank
(Mihalcea & Tarau, 2004).

So với TF-IDF cộng dồn đơn thuần (mỗi câu chấm điểm độc lập), TextRank xét
đến QUAN HỆ giữa các câu: một câu "quan trọng" là câu có nội dung tương đồng
với nhiều câu khác trong văn bản (tức là đại diện cho một ý được nhắc lại/
liên quan nhiều lần), tương tự cách PageRank coi một trang web quan trọng là
trang được nhiều trang khác trỏ tới.

Quy trình:
1. Vector hóa từng câu bằng TF-IDF (dùng chung app.nlp.vectorizer)
2. Xây đồ thị vô hướng: đỉnh = câu, cạnh có trọng số = độ tương đồng cosine
   giữa 2 câu
3. Chạy PageRank trên đồ thị này để có điểm quan trọng từng câu
4. Chọn top-N câu điểm cao nhất, giữ lại đúng thứ tự xuất hiện trong văn bản gốc
"""
import numpy as np
import networkx as nx
from app.nlp.vectorizer import build_tfidf_matrix, sentence_similarity_matrix


def textrank_summarize(sentences: list[str], ratio: float = 0.3,
                        use_mmr: bool = True, diversity: float = 0.7):
    """
    Returns:
        (selected_sentences, selected_indices) — selected_indices là chỉ số
        (0-based) của các câu được chọn trong danh sách `sentences` gốc,
        theo đúng thứ tự xuất hiện. Dùng để tô sáng câu được chọn trên UI.
    """
    if len(sentences) == 0:
        return [], []

    n_select = max(1, round(len(sentences) * ratio))
    n_select = min(n_select, len(sentences))

    vectorizer, tfidf_matrix, _ = build_tfidf_matrix(sentences)
    if tfidf_matrix is None:
        indices = list(range(n_select))
        return sentences[:n_select], indices

    sim_matrix = sentence_similarity_matrix(tfidf_matrix)
    # Bỏ trọng số tự-liên-kết (câu với chính nó) để không làm lệch PageRank
    np.fill_diagonal(sim_matrix, 0)

    graph = nx.from_numpy_array(sim_matrix)

    try:
        pagerank_scores = nx.pagerank(graph, weight='weight')
    except nx.PowerIterationFailedConvergence:
        # Văn bản có cấu trúc đặc biệt khiến PageRank không hội tụ:
        # fallback về tổng độ tương đồng của mỗi câu với các câu khác.
        pagerank_scores = {i: float(sim_matrix[i].sum()) for i in range(len(sentences))}

    scores = np.array([pagerank_scores[i] for i in range(len(sentences))])

    if use_mmr:
        from app.nlp.mmr import mmr_select
        top_indices = mmr_select(scores, sim_matrix, n_select, diversity=diversity)
    else:
        top_indices = list(np.argsort(scores)[::-1][:n_select])

    top_indices = sorted(top_indices)
    return [sentences[i] for i in top_indices], top_indices
