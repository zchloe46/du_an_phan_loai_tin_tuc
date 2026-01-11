# news/crawler_engine.py
import requests
from bs4 import BeautifulSoup
from django.utils.text import slugify
from .models import Article, Category, Tag
from nlp_engine.predictor import classifier # Import bộ não AI của mình
from urllib.parse import urlparse, urljoin

# Cấu hình Header giả lập trình duyệt
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

class NewsCrawler:
    def crawl_vnexpress(self, limit=5):
        print("--- Bắt đầu Crawler VnExpress ---")
        
        # Danh sách các mục cần lấy
        targets = [
            {'url': 'https://vnexpress.net/kinh-doanh', 'default_cat': 'Kinh doanh'},
            {'url': 'https://vnexpress.net/the-thao', 'default_cat': 'Thể thao'},
            {'url': 'https://vnexpress.net/phap-luat', 'default_cat': 'Pháp luật'},
            {'url': 'https://vnexpress.net/giai-tri', 'default_cat': 'Giải trí'},
            {'url': 'https://vnexpress.net/suc-khoe', 'default_cat': 'Sức khỏe'},
            {'url': 'https://vnexpress.net/the-gioi', 'default_cat': 'Thế giới'},
            {'url': 'https://vnexpress.net/doi-song', 'default_cat': 'Đời sống'},            
            {'url': 'https://vnexpress.net/khoa-hoc-cong-nghe', 'default_cat': 'Khoa học công nghệ'},
            {'url': 'https://vnexpress.net/du-lich', 'default_cat': 'Du lịch'},
            {'url': 'https://vnexpress.net/giao-duc', 'default_cat': 'Giáo dục'},
        ]
        
        count_new = 0
        
        for target in targets:
            try:
                response = requests.get(target['url'], headers=HEADERS)
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.select('.title-news a')
                
                for link in links[:limit]: # Chỉ lấy số lượng giới hạn mỗi mục
                    url = link.get('href')
                    if not url or 'video' in url or not url.startswith('http'): continue
                    
                    # Kiểm tra trùng lặp (QUAN TRỌNG)
                    if Article.objects.filter(url=url).exists():
                        print(f"Bỏ qua (đã tồn tại): {url}")
                        continue
                        
                    # Vào chi tiết bài viết
                    self.process_article(url)
                    count_new += 1
            except Exception as e:
                print(f"Lỗi section {target['url']}: {e}")
                
        return count_new

    def process_article(self, url):
        try:
            # --- 1. CHUẨN HÓA URL (QUAN TRỌNG) ---
            # Bỏ hết phần ?utm_... hoặc #comment phía sau
            parsed_url = urlparse(url)
            clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            
            # --- 2. KIỂM TRA TRÙNG LẶP CHẶT CHẼ ---
            if Article.objects.filter(url=clean_url).exists():
                print(f"-> Đã tồn tại (Bỏ qua): {clean_url}")
                return

            resp = requests.get(clean_url, headers=HEADERS)
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            title = soup.select_one('.title-detail').text.strip()
            # Lấy ảnh đại diện (để hiển thị lên Dashboard cho đẹp)
            image_url = ""
            meta_img = soup.find("meta", property="og:image")
            if meta_img:
                image_url = meta_img['content']
                
            # Lấy nội dung
            content_list = [p.text for p in soup.select('.fck_detail p.Normal')]
            content = " ".join(content_list)
            
            if not content: return

            # Lưu vào DB (Hàm save của Model sẽ tự gọi AI để phân loại)
            article = Article(
                title=title,
                content=content,
                url=url,
                image_url=image_url, # Lưu ảnh
                summary=content[:250] + "..."
            )
            article.save() # <-- Lúc này AI sẽ nhảy vào phân loại
            print(f"Đã lưu: {title}")
            
        except Exception as e:
            print(f"Lỗi bài {url}: {e}")

# Instance để gọi nhanh
crawler_service = NewsCrawler()