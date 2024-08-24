from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        Tag.objects.all().delete()
        data = [
            {'name': 'Завтрак', 'slug': 'breakfast'},
            {'name': 'Обед', 'slug': 'lunch'},
            {'name': 'Ужин', 'slug': 'dinner'},
            {'name': 'Праздник', 'slug': 'holiday'},
            {'name': 'Быстро', 'slug': 'fast'}
        ]
        for tag in data:
            Tag.objects.create(name=tag['name'], slug=tag['slug'])
        self.stdout.write(self.style.SUCCESS('Теги добавлены'))
