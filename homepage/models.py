from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    """Модель для хранения курсов"""
    title = models.CharField(max_length=200, verbose_name='Название курса')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    duration = models.CharField(max_length=100, verbose_name='Продолжительность')
    max_students = models.IntegerField(default=15, verbose_name='Максимальное количество студентов')
    is_active = models.BooleanField(default=True, verbose_name='Активный курс')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['created_at']
    
    def __str__(self):
        return self.title
    
    def get_students_count(self):
        """Получить количество записавшихся на курс"""
        return CourseOrder.objects.filter(course_title=self.title).count()
    
    @property
    def students_count(self):
        """Свойство для получения количества студентов"""
        return self.get_students_count()
    
    @property
    def available_slots(self):
        """Свойство для получения количества свободных мест"""
        return self.max_students - self.get_students_count()
    
    @property
    def is_full(self):
        """Свойство для проверки, заполнен ли курс"""
        return self.get_students_count() >= self.max_students

class CourseOrder(models.Model):
    course = models.ForeignKey(
        'Course', 
        on_delete=models.CASCADE, 
        verbose_name='Курс',
        related_name='orders',
        null=True,  # Сначала разрешаем null для миграции
        blank=True
    )
    course_title = models.CharField(max_length=200, verbose_name='Название курса')
    student_name = models.CharField(max_length=100, verbose_name='Имя ученика')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон', blank=True)
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    is_completed = models.BooleanField(default=False, verbose_name='Заказ выполнен')
    
    class Meta:
        verbose_name = 'Заказ курса'
        verbose_name_plural = 'Заказы курсов'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.course_title} - {self.student_name}"
    
    def save(self, *args, **kwargs):
        # Если не указан курс, ищем его по названию
        if not self.course and self.course_title:
            try:
                course = Course.objects.get(title=self.course_title)
                self.course = course
            except Course.DoesNotExist:
                pass
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Аватар')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return self.user.username
    
class UserCourse(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('completed', 'Завершенный'),
        ('cancelled', 'Отмененный'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    course_order = models.ForeignKey(CourseOrder, on_delete=models.CASCADE, verbose_name='Заказ курса', related_name='user_courses')
    course_id = models.IntegerField(verbose_name='ID курса')
    course_title = models.CharField(max_length=200, verbose_name='Название курса')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    start_date = models.DateField(auto_now_add=True, verbose_name='Дата начала')
    end_date = models.DateField(null=True, blank=True, verbose_name='Дата завершения')
    
    class Meta:
        verbose_name = 'Курс пользователя'
        verbose_name_plural = 'Курсы пользователей'
        unique_together = ['user', 'course_order']
    
    def __str__(self):
        return f"{self.user.username} - {self.course_title} ({self.get_status_display()})"

class Review(models.Model):
    """Модель для хранения отзывов"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        verbose_name='Курс', 
        null=True, 
        blank=True,
        related_name='reviews'
    )
    student_name = models.CharField(max_length=100, verbose_name='Имя ученика')
    text = models.TextField(verbose_name='Текст отзыва')
    
    # Рейтинги
    rating_explanation = models.IntegerField(verbose_name='Объяснение материала', choices=[(i, i) for i in range(1, 6)])
    rating_approach = models.IntegerField(verbose_name='Индивидуальный подход', choices=[(i, i) for i in range(1, 6)])
    rating_preparation = models.IntegerField(verbose_name='Качество подготовки', choices=[(i, i) for i in range(1, 6)])
    rating_support = models.IntegerField(verbose_name='Поддержка ученика', choices=[(i, i) for i in range(1, 6)])
    rating_overall = models.IntegerField(verbose_name='Общее впечатление', choices=[(i, i) for i in range(1, 6)])
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_approved = models.BooleanField(default=False, verbose_name='Одобрен')
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Отзыв от {self.user.username} о курсе {self.course.title if self.course else 'Не указан'}"
    
    def get_ratings_dict(self):
        """Получить рейтинги в виде словаря"""
        return {
            'explanation': self.rating_explanation,
            'approach': self.rating_approach,
            'preparation': self.rating_preparation,
            'support': self.rating_support,
            'overall': self.rating_overall
        }

class Cart(models.Model):
    """Модель корзины"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Пользователь',
        related_name='carts'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_active = models.BooleanField(default=True, verbose_name='Активная корзина')
    
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Корзина пользователя {self.user.username}"
    
    @property
    def total_price(self):
        """Общая стоимость товаров в корзине"""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def items_count(self):
        """Количество товаров в корзине"""
        return self.items.count()


class CartItem(models.Model):
    """Товар в корзине"""
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        verbose_name='Корзина',
        related_name='items'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='Курс',
        related_name='cart_items'
    )
    quantity = models.IntegerField(default=1, verbose_name='Количество')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    
    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        unique_together = ['cart', 'course']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.course.title} в корзине {self.cart.user.username}"
    
    @property
    def total_price(self):
        """Общая стоимость по позиции"""
        return self.course.price * self.quantity