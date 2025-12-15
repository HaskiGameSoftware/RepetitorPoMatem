# tests/conftest.py
"""
Конфигурация pytest для Django проекта
"""
import pytest
from django.contrib.auth.models import User
from django.test import Client

@pytest.fixture
def client():
    """Фикстура для тестового клиента"""
    return Client()

@pytest.fixture
def admin_user():
    """Фикстура для пользователя с правами администратора"""
    return User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='adminpass123'
    )

@pytest.fixture
def admin_client(client, admin_user):
    """Фикстура для клиента с правами администратора"""
    client.force_login(admin_user)
    return client

@pytest.fixture
def sample_course():
    """Фикстура для тестового курса"""
    from homepage.models import Course
    return Course.objects.create(
        title="Тестовый курс математики",
        description="Описание тестового курса",
        price=5000.00,
        duration="3 месяца",
        max_students=15
    )