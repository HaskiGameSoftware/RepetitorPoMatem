# admin.py
from django.contrib import admin
from .models import Course, CourseOrder, UserCourse, Review, Cart, CartItem

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'duration', 'max_students', 'students_count', 'available_slots', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'price', 'max_students']
    actions = ['activate_courses', 'deactivate_courses']
    
    @admin.display(description='Кол-во студентов')
    def students_count(self, obj):
        return obj.get_students_count()
    
    @admin.display(description='Свободных мест')
    def available_slots(self, obj):
        return obj.available_slots
    
    @admin.action(description='Активировать выбранные курсы')
    def activate_courses(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} курсов активировано.')
    
    @admin.action(description='Деактивировать выбранные курсы')
    def deactivate_courses(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} курсов деактивировано.')

@admin.register(CourseOrder)
class CourseOrderAdmin(admin.ModelAdmin):
    list_display = ['course_title', 'student_name', 'email', 'price', 'order_date', 'is_completed']
    list_filter = ['order_date', 'is_completed']
    search_fields = ['student_name', 'email', 'course_title']
    list_editable = ['is_completed']
    actions = ['mark_as_completed', 'mark_as_active']

    @admin.action(description='Отметить как завершенные')
    def mark_as_completed(self, request, queryset):
        queryset.update(is_completed=True)

    @admin.action(description='Отметить как активные')
    def mark_as_active(self, request, queryset):
        queryset.update(is_completed=False)

@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ['user', 'course_title', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['user__username', 'course_title']
    list_editable = ['status']
    actions = ['mark_as_completed', 'mark_as_active', 'mark_as_cancelled']
    
    @admin.action(description='Отметить как завершенные')
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='completed', end_date=timezone.now().date())
    
    @admin.action(description='Отметить как активные')
    def mark_as_active(self, request, queryset):
        queryset.update(status='active', end_date=None)
    
    @admin.action(description='Отметить как отмененные')
    def mark_as_cancelled(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='cancelled', end_date=timezone.now().date())

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_name', 'course', 'rating_overall', 'is_approved', 'timestamp']
    list_filter = ['is_approved', 'timestamp', 'rating_overall']
    search_fields = ['student_name', 'text', 'user__username']
    list_editable = ['is_approved']
    actions = ['approve_reviews', 'disapprove_reviews']
    
    @admin.action(description='Одобрить выбранные отзывы')
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} отзывов одобрено.')
    
    @admin.action(description='Снять одобрение с выбранных отзывов')
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'{queryset.count()} отзывов снято с публикации.')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'items_count', 'total_price', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    @admin.display(description='Кол-во товаров')
    def items_count(self, obj):
        return obj.items_count
    
    @admin.display(description='Общая сумма')
    def total_price(self, obj):
        return f"{obj.total_price} ₽"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'course', 'quantity', 'total_price', 'added_at']
    list_filter = ['added_at']
    search_fields = ['cart__user__username', 'course__title']
    list_editable = ['quantity']
    
    @admin.display(description='Сумма')
    def total_price(self, obj):
        return f"{obj.total_price} ₽"