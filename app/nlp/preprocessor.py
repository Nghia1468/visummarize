import re
import unicodedata
import os


def load_stopwords():
    """Tải danh sách stopwords tiếng Việt."""
    stopwords_path = os.path.join(os.path.dirname(__file__), 'stopwords.txt')
    with open(stopwords_path, encoding='utf-8') as f:
        return set(line.strip().lower() for line in f if line.strip())


STOPWORDS = load_stopwords()


def normalize_text(text: str) -> str:
    """Chuẩn hóa văn bản: unicode, khoảng trắng, ký tự đặc biệt."""
    # Chuẩn hóa unicode NFC
    text = unicodedata.normalize('NFC', text)
    # Loại bỏ thẻ HTML nếu có
    text = re.sub(r'<[^>]+>', ' ', text)
    # Loại bỏ URL
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # Chuẩn hóa dấu câu
    text = re.sub(r'["""]', '"', text)
    text = re.sub(r"[''']", "'", text)
    # Loại bỏ ký tự không phải chữ cái, số, dấu câu cơ bản
    text = re.sub(r'[^\w\s.,!?;:()\-–—"\'áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ]', ' ', text)
    # Chuẩn hóa khoảng trắng
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def split_sentences(text: str) -> list[str]:
    """Tách văn bản thành danh sách câu.
    Ưu tiên dùng underthesea, fallback sang regex.
    """
    try:
        from underthesea import sent_tokenize
        sentences = sent_tokenize(text)
    except Exception:
        # Fallback: tách theo dấu câu
        sentences = re.split(r'(?<=[.!?])\s+', text)

    # Lọc bỏ câu quá ngắn (< 10 ký tự)
    sentences = [s.strip() for s in sentences if len(s.strip()) >= 10]
    return sentences


def tokenize_words(sentence: str) -> list[str]:
    """Phân tách từ tiếng Việt.
    Ưu tiên underthesea, fallback sang tách theo khoảng trắng.
    """
    try:
        from underthesea import word_tokenize
        tokens = word_tokenize(sentence, format='text').split()
    except Exception:
        tokens = sentence.split()

    return tokens


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Loại bỏ stopwords và token không hợp lệ."""
    cleaned = []
    for t in tokens:
        t_lower = t.lower().replace('_', ' ')
        if t_lower not in STOPWORDS and len(t) > 1 and not t.isdigit():
            cleaned.append(t_lower)
    return cleaned


def preprocess_sentence(sentence: str) -> list[str]:
    """Pipeline đầy đủ: tokenize → remove stopwords cho 1 câu."""
    tokens = tokenize_words(sentence)
    tokens = remove_stopwords(tokens)
    return tokens
