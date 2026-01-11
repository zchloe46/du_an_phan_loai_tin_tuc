# news/forms.py
from django import forms
from .models import Article, Category

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'summary', 'category', 'image_url', 'url', 'status', 'confidence']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500'}),
            'url': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Có thể để trống'}),
            'image_url': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Có thể để trống'}),
            'summary': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border rounded-lg'}),
            'content': forms.Textarea(attrs={'rows': 10, 'class': 'w-full px-4 py-2 border rounded-lg'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            # THÊM WIDGET CHO CONFIDENCE (Ẩn đi)
            'confidence': forms.HiddenInput(),
        }

        

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description'] # Slug tự sinh nên không cần nhập
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500', 'placeholder': 'Ví dụ: Kinh tế, Thể thao...'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500', 'placeholder': 'Mô tả ngắn về danh mục này...'}),
        }   

def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Đảm bảo Django không bắt buộc nhập ở phía Backend
        self.fields['url'].required = False
        self.fields['image_url'].required = False
        self.fields['summary'].required = False
        self.fields['confidence'].required = False