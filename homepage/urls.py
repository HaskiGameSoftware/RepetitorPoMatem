# homepage/urls.py
from django.urls import path
from . import views

app_name = 'homepage'

urlpatterns = [
    path('', views.index, name='index'),
    path('personal-cabinet/', views.personal_cabinet, name='personal_cabinet'),
    path('buy-course/<int:course_id>/', views.buy_course, name='buy_course'),
    path('leave-review/', views.leave_review, name='leave_review'),
    path('courses/', views.courses, name='courses'),
    path('reviews/', views.all_reviews, name='all_reviews'),
    
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),  # ДОБАВИТЬ ЭТУ СТРОКУ
    
    # Восстановление пароля
    path('password-reset/', views.password_reset, name='password_reset'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:course_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
]