from .models import UserBalance
def user_stock(request):
    stock = 0
    if request.user.is_authenticated:
        try:
            stock = UserBalance.objects.get(user=request.user).balance
        except Exception as e :
            print(e)
        return {'user_stock': stock}
    return {}
