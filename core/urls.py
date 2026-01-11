from django.contrib import admin
from django.urls import path
from news import views  

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Dashboard chính
    path('', views.dashboard_home, name='home'),
    
    # Crawl thủ công
    path('crawl-now/', views.trigger_crawl, name='trigger_crawl'),
    
    # CRUD (Thêm/Sửa/Xóa)
    path('article/add/', views.article_create, name='article_create'),
    path('article/<int:pk>/edit/', views.article_update, name='article_update'),
    path('article/<int:pk>/delete/', views.article_delete, name='article_delete'),

    path('api/crawler-config/', views.configure_crawler, name='crawler_config'),
    path('statistics/', views.dashboard_stats, name='statistics'),
    path('api/analyze/', views.api_analyze_content, name='api_analyze'),
    path('about/', views.about_page, name='about'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/save/', views.category_save, name='category_create'),          # URL tạo mới
    path('categories/save/<int:pk>/', views.category_save, name='category_update'), # URL cập nhật
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
]