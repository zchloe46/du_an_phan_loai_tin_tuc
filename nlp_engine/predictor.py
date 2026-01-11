# nlp_engine/predictor.py
import os
import joblib
from underthesea import word_tokenize
from django.conf import settings
import numpy as np

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
            return "Chưa phân loại", 0.0
        
        try:
            # 1. Tiền xử lý
            processed_text = self.preprocess(text)
            
            # 2. Lấy xác suất (predict_proba) thay vì chỉ lấy nhãn (predict)
            # Hàm predict_proba trả về mảng xác suất: [[0.05, 0.92, 0.03]]
            proba = self.model.predict_proba([processed_text])[0]
            
            # 3. Tìm nhãn có xác suất cao nhất
            max_index = np.argmax(proba)
            max_score = proba[max_index] # Đây là % độ tin cậy (VD: 0.92)
            label = self.model.classes_[max_index] # Tên nhãn (VD: Kinh doanh)
            
            return label, max_score
            
        except Exception as e:
            # Nếu model không hỗ trợ predict_proba (như SVM thuần), fallback về predict thường
            try:
                label = self.model.predict([processed_text])[0]
                return label, 0.0 # Không tính được score thì trả về 0
            except:
                print(f"Lỗi dự đoán: {e}")
                return "Lỗi AI", 0.0

# Khởi tạo sẵn một instance để các nơi khác import dùng luôn
classifier = NewsClassifier()