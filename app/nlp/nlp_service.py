import time
from app.nlp.preprocessor import normalize_text, split_sentences
from app.nlp.tfidf_summarizer import tfidf_summarize
from app.nlp.textrank_summarizer import textrank_summarize
from app.nlp.keyword_extractor import extract_keywords


MIN_TEXT_LENGTH = 100   # Ký tự tối thiểu
MIN_SENTENCES = 3       # Số câu tối thiểu để tóm tắt có nghĩa

METHODS = {
    'tfidf': tfidf_summarize,
    'textrank': textrank_summarize,
}
DEFAULT_METHOD = 'textrank'


def summarize(text: str, method: str = DEFAULT_METHOD, ratio: float = 0.3,
              use_mmr: bool = True, extract_kw: bool = True) -> dict:
    """
    Điểm vào chính của module NLP.

    Args:
        text:       Văn bản gốc tiếng Việt
        method:     Phương pháp tóm tắt ('tfidf' | 'textrank')
        ratio:      Tỷ lệ tóm tắt (0.1 – 0.5)
        use_mmr:    Có áp dụng MMR để giảm câu trùng lặp nội dung không
        extract_kw: Có trích xuất từ khóa hay không

    Returns:
        dict với các key: summary, keywords, method, original_length,
                          summary_length, sentence_count, selected_count,
                          processing_time, error
    """
    # Validate đầu vào
    if not text or not text.strip():
        return {'error': 'Văn bản không được để trống.'}

    text = text.strip()

    if len(text) < MIN_TEXT_LENGTH:
        return {'error': f'Văn bản quá ngắn. Vui lòng nhập ít nhất {MIN_TEXT_LENGTH} ký tự.'}

    ratio = max(0.1, min(0.5, float(ratio)))

    if method not in METHODS:
        method = DEFAULT_METHOD
    summarize_fn = METHODS[method]

    start = time.time()

    # Bước 1: Chuẩn hóa văn bản
    normalized = normalize_text(text)

    # Bước 2: Tách câu
    sentences = split_sentences(normalized)

    if len(sentences) < MIN_SENTENCES:
        return {'error': f'Văn bản cần có ít nhất {MIN_SENTENCES} câu để tóm tắt.'}

    # Bước 3: Tóm tắt bằng phương pháp đã chọn (có MMR để giảm trùng lặp)
    selected, selected_indices = summarize_fn(sentences, ratio, use_mmr=use_mmr)

    if not selected:
        return {'error': 'Không thể tạo bản tóm tắt. Vui lòng thử lại với văn bản khác.'}

    summary = ' '.join(selected)

    # Bước 4: Trích xuất từ khóa (tùy chọn, không ảnh hưởng đến bản tóm tắt)
    keywords = extract_keywords(sentences, top_k=8) if extract_kw else []

    elapsed = round(time.time() - start, 3)

    return {
        'summary': summary,
        'keywords': keywords,
        'method': method,
        'original_length': len(text),
        'summary_length': len(summary),
        'sentence_count': len(sentences),
        'selected_count': len(selected),
        'processing_time': elapsed,
        # Dùng để tô sáng câu được chọn trên UI: danh sách toàn bộ câu (đã
        # chuẩn hóa) và chỉ số các câu lọt vào bản tóm tắt.
        'sentences': sentences,
        'selected_indices': selected_indices,
        'error': None
    }
