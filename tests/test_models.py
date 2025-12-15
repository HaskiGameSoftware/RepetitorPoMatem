# tests/test_models.py - дополнительные тесты
import pytest
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from datetime import date
from homepage.models import Course, CourseOrder, UserProfile, UserCourse, Review, Cart, CartItem

@pytest.mark.django_db
class TestCourseOrderModel:
    """Тесты для модели CourseOrder"""
    
    def test_create_course_order(self):
        """Тест создания заказа курса"""
        course = Course.objects.create(
            title="Математика",
            description="Описание",
            price=5000.00,
            duration="3 месяца"
        )
        
        order = CourseOrder.objects.create(
            course=course,
            course_title=course.title,
            student_name="Иван Иванов",
            email="ivan@test.com",
            phone="+79991234567",
            price=course.price
        )
        
        assert order.student_name == "Иван Иванов"
        assert order.email == "ivan@test.com"
        assert order.is_completed is False
        assert str(order) == f"Математика - Иван Иванов"
    
    def test_course_order_auto_lookup(self):
        """Тест автоматического поиска курса по названию при сохранении"""
        course = Course.objects.create(
            title="Математика продвинутая",
            description="Описание",
            price=5000.00,
            duration="3 месяца"
        )
        
        order = CourseOrder(
            course_title="Математика продвинутая",
            student_name="Иван Иванов",
            email="ivan@test.com",
            price=5000.00
        )
        order.save()  # Должен найти и связать курс
        
        assert order.course == course

@pytest.mark.django_db
class TestUserProfileModel:
    """Тесты для модели UserProfile"""
    
    def test_create_user_profile(self):
        """Тест создания профиля пользователя"""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        
        profile = UserProfile.objects.create(
            user=user,
            phone="+79991234567",
            birth_date=date(2000, 1, 1)
        )
        
        assert profile.user == user
        assert profile.phone == "+79991234567"
        assert str(profile) == "testuser"

@pytest.mark.django_db
class TestReviewModel:
    """Тесты для модели Review"""
    
    def test_create_review(self):
        """Тест создания отзыва"""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        
        course = Course.objects.create(
            title="Математика",
            description="Описание",
            price=5000.00,
            duration="3 месяца"
        )
        
        review = Review.objects.create(
            user=user,
            course=course,
            student_name="Иван Иванов",
            text="Отличный курс, всем рекомендую!",
            rating_explanation=5,
            rating_approach=4,
            rating_preparation=5,
            rating_support=4,
            rating_overall=5
        )
        
        assert review.user == user
        assert review.course == course
        assert review.text == "Отличный курс, всем рекомендую!"
        assert review.is_approved is False
        assert review.get_ratings_dict()['explanation'] == 5
        assert review.get_ratings_dict()['overall'] == 5

@pytest.mark.django_db
class TestCartModels:
    """Тесты для моделей Cart и CartItem"""
    
    def test_create_cart(self):
        """Тест создания корзины"""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        
        cart = Cart.objects.create(user=user)
        
        assert cart.user == user
        assert cart.is_active is True
        assert cart.items_count == 0
        assert cart.total_price == 0
    
    def test_cart_with_items(self):
        """Тест корзины с товарами"""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        
        course1 = Course.objects.create(
            title="Курс 1",
            description="Описание 1",
            price=1000.00,
            duration="1 месяц"
        )
        
        course2 = Course.objects.create(
            title="Курс 2",
            description="Описание 2",
            price=2000.00,
            duration="2 месяца"
        )
        
        cart = Cart.objects.create(user=user)
        
        item1 = CartItem.objects.create(cart=cart, course=course1, quantity=2)
        item2 = CartItem.objects.create(cart=cart, course=course2, quantity=1)
        
        assert cart.items_count == 2
        assert cart.total_price == 4000.00  # 1000*2 + 2000*1
        assert item1.total_price == 2000.00
        assert item2.total_price == 2000.00