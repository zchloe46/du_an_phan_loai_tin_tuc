# import_data.py
import os
import django
import pandas as pd
from django.utils.text import slugify

# Cấu hình để chạy script độc lập với Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from news.models import Article, Category

def run_import():
    csv_path = 'dataset_demo.csv'
    if not os.path.exists(csv_path):
        print("Không tìm thấy file csv!")
        return

    df = pd.read_csv(csv_path)
    count = 0
    
    print("Bắt đầu import dữ liệu vào MySQL...")
    
    for index, row in df.iterrows():
        title = row['Title']
        content = row['Content']
        label = row['Label'] # Category
        
        # 1. Xử lý Category (Nếu chưa có thì tạo mới)
        category, created = Category.objects.get_or_create(name=label)
        
        # 2. Tạo bài viết
        # Giả lập URL vì trong csv demo ta không lưu URL (bạn có thể sửa crawler để lưu thêm url)
        fake_url = f"https://vnexpress.net/demo-{slugify(title[:20])}-{index}.html"
        
        if not Article.objects.filter(title=title).exists():
            Article.objects.create(
                title=title,
                content=content,
                category=category,
                url=fake_url, # Lưu ý: Crawler thực tế cần lưu URL thật
                summary=content[:200] + "..." # Tạm lấy 200 ký tự đầu làm tóm tắt
            )
            count += 1
            print(f"Imported: {title[:30]}...")
            
    print(f"Hoàn tất! Đã thêm {count} bài viết mới.")

if __name__ == '__main__':
    run_import()