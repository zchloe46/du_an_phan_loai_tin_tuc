# Dự án Phân Loại Tin Tức

Hệ thống phân loại tin tức tự động sử dụng Machine Learning và Django để thu thập, phân loại và quản lý tin tức tiếng Việt.

## Tính năng

- 🤖 **Phân loại tự động**: Sử dụng AI để phân loại tin tức vào các danh mục (Chính trị Xã hội, Đời sống, Khoa học, Kinh doanh, Pháp luật, Sức khỏe, Thế giới, Thể thao, Văn hóa)
- 🕷️ **Thu thập tin tức**: Crawler tự động thu thập tin tức từ các nguồn
- 📊 **Dashboard quản lý**: Giao diện quản lý và xem thống kê tin tức
- ✅ **Xem xét thủ công**: Hỗ trợ xem xét và chỉnh sửa phân loại thủ công
- 🔄 **Lập lịch tự động**: Tự động thu thập và phân loại tin tức theo lịch

## Công nghệ sử dụng

- **Backend**: Django 4.2
- **Machine Learning**: scikit-learn, underthesea
- **Database**: MySQL
- **Task Queue**: Celery (tùy chọn)
- **Web Scraping**: BeautifulSoup4, lxml

## Yêu cầu hệ thống

- Python 3.8+
- MySQL 5.7+ hoặc 8.0+
- pip

## Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/your-username/du_an_phan_loai_tin_tuc.git
cd du_an_phan_loai_tin_tuc
```

### 2. Tạo virtual environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường

Tạo file `.env` từ template:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env` với thông tin của bạn:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=vietnam_news_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

### 5. Tạo database MySQL

```sql
CREATE DATABASE vietnam_news_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Chạy migrations

```bash
python manage.py migrate
```

### 7. Tạo superuser (tùy chọn)

```bash
python manage.py createsuperuser
```

### 8. Chạy server

```bash
python manage.py runserver
```

Truy cập: http://127.0.0.1:8000

## Sử dụng

### Training model

Để train lại model phân loại:

```bash
python train_from_vntc.py
```

Hoặc:

```bash
python train_new_ai.py
```

### Import dữ liệu

```bash
python import_data.py
```

### Chạy crawler demo

```bash
python crawler_demo.py
```

## Cấu trúc dự án

```
du_an_phan_loai_tin_tuc/
├── core/                 # Django settings và cấu hình
├── news/                 # App chính - quản lý tin tức
│   ├── models.py        # Models (Article, Category, Tag)
│   ├── views.py         # Views
│   ├── crawler_engine.py # Engine thu thập tin tức
│   └── scheduler.py     # Lập lịch tự động
├── dashboard/            # App dashboard quản lý
├── nlp_engine/          # Engine phân loại AI
│   ├── predictor.py     # Model predictor
│   └── news_classifier.pkl # Model đã train
├── templates/            # HTML templates
├── static/              # CSS, JS, images
├── media/               # Media files (datasets, images)
├── requirements.txt     # Python dependencies
└── manage.py           # Django management script
```

## Lưu ý

- File `news_classifier.pkl` cần được train trước khi sử dụng
- Dataset trong thư mục `media/Train_Full/` không được commit lên Git (quá lớn)
- Cần cấu hình MySQL trước khi chạy migrations
- SECRET_KEY trong production nên được bảo mật kỹ

## Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

## License

MIT License

