# news/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from .crawler_engine import crawler_service

# Biến toàn cục để lưu trạng thái
scheduler = BackgroundScheduler()
is_running = False
current_interval = 30 # Mặc định 30 phút

def start_scheduler():
    global scheduler
    if not scheduler.running:
        scheduler.start()

def update_crawl_job(minutes):
    """Hàm này dùng để BẬT hoặc CẬP NHẬT thời gian crawl"""
    global is_running, current_interval
    
    # Xóa job cũ nếu có
    if scheduler.get_job('crawl_job'):
        scheduler.remove_job('crawl_job')
    
    # Thêm job mới với thời gian mới
    scheduler.add_job(
        crawler_service.crawl_vnexpress, 
        'interval', 
        minutes=int(minutes), 
        id='crawl_job', 
        replace_existing=True
    )
    
    is_running = True
    current_interval = int(minutes)
    print(f"--- Đã SET lịch Auto Crawl: {minutes} phút/lần ---")

def stop_crawl_job():
    """Hàm này dùng để TẮT auto crawl"""
    global is_running
    if scheduler.get_job('crawl_job'):
        scheduler.remove_job('crawl_job')
    
    is_running = False
    print("--- Đã DỪNG Auto Crawl ---")

def get_status():
    return {
        'is_running': is_running,
        'interval': current_interval
    }