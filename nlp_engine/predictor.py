# nlp_engine/predictor.py
import os
import joblib
from underthesea import word_tokenize
from django.conf import settings

class NewsClassifier:
    _instance = None
    model = None

    def __new__(cls):
        # Singleton Pattern: Chỉ khởi tạo 1 lần duy nhất
        if cls._instance is None:
            cls._instance = super(NewsClassifier, cls).__new__(cls)
            cls._instance.load_model()
        return cls._instance

    def load_model(self):
        # Đường dẫn tuyệt đối tới file model để tránh lỗi path
        base_dir = getattr(settings, 'BASE_DIR', os.getcwd())
        model_path = os.path.join(base_dir, 'nlp_engine', 'news_classifier.pkl')
        
        try:
            print(f"Đang load AI Model từ: {model_path}...")
            self.model = joblib.load(model_path)
            print("Load Model thành công!")
        except Exception as e:
            print(f"LỖI: Không thể load model. Chi tiết: {e}")
            self.model = None

    def preprocess(self, text):
        # Bắt buộc phải giống hệt lúc train: Tách từ bằng underthesea
        if not text: return ""
        return word_tokenize(text, format="text")

    def predict(self, text):
        if self.model is None:
            return "Chưa phân loại"
        
        try:
            # 1. Tiền xử lý (Tách từ)
            processed_text = self.preprocess(text)
            
            # 2. Dự đoán (Model trả về mảng, lấy phần tử đầu tiên)
            label = self.model.predict([processed_text])[0]
            return label
        except Exception as e:
            print(f"Lỗi dự đoán: {e}")
            return "Lỗi AI"

# Khởi tạo sẵn một instance để các nơi khác import dùng luôn
classifier = NewsClassifier()