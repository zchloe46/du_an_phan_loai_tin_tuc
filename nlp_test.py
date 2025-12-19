# nlp_test.py
import pandas as pd
from underthesea import word_tokenize, pos_tag
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# 1. Load dữ liệu vừa crawl
try:
    df = pd.read_csv('dataset_demo.csv')
    print(f"Đã load {len(df)} bài báo.")
except:
    print("Chưa có file data, hãy chạy crawler_demo.py trước!")
    exit()

# 2. Hàm tiền xử lý (Sử dụng Underthesea)
def preprocess(text):
    # word_tokenize với format='text' sẽ nối từ ghép bằng _ (ví_dụ)
    return word_tokenize(text, format="text")

print("Đang xử lý ngôn ngữ tự nhiên (Tokenizing)...")
df['processed_content'] = df['Content'].apply(preprocess)

# 3. Chia dữ liệu train/test
X_train, X_test, y_train, y_test = train_test_split(
    df['processed_content'], df['Label'], test_size=0.2, random_state=42
)

# 4. Xây dựng Pipeline đơn giản (TF-IDF + Naive Bayes)
# Đây là mô hình "nhẹ" nhất để khởi động dự án
model = make_pipeline(TfidfVectorizer(), MultinomialNB())

print("Đang huấn luyện mô hình...")
model.fit(X_train, y_train)

# 5. Đánh giá sơ bộ
print("\nKết quả đánh giá trên tập test:")
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# 6. Thử nghiệm thực tế
test_text = "Giá vàng hôm nay tăng mạnh, thị trường chứng khoán biến động"
processed_test = preprocess(test_text)
prediction = model.predict([processed_test])[0]
print(f"\nTest câu: '{test_text}'")
print(f"Dự đoán: {prediction}")

# 7. Lưu model lại để sau này dùng trong Django
joblib.dump(model, 'news_classifier.pkl')
print("\nĐã lưu model vào 'news_classifier.pkl'")