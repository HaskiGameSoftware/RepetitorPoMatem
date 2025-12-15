# tests/test_views.py - дополнительные тесты
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from homepage.models import Course, CourseOrder, Review

@pytest.mark.django_db
class TestBuyCourseView:
    """Тесты для покупки курса"""
    
    def test_buy_course_success(self, client):
        """Тест успешной покупки курса"""
        course = Course.objects.create(
            title="Тестовый курс",
            description="Описание",
            price=1000.00,
            duration="1 месяц",
            is_active=True,
            max_students=10
        )
        
        # Изначально студентов нет
        assert course.students_count == 0
        
        # POST-запрос с данными формы
        data = {
            'student_name': 'Иван Иванов',
            'email': 'ivan@test.com',
            'phone': '+79991234567'
        }
        
        response = client.post(
            reverse('homepage:buy_course', args=[course.id]),
            data
        )
        
        # Должен быть редирект
        assert response.status_code == 302
        
        # Проверяем создание заказа
        assert CourseOrder.objects.count() == 1
        order = CourseOrder.objects.first()
        assert order.student_name == 'Иван Иванов'
        assert order.email == 'ivan@test.com'
        
        # Проверяем обновление счетчика студентов
        course.refresh_from_db()
        assert course.students_count == 1
    
    def test_buy_course_full_course(self, client):
        """Тест покупки заполненного курса"""
        course = Course.objects.create(
            title="Тестовый курс",
            description="Описание",
            price=1000.00,
            duration="1 месяц",
            is_active=True,
            max_students=1  # Только 1 место
        )
        
        # Заполняем курс
        CourseOrder.objects.create(
            course=course,
            course_title=course.title,
            student_name="Первый студент",
            email="first@test.com",
            price=course.price
        )
        
        course.refresh_from_db()
        assert course.is_full is True
        
        # Пытаемся купить заполненный курс
        data = {
            'student_name': 'Второй студент',
            'email': 'second@test.com',
            'phone': '+79991234567'
        }
        
        response = client.post(
            reverse('homepage:buy_course', args=[course.id]),
            data
        )
        
        # Должен быть редирект с ошибкой
        assert response.status_code == 302

@pytest.mark.django_db
class TestAuthViews:
    """Тесты для аутентификации"""
    
    def test_register_success(self, client):
        """Тест успешной регистрации"""
        data = {
            'email': 'newuser@test.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123'
        }
        
        response = client.post(reverse('homepage:register'), data)
        
        # Должен быть редирект после успешной регистрации
        assert response.status_code == 302
        
        # Проверяем создание пользователя
        assert User.objects.filter(email='newuser@test.com').exists()
    
    def test_login_success(self, client):
        """Тест успешного входа"""
        # Создаем пользователя
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        data = {
            'email': 'test@test.com',
            'password': 'testpass123'
        }
        
        response = client.post(reverse('homepage:login'), data)
        
        # Должен быть редирект после успешного входа
        assert response.status_code == 302
    
    def test_login_failure(self, client):
        """Тест неудачного входа"""
        # Пытаемся войти с неверными данными
        data = {
            'email': 'wrong@test.com',
            'password': 'wrongpass'
        }
        
        response = client.post(reverse('homepage:login'), data)
        
        # Должен вернуться на ту же страницу
        assert response.status_code == 200

@pytest.mark.django_db
class TestPersonalCabinetView:
    """Тесты для личного кабинета"""
    
    def test_personal_cabinet_anonymous(self, client):
        """Тест доступа к ЛК без авторизации"""
        response = client.get(reverse('homepage:personal_cabinet'))
        
        # Должен быть редирект на страницу входа
        assert response.status_code == 302
        assert '/login' in response.url
    
    def test_personal_cabinet_authenticated(self, admin_client):
        """Тест доступа к ЛК с авторизацией"""
        response = admin_client.get(reverse('homepage:personal_cabinet'))
        
        assert response.status_code == 200
        assert 'active_courses' in response.context
        assert 'courses' in response.context

@pytest.mark.django_db
class TestCartViews:
    """Тесты для функциональности корзины"""
    
    def test_add_to_cart(self, client, sample_course):
        """Тест добавления курса в корзину"""
        response = client.get(reverse('homepage:add_to_cart', args=[sample_course.id]))
        
        assert response.status_code == 302  # Редирект