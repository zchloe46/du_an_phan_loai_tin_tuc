# news/models.py
from django.db import models
from django.utils.text import slugify
import uuid
from nlp_engine.predictor import classifier # <-- Import bộ não AI

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Tạo slug tự động từ tên (VD: Kinh Doanh -> kinh-doanh)
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Article(models.Model):
    # Thông tin cơ bản
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    content = models.TextField()
    summary = models.TextField(blank=True, null=True) # Tóm tắt 3 dòng
    url = models.CharField(max_length=500, blank=True, null=True) 
    image_url = models.CharField(max_length=500, blank=True, null=True)
    
    # Quan hệ
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='articles')
    confidence = models.FloatField(default=0.0) # Mức độ tin cậy phân loại
    original_confidence = models.FloatField(default=0.0) # Lưu lại điểm AI chấm lúc đầu
    is_reviewed = models.BooleanField(default=False)     # True nếu con người đã chỉnh sửa/duyệt
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    
    # AI & Analytics Fields (Dành cho tính năng Premium)
    sentiment_score = models.FloatField(default=0.0) # Từ -1 (Tiêu cực) đến 1 (Tích cực)
    sentiment_label = models.CharField(max_length=20, default='Neutral') # Tích cực/Tiêu cực
    
    # Meta data
    published_date = models.DateTimeField(auto_now_add=True)
    crawled_at = models.DateTimeField(auto_now_add=True)
    
    # Trạng thái
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')

    def save(self, *args, **kwargs):
        # 1. Tự động tạo Slug (Code cũ)
        if not self.slug:
            base_slug = slugify(self.title)
            if Article.objects.filter(slug=base_slug).exists():
                self.slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
            else:
                self.slug = base_slug

        # 2. Tự động Phân loại bằng AI (Code MỚI)
        # Logic AI
        if not self.category and self.content:
            try:
                # Lấy cả Label và Score
                predicted_label, score = classifier.predict(self.content)
                
                print(f"AI: {predicted_label} - Độ tin cậy: {score:.2f}")
                
                cat_obj, _ = Category.objects.get_or_create(name=predicted_label)
                self.category = cat_obj
                self.confidence = score # Lưu điểm vào DB
                self.original_confidence=score   # Lưu bản sao lưu để làm lịch sử
                self.is_reviewed=False   
            except Exception as e:
                print(f"Lỗi AI: {e}")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_date']