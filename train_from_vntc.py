# train_from_vntc.py
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from underthesea import word_tokenize

# ĐƯỜNG DẪN ĐẾN THƯ MỤC VNTC BẠN VỪA TẢI VỀ
DATA_DIR = 'D:\du_an_phan_loai_tin_tuc\media\Train_Full' 

def load_data():
    data = []
    labels = []
    print("Đang đọc dữ liệu từ ổ cứng...")
    
    # Duyệt qua các thư mục con (Mỗi thư mục là 1 nhãn)
    for label in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, label)
        if os.path.isdir(path):
            print(f"-> Đang đọc mục: {label}")
            # Đọc các file text trong thư mục
            for filename in os.listdir(path)[:200]: # Lấy 200 bài mỗi mục để train cho nhanh
                try:
                    with open(os.path.join(path, filename), 'r', encoding='utf-16') as f:
                        content = f.read()
                        # Tokenize
                        content = word_tokenize(content, format="text")
                        data.append(content)
                        labels.append(label)
                except:
                    continue
    return data, labels

# Chạy quy trình
texts, labels = load_data()
print(f"Tổng số bài: {len(texts)}")

# Train
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)
model = make_pipeline(TfidfVectorizer(ngram_range=(1,2), max_features=10000), LogisticRegression(max_iter=1000))

print("Đang training...")
model.fit(X_train, y_train)

# Đánh giá
print(classification_report(y_test, model.predict(X_test)))

# Lưu
joblib.dump(model, 'nlp_engine/news_classifier.pkl')
print("Đã tạo xong file .pkl xịn!")