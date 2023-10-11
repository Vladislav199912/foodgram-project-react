from django.shortcuts import HttpResponse


def send_message(ingredient_lst):
    shopping_list = ['Список покупок:']
    for ingredient in ingredient_lst:
        shopping_list.append('{} ({}) - {}'.format(*ingredient))

    response = HttpResponse('\n'.join(shopping_list),
                            content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.txt"'
    )
    return response
