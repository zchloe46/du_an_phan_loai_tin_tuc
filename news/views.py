import traceback
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
import docx
from pypdf import PdfReader
from .models import Article, Category
from .forms import ArticleForm
from .crawler_engine import crawler_service  # Đảm bảo bạn đã có file crawler_engine.py
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from django.http import JsonResponse
from . import scheduler as my_scheduler
# Thêm các import cần thiết cho thống kê
from django.db.models import Count, Avg
from django.db.models.functions import TruncDay
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from .crawler_engine import crawler_service
from nlp_engine.predictor import classifier
import re
from django.db.models import Count
from .forms import CategoryForm

# ---------------------------------------------------------
# 1. TRANG DASHBOARD (DANH SÁCH + TÌM KIẾM + LỌC)
# ---------------------------------------------------------
def dashboard_home(request):
    # 1. LẤY DỮ LIỆU GỐC VÀ SẮP XẾP MẶC ĐỊNH
    articles_list = Article.objects.all().select_related('category').order_by('-published_date')
    categories = Category.objects.all()

    # 2. XỬ LÝ BỘ LỌC KẾT HỢP
    search_query = request.GET.get('q', '')
    cat_slug = request.GET.get('category', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    if search_query:
        articles_list = articles_list.filter(Q(title__icontains=search_query) | Q(summary__icontains=search_query))
    if cat_slug:
        articles_list = articles_list.filter(category__slug=cat_slug)
    
    # LỌC THEO ĐỘ TIN CẬY
    conf_level = request.GET.get('confidence_level', '')
    if conf_level == 'high':
        articles_list = articles_list.filter(confidence__gte=0.8)
    elif conf_level == 'medium':
        articles_list = articles_list.filter(confidence__gte=0.5, confidence__lt=0.8)
    elif conf_level == 'low':
        articles_list = articles_list.filter(confidence__lt=0.5)
        
    # Lọc theo ngày tháng
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            articles_list = articles_list.filter(published_date__date__range=[start_date, end_date])
        except ValueError:
            pass # Bỏ qua nếu ngày không hợp lệ

    # 3. THIẾT LẬP PHÂN TRANG (PAGINATION)
    paginator = Paginator(articles_list, 10) # 10 bài viết mỗi trang
    page_number = request.GET.get('page')
    try:
        articles = paginator.get_page(page_number)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    # 4. TRẢ VỀ CONTEXT
    context = {
        'articles': articles, # Đây là page_obj, không phải articles_list
        'categories': categories,
        'total_articles': articles_list.count(), # Lấy tổng số trước khi phân trang
        'current_cat': cat_slug,
        'search_query': search_query,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'conf_level': conf_level, # Mức độ tin cậy hiện tại
    }
    return render(request, 'dashboard/home.html', context) 
# ---------------------------------------------------------
# 2. CHỨC NĂNG CRAWL (THỦ CÔNG)
# ---------------------------------------------------------
def trigger_crawl(request):
    # Lấy nguồn từ URL (VD: ?source=dantri), mặc định là 'vnexpress'
    source = request.GET.get('source', 'vnexpress')
    
    def run_in_background():
        # Truyền tham số source vào crawler (Bạn cần update logic crawler_engine sau để xử lý logic này)
        # Tạm thời ta vẫn gọi hàm cũ, nhưng in ra log để biết đang chọn nguồn nào
        print(f"--- Đang chạy Crawler nguồn: {source} ---")
        crawler_service.crawl_vnexpress(limit=10) 
        
    import threading
    thread = threading.Thread(target=run_in_background)
    thread.start()
    
    # Map tên nguồn để hiển thị thông báo đẹp hơn
    source_names = {
        'vnexpress': 'VnExpress',
        'dantri': 'Dân Trí',
        'tuoitre': 'Tuổi Trẻ',
        'all': 'Tất cả nguồn'
    }
    name = source_names.get(source, source)
    
    messages.success(request, f"Hệ thống đang quét tin từ {name}. Vui lòng chờ!")
    return redirect('home')

# ---------------------------------------------------------
# 3. CRUD: THÊM BÀI VIẾT MỚI
# ---------------------------------------------------------
# news/views.py

def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        
        # Kiểm tra tính hợp lệ
        if form.is_valid():
            instance = form.save(commit=False)
            
            # Logic AI (Giữ nguyên code của bạn)
            if not instance.confidence or instance.confidence == 0:
                 if instance.content:
                     try:
                         label, score = classifier.predict(instance.content)
                         instance.confidence = score
                         if not instance.category:
                             cat, _ = Category.objects.get_or_create(name=label)
                             instance.category = cat
                     except:
                         pass

            instance.save()
            messages.success(request, 'Thêm bài viết thành công!')
            return redirect('home')
            
        else:
            # --- THÊM ĐOẠN NÀY ĐỂ DEBUG ---
            print("--- LỖI FORM INVALID ---")
            print(form.errors) # Nó sẽ in ra dòng chữ đỏ ở terminal cho bạn biết sai ở đâu
            messages.error(request, 'Lỗi nhập liệu: Vui lòng kiểm tra lại các trường báo đỏ.')
            
    else:
        form = ArticleForm()
        
    return render(request, 'dashboard/article_form.html', {'form': form, 'title': 'Thêm bài mới'})

# ---------------------------------------------------------
# 4. CRUD: SỬA BÀI VIẾT
# ---------------------------------------------------------
def article_update(request, pk):
    article = get_object_or_404(Article, pk=pk)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            instance = form.save(commit=False)
            
            # --- LOGIC CON NGƯỜI CAN THIỆP ---
            # Nếu người dùng nhấn Lưu, nghĩa là họ đã xác nhận nội dung này đúng
            instance.is_reviewed = True
            instance.confidence = 1.0 # Tuyệt đối tin cậy (100%)
            
            instance.save()
            messages.success(request, 'Đã cập nhật và xác thực bài viết!')
            return redirect('home')
    else:
        form = ArticleForm(instance=article)
        
    return render(request, 'dashboard/article_form.html', {'form': form, 'title': 'Sửa bài viết'})

# ---------------------------------------------------------
# 5. CRUD: XÓA BÀI VIẾT
# ---------------------------------------------------------
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    
    # Chỉ xử lý khi là POST (bấm nút xác nhận)
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Đã xóa bài viết thành công!')
        return redirect('home')
        
    # Nếu ai đó cố tình truy cập GET, ta cũng redirect về home hoặc hiện trang confirm (tùy chọn)
    # Ở đây redirect luôn cho gọn, vì ta dùng confirm JS rồi.
    return redirect('home')


def configure_crawler(request):
    """API để Bật/Tắt và chỉnh thời gian Crawl"""
    if request.method == 'POST':
        action = request.POST.get('action') # 'start' hoặc 'stop'
        minutes = request.POST.get('minutes', 30)
        
        if action == 'start':
            my_scheduler.update_crawl_job(minutes)
            return JsonResponse({'status': 'running', 'interval': minutes, 'message': f'Đã bật Auto Crawl ({minutes} phút/lần)'})
        
        elif action == 'stop':
            my_scheduler.stop_crawl_job()
            return JsonResponse({'status': 'stopped', 'message': 'Đã dừng Auto Crawl'})
            
    # GET: Trả về trạng thái hiện tại (để UI cập nhật khi F5)
    status = my_scheduler.get_status()
    return JsonResponse(status)

def dashboard_stats(request):
    # 1. THỐNG KÊ TỔNG QUAN (CARD)
    total_articles = Article.objects.count()
    # Tính số bài hôm nay
    today = datetime.now().date()
    articles_today = Article.objects.filter(published_date__date=today).count()
    # Độ tin cậy trung bình của AI
    avg_confidence = Article.objects.aggregate(Avg('confidence'))['confidence__avg'] or 0
    
    # 2. BIỂU ĐỒ 1: SỐ LƯỢNG BÀI VIẾT THEO NGÀY (7 ngày gần nhất)
    # Group by ngày và đếm
    timeline_data = Article.objects.annotate(date=TruncDay('published_date'))\
        .values('date')\
        .annotate(count=Count('id'))\
        .order_by('date')
    
    # Chuyển dữ liệu thành List để vẽ biểu đồ
    dates = [item['date'].strftime("%d/%m") for item in timeline_data]
    counts = [item['count'] for item in timeline_data]

    # 3. BIỂU ĐỒ 2: TỶ LỆ CÁC CHỦ ĐỀ (PIE CHART)
    category_data = Article.objects.values('category__name')\
        .annotate(count=Count('id'))\
        .order_by('-count')
    
    cat_names = [item['category__name'] if item['category__name'] else 'Chưa phân loại' for item in category_data]
    cat_counts = [item['count'] for item in category_data]

    # 4. BIỂU ĐỒ 3: TOP 5 NGUỒN TIN (Nếu bạn lưu domain)
    # Tạm thời ta demo thống kê theo độ tin cậy AI (Histogram)
    # Đếm số bài theo các mức tin cậy: Cao (>80%), Trung bình (50-80%), Thấp (<50%)
    high_conf = Article.objects.filter(confidence__gte=0.8).count()
    med_conf = Article.objects.filter(confidence__gte=0.5, confidence__lt=0.8).count()
    low_conf = Article.objects.filter(confidence__lt=0.5).count()

    context = {
        'total_articles': total_articles,
        'articles_today': articles_today,
        'avg_confidence': round(avg_confidence * 100, 1),
        
        # Dữ liệu biểu đồ (Chuyển sang JSON để JS đọc được)
        'chart_dates': json.dumps(dates),
        'chart_counts': json.dumps(counts),
        'cat_names': json.dumps(cat_names),
        'cat_counts': json.dumps(cat_counts),
        'conf_data': json.dumps([high_conf, med_conf, low_conf]),
    }
    return render(request, 'dashboard/statistics.html', context)

def api_analyze_content(request):
    """API hỗ trợ chức năng Thêm bài thông minh"""
    if request.method == 'POST':
        try:
            # Khởi tạo biến
            url = ''
            content = ''
            
            # --- KIỂM TRA: CÓ PHẢI UPLOAD FILE KHÔNG? ---
            if request.FILES.get('file_upload'):
                uploaded_file = request.FILES['file_upload']
                file_name = uploaded_file.name.lower()
                
                try:
                    # 1. Xử lý file .TXT
                    if file_name.endswith('.txt'):
                        content = uploaded_file.read().decode('utf-8')
                        
                    # 2. Xử lý file .DOCX (Word)
                    elif file_name.endswith('.docx'):
                        doc = docx.Document(uploaded_file)
                        content = "\n".join([para.text for para in doc.paragraphs])
                        
                    # 3. Xử lý file .PDF
                    elif file_name.endswith('.pdf'):
                        reader = PdfReader(uploaded_file)
                        content = ""
                        for page in reader.pages:
                            content += page.extract_text() + "\n"
                    
                    else:
                        return JsonResponse({'error': 'Chỉ hỗ trợ file .txt, .docx, .pdf'}, status=400)
                        
                except Exception as e:
                    return JsonResponse({'error': f'Lỗi đọc file: {str(e)}'}, status=400)

            # --- KIỂM TRA: HAY LÀ GỬI JSON (URL/TEXT)? ---
            elif request.body:
                try:
                    data = json.loads(request.body)
                    url = data.get('url', '').strip()
                    content = data.get('content', '').strip()
                except:
                    pass # Body rỗng hoặc không phải JSON hợp lệ
            result = {}

            # TRƯỜNG HỢP 1: CÓ URL -> CRAWL TỪ URL
            if url:
                try:
                    # Tận dụng crawler có sẵn nhưng chỉnh lại chút để chỉ return data chứ ko save
                    # Ở đây tôi viết logic nhanh để lấy dữ liệu single page
                    import requests
                    from bs4 import BeautifulSoup
                    
                    headers = {'User-Agent': 'Mozilla/5.0 ...'}
                    resp = requests.get(url, headers=headers, timeout=10)
                    soup = BeautifulSoup(resp.content, 'html.parser')
                    
                    # Lấy tiêu đề nếu không có tiêu đề thì sinh tiêu đề từ code phân loại                                        
                    # title = soup.select_one('h1').text.strip() if soup.select_one('h1') else ''
                    title = ''
                    if soup.select_one('.title-detail'):
                        title = soup.select_one('.title-detail').text.strip()
                    
                    # Lấy nội dung (Thử nhiều selector phổ biến)
                    content_text = ""
                    for selector in ['.fck_detail', '.content-detail', 'article', '.post-content']:
                        if soup.select_one(selector):
                            content_text = " ".join([p.text for p in soup.select(f'{selector} p')])
                            break
                    
                    # Lấy ảnh
                    image_url = ""
                    meta_img = soup.find("meta", property="og:image")
                    if meta_img: image_url = meta_img['content']

                    result = {
                        'title': title,
                        'content': content_text,
                        'image_url': image_url,
                        'url': url
                    }
                    
                    # Nếu crawl được content thì chạy AI phân loại luôn
                    if content_text:
                        cat_label, score = classifier.predict(content_text)                        
                        result['category'] = cat_label
                        raw_summary = content_text[:300] # Lấy 300 ký tự đầu thôi cho an toàn
                        if len(raw_summary) > 250: 
                            raw_summary = raw_summary[:250] + "..."
                            result['summary'] = raw_summary
                        result['confidence'] = score

                except Exception as e:
                    return JsonResponse({'error': f'Lỗi Crawl: {str(e)}'}, status=400)

            # TRƯỜNG HỢP 2: CHỈ CÓ TEXT -> SINH TITLE, SUMMARY, CATEGORY
            elif content:
                # Sinh tiêu đề
                sentences = re.split(r'(?<=[.!?]) +', content)
                first_sentence = sentences[0] if sentences else content
                generated_title = " ".join(first_sentence.split()[:15])
                
                # Sinh tóm tắt (CẮT NGẮN ĐỂ TRÁNH LỖI DB)
                summary = " ".join(sentences[:3])
                if len(summary) > 490: summary = summary[:490] + "..."
                
                # Chạy AI
                cat_label = "Chưa phân loại"
                score = 0.0
                try:
                    cat_label, score = classifier.predict(content)
                except:
                    pass

                result = {
                    'title': generated_title,
                    'summary': summary,
                    'category': cat_label,
                    'confidence': float(score),
                    'content': content, # Trả về nội dung gốc
                    'image_url': '',
                    'url': ''
                }

            else:
                return JsonResponse({'error': 'Vui lòng nhập URL, Text hoặc Upload file'}, status=400)

            return JsonResponse(result)

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': f'Lỗi hệ thống: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# 1. Danh sách Category (Kèm thống kê số bài)
def category_list(request):
    # annotate(num_articles=Count('articles')): Đếm số bài viết trong từng category
    categories = Category.objects.annotate(num_articles=Count('articles')).order_by('-num_articles')
    
    return render(request, 'dashboard/category_list.html', {
        'categories': categories,
    })

# 2. Xử lý Lưu (Thêm mới hoặc Sửa)
def category_save(request, pk=None):
    if pk:
        category = get_object_or_404(Category, pk=pk)
        action = "Cập nhật"
    else:
        category = None
        action = "Thêm mới"

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã {action} danh mục thành công!')
            return redirect('category_list')
        else:
            messages.error(request, 'Lỗi! Vui lòng kiểm tra lại thông tin.')
    
    return redirect('category_list')

# 3. Xóa Category
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        # Kiểm tra xem có bài viết nào không?
        if category.articles.exists():
            messages.warning(request, f'Không thể xóa "{category.name}" vì đang chứa bài viết. Hãy chuyển bài viết sang mục khác trước!')
        else:
            category.delete()
            messages.success(request, 'Đã xóa danh mục!')
            
    return redirect('category_list')

def about_page(request):
    return render(request, 'dashboard/about.html')