from django.db.models import Sum
from django.http import FileResponse

from recipes.models import AmountRecipe


def download_shopping_cart(request):
    user = request.user
    ingredients = (
        AmountRecipe.objects.filter(recipe__purchases__user=user)
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(amount=Sum('amount'))
        .order_by()
    )
    f = open("shopping_cart.txt", "w+")
    for ingredient in ingredients:
        name = ingredient['ingredient__name']
        measurement_unit = ingredient['ingredient__measurement_unit']
        amount = ingredient['amount']
        f.write(f'{name} - {amount} {measurement_unit}\n')
    f.close()
    f = open("shopping_cart.txt", "r")
    response = FileResponse(f, content_type='text/plain')
    return response
