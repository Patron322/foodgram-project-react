from django.db.models import Sum
from django.http.response import HttpResponse
from rest_framework import permissions
from rest_framework.decorators import action
from recipe.models import RecipeIngredient
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


@action(detail=False, methods=['get'],
        permission_classes=[permissions.IsAuthenticated])
def download_shopping_cart(self, request):
    user = request.user
    ingredients = RecipeIngredient.objects.filter(
        recipe_id__cart_recipe__user=user).values_list(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(Sum('amount'))

    shopping_list = []
    for ingredient in ingredients:
        shopping_list.append(
            f'{ingredient[0].capitalize()} '
            f'({ingredient[1]}) - {ingredient[2]}'
        )

    pdfmetrics.registerFont(
        TTFont('DejaVuSans', 'DejaVuSans.ttf', 'UTF-8'))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = ('attachment; '
                                       'filename="shopping_list.pdf"')
    page = canvas.Canvas(response)
    page.setFont('DejaVuSans', size=24)
    page.drawString(200, 800, 'Список покупок')
    page.setFont('DejaVuSans', size=16)
    height = 750
    for item in shopping_list:
        page.drawString(75, height, item)
        height -= 25
    page.showPage()
    page.save()

    return response
