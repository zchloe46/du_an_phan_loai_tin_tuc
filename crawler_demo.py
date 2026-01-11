# crawler_demo.py
import sys
import requests
from bs4 import BeautifulSoup
import csv
import time

# Giả lập trình duyệt để không bị chặn
sys.stdout.reconfigure(encoding='utf-8')
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def get_articles(category_url, label, limit=20):
    data = []
    print(f"Đang crawl mục: {label}...")
    
    response = requests.get(category_url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Lấy các link bài viết (Cấu trúc này có thể thay đổi tùy VnExpress update)
    # Đây là demo logic chung
    links = soup.select('.title-news a') 
    
    count = 0
    for link in links:
        if count >= limit: break
        url = link.get('href')
        
        # Bỏ qua video hoặc link quảng cáo
        if 'video' in url or 'https' not in url: continue 
        
        try:
            art_resp = requests.get(url, headers=HEADERS)
            art_soup = BeautifulSoup(art_resp.content, 'html.parser')
            
            # Lấy tiêu đề và nội dung
            title = art_soup.select_one('.title-detail').text.strip()
            # Ghép các đoạn văn lại
            content = " ".join([p.text for p in art_soup.select('.fck_detail p.Normal')])
            
            if content:
                data.append([title, content, label])
                count += 1
                print(f" - Đã lấy: {title[:30]}...")
        except Exception as e:
            print(f"Lỗi link {url}: {e}")
            
    return data

# Chạy thử
if __name__ == "__main__":
    # Danh sách các lĩnh vực và url tương ứng
    categories = [
        ("https://vnexpress.net/kinh-doanh", "Kinh doanh"),
        ("https://vnexpress.net/the-thao", "Thể thao"),
        ("https://vnexpress.net/phap-luat", "Pháp luật"),
        ("https://vnexpress.net/chinh-tri", "Chính trị"),
        ("https://vnexpress.net/suc-khoe", "Sức khỏe"),
        ("https://vnexpress.net/the-gioi", "Thế giới"),
        ("https://vnexpress.net/so-hoa", "Vi tính"),
        ("https://vnexpress.net/khoa-hoc", "Khoa học"),
        ("https://vnexpress.net/giai-tri/van-hoa", "Văn hóa"),
        ("https://vnexpress.net/cong-nghe", "Công nghệ"),
    ]

    all_news = []
    for url, label in categories:
        all_news += get_articles(url, label)

    # Lưu ra file CSV để dùng cho bước sau
    with open('dataset_demo.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Content', 'Label'])
        writer.writerows(all_news)
    print("Xong! Đã có dữ liệu demo.")