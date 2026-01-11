# news/templatetags/color_filters.py
from django import template

register = template.Library()

@register.filter
def category_color(value):
    """
    Input: Tên category (VD: Kinh doanh)
    Output: Class màu của Tailwind CSS
    """
    colors = {
        'Kinh doanh': 'bg-blue-100 text-blue-800 border-blue-200',
        'Thể thao': 'bg-green-100 text-green-800 border-green-200',
        'Pháp luật': 'bg-red-100 text-red-800 border-red-200',
        'Khoa học công nghệ': 'bg-purple-100 text-purple-800 border-purple-200',
        'Giải trí': 'bg-pink-100 text-pink-800 border-pink-200',
        'Sức khỏe': 'bg-yellow-100 text-yellow-800 border-yellow-200',
        'Thế giới': 'bg-indigo-100 text-indigo-800 border-indigo-200',
        'Đời sống': 'bg-teal-100 text-teal-800 border-teal-200',        
        'Du lịch': 'bg-amber-100 text-amber-800 border-amber-200',
        'Giáo dục': 'bg-lime-100 text-lime-800 border-lime-200',
    }
    # Mặc định là màu xám
    return colors.get(value, 'bg-gray-100 text-gray-800 border-gray-200')