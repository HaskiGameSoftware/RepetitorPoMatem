from django.shortcuts import render, redirect
from .forms import FeedbackForm

def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Получаем очищенные данные
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            # Выводим данные в консоль
            print("=" * 50)
            print("НОВАЯ ФОРМА ОБРАТНОЙ СВЯЗИ")
            print(f"ФИО: {name}")
            print(f"Email: {email}")
            print(f"Сообщение: {message}")
            print("=" * 50)
            
            # Перенаправляем на страницу успеха
            return redirect('feedback:feedback_success')
    else:
        form = FeedbackForm()
    
    # Передаем список запрещенных слов в контекст для JavaScript
    context = {
        'form': form,
        'bad_words_json': str(form.BAD_WORDS)  # Для передачи в JavaScript
    }
    
    return render(request, 'feedback/feedback.html', context)

def feedback_success(request):
    return render(request, 'feedback/success.html')