"""
MMR (Maximal Marginal Relevance) — chọn lại danh sách câu để vừa giữ điểm quan
trọng cao, vừa giảm trùng lặp nội dung giữa các câu đã chọn.

Vấn đề trước khi có MMR: TF-IDF/TextRank chỉ chấm điểm từng câu độc lập, nên
2 câu diễn đạt gần giống nhau (ví dụ cùng nói về một số liệu) có thể cùng lọt
vào bản tóm tắt, chiếm mất chỗ của một ý khác trong văn bản.

Công thức mỗi bước chọn câu tiếp theo:
    MMR(i) = λ * score(i) - (1 - λ) * max( sim(i, j) với j đã chọn )

λ càng cao thì càng ưu tiên điểm quan trọng gốc; λ càng thấp thì càng ưu tiên
đa dạng hóa nội dung.
"""
import numpy as np


def mmr_select(scores: np.ndarray, similarity_matrix: np.ndarray,
                n_select: int, diversity: float = 0.7) -> list[int]:
    """
    Args:
        scores:            điểm quan trọng gốc của từng câu (TF-IDF sum hoặc TextRank)
        similarity_matrix:  ma trận tương đồng cosine giữa các câu (n x n)
        n_select:           số câu cần chọn
        diversity:          hệ số λ (0-1). Mặc định 0.7 = ưu tiên điểm quan trọng,
                             nhưng vẫn tránh chọn 2 câu quá giống nhau.

    Returns:
        Danh sách chỉ số câu được chọn (chưa sắp lại theo thứ tự gốc).
    """
    n = len(scores)
    n_select = min(n_select, n)
    if n_select <= 0:
        return []

    # Chuẩn hóa điểm về [0, 1] để cộng trừ với similarity (cũng trong [0, 1]) hợp lý
    score_range = scores.max() - scores.min()
    norm_scores = (scores - scores.min()) / score_range if score_range > 0 else np.ones(n)

    selected: list[int] = []
    remaining = set(range(n))

    # Câu đầu tiên: luôn là câu điểm cao nhất
    first = int(np.argmax(norm_scores))
    selected.append(first)
    remaining.discard(first)

    while len(selected) < n_select and remaining:
        best_idx, best_mmr = None, -np.inf
        for idx in remaining:
            redundancy = max(similarity_matrix[idx][j] for j in selected)
            mmr_score = diversity * norm_scores[idx] - (1 - diversity) * redundancy
            if mmr_score > best_mmr:
                best_mmr, best_idx = mmr_score, idx
        selected.append(best_idx)
        remaining.discard(best_idx)

    return selected
