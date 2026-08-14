"""
Đánh giá chất lượng bản tóm tắt bằng ROUGE (Lin, 2004) — so sánh bản tóm tắt
do hệ thống sinh ra (candidate) với 1 bản tóm tắt tham chiếu do con người
viết (reference).

Cài đặt thuần Python (không phụ thuộc thư viện ngoài) để minh bạch về mặt
thuật toán — phù hợp mục đích học thuật/bảo vệ đồ án, đồng thời tránh thêm
một dependency cần build native (rút kinh nghiệm từ underthesea).

3 biến thể ROUGE được cài đặt:
- ROUGE-1: độ chồng lấp unigram (từng từ đơn) giữa candidate và reference.
- ROUGE-2: độ chồng lấp bigram (cặp từ liên tiếp).
- ROUGE-L: dựa trên LCS (Longest Common Subsequence) — dãy con chung dài
  nhất giữa 2 chuỗi từ, không yêu cầu liên tiếp.

Mỗi biến thể trả về 3 chỉ số:
- precision: bao nhiêu phần của candidate khớp với reference.
- recall:    bao nhiêu phần của reference được candidate "bắt" được.
- f1:        trung bình điều hòa (harmonic mean) của precision và recall.
"""
from collections import Counter
from app.nlp.preprocessor import normalize_text, tokenize_words


def _tokenize_for_rouge(text: str) -> list[str]:
    """Tách từ phục vụ tính ROUGE.

    Khác với preprocess_sentence() dùng cho tóm tắt, ở đây KHÔNG loại bỏ
    stopword — ROUGE theo định nghĩa gốc so khớp trên toàn bộ từ, loại
    stopword sẽ làm sai lệch điểm số so với chuẩn.
    """
    normalized = normalize_text(text)
    tokens = tokenize_words(normalized)
    return [t.lower() for t in tokens if t.strip()]


def _ngrams(tokens: list[str], n: int) -> list[tuple]:
    if len(tokens) < n:
        return []
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def _prf1(precision: float, recall: float) -> dict:
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return {'precision': round(precision, 4), 'recall': round(recall, 4), 'f1': round(f1, 4)}


def rouge_n(candidate_tokens: list[str], reference_tokens: list[str], n: int) -> dict:
    """ROUGE-N: độ chồng lấp n-gram giữa candidate và reference."""
    cand_ngrams = _ngrams(candidate_tokens, n)
    ref_ngrams = _ngrams(reference_tokens, n)

    if not cand_ngrams or not ref_ngrams:
        return _prf1(0.0, 0.0)

    cand_counts = Counter(cand_ngrams)
    ref_counts = Counter(ref_ngrams)
    # Số n-gram trùng khớp, không vượt quá số lần xuất hiện ở mỗi bên
    overlap = sum((cand_counts & ref_counts).values())

    precision = overlap / len(cand_ngrams)
    recall = overlap / len(ref_ngrams)
    return _prf1(precision, recall)


def _lcs_length(a: list[str], b: list[str]) -> int:
    """Độ dài LCS (Longest Common Subsequence) giữa 2 danh sách token, quy
    hoạch động O(len(a) × len(b))."""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]


def rouge_l(candidate_tokens: list[str], reference_tokens: list[str]) -> dict:
    """ROUGE-L: dựa trên độ dài LCS giữa candidate và reference."""
    if not candidate_tokens or not reference_tokens:
        return _prf1(0.0, 0.0)

    lcs = _lcs_length(candidate_tokens, reference_tokens)
    precision = lcs / len(candidate_tokens)
    recall = lcs / len(reference_tokens)
    return _prf1(precision, recall)


def evaluate_rouge(candidate_text: str, reference_text: str) -> dict:
    """
    Điểm vào chính: so sánh 1 bản tóm tắt do hệ thống sinh ra (candidate)
    với 1 bản tóm tắt tham chiếu do con người viết (reference).

    Args:
        candidate_text: bản tóm tắt do hệ thống tạo ra (Summary.summary_text)
        reference_text: bản tóm tắt tham chiếu do người dùng tự nhập

    Returns:
        dict: {'rouge1': {...}, 'rouge2': {...}, 'rougeL': {...}}
        mỗi giá trị con gồm precision/recall/f1.
    """
    cand_tokens = _tokenize_for_rouge(candidate_text)
    ref_tokens = _tokenize_for_rouge(reference_text)

    return {
        'rouge1': rouge_n(cand_tokens, ref_tokens, 1),
        'rouge2': rouge_n(cand_tokens, ref_tokens, 2),
        'rougeL': rouge_l(cand_tokens, ref_tokens),
    }
