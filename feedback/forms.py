# feedback/forms.py - дополнительная валидация
from django import forms
from django.core.exceptions import ValidationError

class FeedbackForm(forms.Form):
    # Список запрещенных слов (ругательства)
    BAD_WORDS = [
        'дурак', 'идиот', 'кретин', 'дебил', 'тупица', 'олух', 'болван',
        'сволочь', 'подлец', 'негодяй', 'мерзавец'
    ]
    
    name = forms.CharField(
        max_length=100,
        label='Ваше ФИО',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше ФИО (Иванов Иван Иванович)',
            'required': 'true'
        })
    )
    
    email = forms.EmailField(
        label='Email адрес',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.com',
            'required': 'true'
        })
    )
    
    message = forms.CharField(
        label='Сообщение',
        min_length=10,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Напишите ваше сообщение...',
            'required': 'true'
        })
    )
    
    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        
        # Проверяем, что имя содержит только буквы и пробелы
        if not all(c.isalpha() or c.isspace() or c == '-' for c in name):
            raise ValidationError("ФИО может содержать только буквы, пробелы и дефисы")
        
        # Разделяем на слова
        words = name.split()
        
        # Проверяем, что ровно 3 слова
        if len(words) != 3:
            raise ValidationError("Пожалуйста, введите полное ФИО (три слова через пробел)")
        
        # Проверяем, что каждое слово начинается с заглавной буквы
        for word in words:
            if not word[0].isupper():
                raise ValidationError("Каждое слово в ФИО должно начинаться с заглавной буквы")
            
            # Проверяем длину каждого слова
            if len(word) < 2:
                raise ValidationError("Каждое слово в ФИО должно содержать минимум 2 буквы")
        
        # Проверяем на запрещенные слова в имени
        for bad_word in self.BAD_WORDS:
            if bad_word in name.lower():
                raise ValidationError("ФИО содержит недопустимые слова")
        
        # Форматируем имя: каждое слово с заглавной буквы, остальные - строчные
        formatted_name = ' '.join([word.capitalize() for word in words])
        
        return formatted_name
    
    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        
        if len(message) < 10:
            raise ValidationError("Сообщение должно содержать не менее 10 символов")
        
        # Проверяем на запрещенные слова в сообщении
        message_lower = message.lower()
        for bad_word in self.BAD_WORDS:
            if bad_word in message_lower:
                raise ValidationError("Сообщение содержит недопустимые слова. Пожалуйста, измените формулировку.")
        
        return message
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Дополнительная проверка: если email содержит запрещенные слова
        email = cleaned_data.get('email', '').lower()
        for bad_word in self.BAD_WORDS:
            if bad_word in email:
                self.add_error('email', 'Email содержит недопустимые слова')
        
        return cleaned_data