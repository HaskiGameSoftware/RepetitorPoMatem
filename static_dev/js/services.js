// JavaScript для управления услугами
document.addEventListener('DOMContentLoaded', function() {
    initializeServices();
});

function initializeServices() {
    const serviceButtons = document.querySelectorAll('.service-btn');
    let activeService = null;
    
    // Добавляем обработчики событий для каждой кнопки
    serviceButtons.forEach(button => {
        button.addEventListener('click', function() {
            const serviceIndex = this.getAttribute('data-service-index');
            const targetId = this.getAttribute('data-bs-target').substring(1);
            
            handleServiceClick(this, serviceIndex, targetId);
        });
        
        // Обработчики событий для collapse
        const targetId = button.getAttribute('data-bs-target').substring(1);
        const targetElement = document.getElementById(targetId);
        
        if (targetElement) {
            targetElement.addEventListener('show.bs.collapse', function() {
                console.log('Открыта услуга:', button.textContent.trim());
                trackServiceView(button.getAttribute('data-service-index'));
            });
            
            targetElement.addEventListener('hide.bs.collapse', function() {
                resetButtonStyle(button);
            });
            
            targetElement.addEventListener('shown.bs.collapse', function() {
                scrollToServiceDetail(targetId);
            });
        }
    });
    
    // Автоматически открываем первую услугу при загрузке страницы
    if (serviceButtons.length > 0) {
        openFirstService(serviceButtons[0]);
    }
    
    // Добавляем глобальные обработчики клавиатуры
    document.addEventListener('keydown', function(e) {
        handleKeyboardNavigation(e, serviceButtons);
    });
}

function handleServiceClick(button, serviceIndex, targetId) {
    // Убираем активный класс у всех кнопок
    document.querySelectorAll('.service-btn').forEach(btn => {
        btn.classList.remove('btn-primary', 'active');
        btn.classList.add('btn-outline-primary');
    });
    
    // Добавляем активный класс к текущей кнопке
    button.classList.remove('btn-outline-primary');
    button.classList.add('btn-primary', 'active');
    
    // Закрываем все другие открытые детали
    closeOtherServiceDetails(targetId);
}

function closeOtherServiceDetails(currentTargetId) {
    const allDetails = document.querySelectorAll('.service-detail');
    allDetails.forEach(detail => {
        if (detail.id !== currentTargetId && detail.classList.contains('show')) {
            const bsCollapse = bootstrap.Collapse.getInstance(detail);
            if (bsCollapse) {
                bsCollapse.hide();
            }
        }
    });
}

function resetButtonStyle(button) {
    button.classList.remove('btn-primary', 'active');
    button.classList.add('btn-outline-primary');
}

function openFirstService(firstButton) {
    const firstTargetId = firstButton.getAttribute('data-bs-target').substring(1);
    const firstDetail = document.getElementById(firstTargetId);
    
    if (firstDetail) {
        const bsCollapse = new bootstrap.Collapse(firstDetail, {
            toggle: true
        });
        firstButton.classList.remove('btn-outline-primary');
        firstButton.classList.add('btn-primary', 'active');
    }
}

function scrollToServiceDetail(targetId) {
    const element = document.getElementById(targetId);
    if (element) {
        const offsetTop = element.offsetTop - 100;
        window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
        });
    }
}

function trackServiceView(serviceIndex) {
    // Здесь можно добавить логику для отслеживания просмотров услуг
    console.log(`Просмотр услуги с индексом: ${serviceIndex}`);
    
    // Пример: отправка данных в аналитику
    // if (typeof gtag !== 'undefined') {
    //     gtag('event', 'service_view', {
    //         'service_index': serviceIndex
    //     });
    // }
}

function handleKeyboardNavigation(e, serviceButtons) {
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
        e.preventDefault();
        
        const activeButton = document.querySelector('.service-btn.active');
        if (!activeButton) return;
        
        const currentIndex = parseInt(activeButton.getAttribute('data-service-index'));
        let newIndex;
        
        if (e.key === 'ArrowRight') {
            newIndex = (currentIndex + 1) % serviceButtons.length;
        } else {
            newIndex = (currentIndex - 1 + serviceButtons.length) % serviceButtons.length;
        }
        
        const newButton = serviceButtons[newIndex];
        if (newButton) {
            newButton.click();
        }
    }
}

// Функция для программного открытия услуги по индексу
function openServiceByIndex(index) {
    const button = document.querySelector(`[data-service-index="${index}"]`);
    if (button) {
        button.click();
    }
}

// Функция для получения текущей активной услуги
function getActiveService() {
    const activeButton = document.querySelector('.service-btn.active');
    return activeButton ? parseInt(activeButton.getAttribute('data-service-index')) : null;
}

// Экспортируем функции для глобального использования
window.ServicesManager = {
    openServiceByIndex,
    getActiveService,
    initializeServices
};