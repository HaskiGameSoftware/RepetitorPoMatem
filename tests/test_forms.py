# tests/test_forms.py
import pytest
from feedback.forms import FeedbackForm

def test_feedback_form_valid():
    """Тест валидной формы"""
    form_data = {
        'name': 'Иванов Иван Иванович',
        'email': 'ivanov@example.com',
        'message': 'Хороший сайт, все понравилось! Минимум 10 символов.'
    }
    
    form = FeedbackForm(data=form_data)
    assert form.is_valid() is True
    assert form.cleaned_data['name'] == 'Иванов Иван Иванович'

def test_feedback_form_name_too_short():
    """Тест слишком короткого имени"""
    form_data = {
        'name': 'Ив',
        'email': 'test@test.com',
        'message': 'Сообщение достаточной длины для теста.'
    }
    
    form = FeedbackForm(data=form_data)
    assert form.is_valid() is False
    assert 'name' in form.errors

def test_feedback_form_message_too_short():
    """Тест слишком короткого сообщения"""
    form_data = {
        'name': 'Иванов Иван Иванович',
        'email': 'test@test.com',
        'message': 'Коротко'  # Менее 10 символов
    }
    
    form = FeedbackForm(data=form_data)
    assert form.is_valid() is False
    assert 'message' in form.errors