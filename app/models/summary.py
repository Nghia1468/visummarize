from app import db
from datetime import datetime


class Summary(db.Model):
    __tablename__ = 'summaries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    summary_text = db.Column(db.Text, nullable=False)
    method = db.Column(db.String(20), nullable=False, default='textrank')
    ratio = db.Column(db.Float, nullable=False, default=0.3)
    original_length = db.Column(db.Integer, nullable=False)
    summary_length = db.Column(db.Integer, nullable=False)
    processing_time = db.Column(db.Float, nullable=True)
    keywords = db.Column(db.String(500), nullable=True)  # lưu dạng "từ1, từ2, ..."
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'original_text': self.original_text,
            'summary_text': self.summary_text,
            'method': self.method,
            'ratio': self.ratio,
            'keywords': [k.strip() for k in self.keywords.split(',')] if self.keywords else [],
            'original_length': self.original_length,
            'summary_length': self.summary_length,
            'processing_time': self.processing_time,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
            'compression': round((1 - self.summary_length / self.original_length) * 100, 1)
        }

    def __repr__(self):
        return f'<Summary {self.id}>'
