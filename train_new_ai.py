# train_new_ai.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
from underthesea import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import sys
import os
import time

# --- 1. CẤU HÌNH HỆ THỐNG ---
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# Danh sách từ vô nghĩa (Stopwords) tiếng Việt cần loại bỏ
# AI sẽ bỏ qua những từ này để tập trung vào từ khóa "đắt giá"
STOP_WORDS = {
    'thì', 'là', 'mà', 'và', 'của', 'những', 'các', 'như', 'với', 'cho', 'tại', 'trong',
    'khi', 'do', 'đến', 'để', 'từ', 'có', 'được', 'người', 'này', 'đó', 'theo', 'về',
    'nhưng', 'đã', 'sẽ', 'đang', 'cũng', 'ra', 'vào', 'lên', 'xuống', 'năm', 'tháng', 'ngày'
}

TOPICS = {
    'Kinh doanh': 'https://vnexpress.net/kinh-doanh',
    'Thể thao': 'https://vnexpress.net/the-thao',
    'Pháp luật': 'https://vnexpress.net/phap-luat',
    'Thế giới': 'https://vnexpress.net/the-gioi',
    'Đời sống': 'https://vnexpress.net/doi-song',
    'Khoa học công nghệ': 'https://vnexpress.net/khoa-hoc-cong-nghe',
    'Sức khỏe': 'https://vnexpress.net/suc-khoe',
    'Du lịch': 'https://vnexpress.net/du-lich',
    'Giải trí': 'https://vnexpress.net/giai-tri',
    'Giáo dục': 'https://vnexpress.net/giao-duc',

}

# Hàm lọc từ vô nghĩa
def remove_stopwords(text):
    words = text.split()
    # Chỉ giữ lại từ KHÔNG nằm trong STOP_WORDS và độ dài > 1 ký tự
    valid_words = [w for w in words if w not in STOP_WORDS and len(w) > 1]
    return " ".join(valid_words)

def crawl_data_for_training(limit_per_topic=300): # TĂNG SỐ LƯỢNG LÊN 80
    data = []
    print(f"--- BẮT ĐẦU CRAWL ({limit_per_topic} bài/chủ đề) ---")
    
    for label, url in TOPICS.items():
        print(f"\n-> Đang học chủ đề: {label} ", end="")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(resp.content, 'html.parser')
            links = soup.select('.title-news a')
            
            count = 0
            for link in links:
                if count >= limit_per_topic: break
                
                art_url = link.get('href')
                if not art_url or 'video' in art_url or 'http' not in art_url: continue
                
                try:
                    art_resp = requests.get(art_url, headers=HEADERS, timeout=10)
                    art_soup = BeautifulSoup(art_resp.content, 'html.parser')
                    
                    content_list = [p.text for p in art_soup.select('.fck_detail p.Normal')]
                    content = " ".join(content_list)
                    
                    if len(content) > 200: # Chỉ học bài dài > 200 ký tự (bài ngắn quá gây nhiễu)
                        
                        # 1. Tokenize (Tách từ: kinh tế -> kinh_tế)
                        processed_text = word_tokenize(content, format="text")
                        
                        # 2. Lowercase (Chữ thường)
                        processed_text = processed_text.lower()
                        
                        # 3. Remove Stopwords (Lọc nhiễu)
                        processed_text = remove_stopwords(processed_text)
                        
                        data.append({'text': processed_text, 'label': label})
                        count += 1
                        print(".", end="", flush=True) # Hiệu ứng loading
                        
                except:
                    continue
            
        except Exception as e:
            print(f"[LỖI] {label}: {e}")
            
    return pd.DataFrame(data)

def train_and_save_model():
    # 1. Thu thập dữ liệu (Số lượng lớn hơn)
    df = crawl_data_for_training(limit_per_topic=100) 
    
    if df.empty:
        print("\n[LỖI] Không có dữ liệu.")
        return

    print(f"\n\nTổng dữ liệu: {len(df)} bài. Đang huấn luyện...")
    
    X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.15, random_state=42)
    
    # 2. TẠO PIPELINE MẠNH MẼ HƠN
    model = make_pipeline(
        # ngram_range=(1, 2): Học cả từ đơn (đất) và cụm 2 từ (đất_đai)
        # min_df=2: Bỏ qua những từ chỉ xuất hiện 1 lần (từ rác)
        TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=5000),
        
        # C=5.0: Tăng độ phức tạp để model "tự tin" hơn (giảm Regularization)
        LogisticRegression(max_iter=2000, C=5.0, solver='liblinear') 
    )
    
    model.fit(X_train, y_train)
    
    # 3. Đánh giá
    print("\n--- KẾT QUẢ ĐÁNH GIÁ (Mong đợi > 0.90) ---")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    # 4. Lưu model
    os.makedirs('nlp_engine', exist_ok=True)
    joblib.dump(model, 'nlp_engine/news_classifier.pkl')
    print(f"\n>>> ĐÃ NÂNG CẤP TRÍ TUỆ AI! Model saved.")

if __name__ == "__main__":
    train_and_save_model()