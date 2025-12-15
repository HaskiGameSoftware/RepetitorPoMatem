from .models import Cart

def cart_context(request):
    """Добавляет корзину в контекст всех шаблонов"""
    cart = None
    print("OK!")
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
        except Cart.DoesNotExist:
            cart = None
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, is_active=True)
            except Cart.DoesNotExist:
                cart = None
    
    return {'cart': cart}