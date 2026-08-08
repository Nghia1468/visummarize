"""
Tiện ích dùng chung: vector hóa câu bằng TF-IDF + tính ma trận tương đồng.
Được dùng lại bởi cả tfidf_summarizer, textrank_summarizer, mmr và keyword_extractor
để tránh tính TF-IDF nhiều lần trên cùng một văn bản.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.nlp.preprocessor import preprocess_sentence


def build_tfidf_matrix(sentences: list[str]):
    """
    Tiền xử lý danh sách câu và tính ma trận TF-IDF.

    Returns:
        (vectorizer, tfidf_matrix, processed_texts) hoặc (None, None, None)
        nếu không thể vector hóa (ví dụ toàn bộ câu rỗng sau khi tiền xử lý
        và cũng không dùng được câu gốc).
    """
    processed = [' '.join(preprocess_sentence(s)) for s in sentences]

    # Câu nào rỗng sau tiền xử lý (toàn stopword / ký tự lạ) thì dùng lại câu gốc
    # viết thường, để tránh lỗi "empty vocabulary" của TfidfVectorizer.
    for i, p in enumerate(processed):
        if p.strip() == '':
            processed[i] = sentences[i].lower()

    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform(processed)
    except ValueError:
        return None, None, None

    return vectorizer, tfidf_matrix, processed


def sentence_similarity_matrix(tfidf_matrix):
    """Ma trận tương đồng cosine giữa các câu, dựa trên vector TF-IDF đã có."""
    return cosine_similarity(tfidf_matrix)
