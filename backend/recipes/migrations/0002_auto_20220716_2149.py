# Generated by Django 3.2.14 on 2022-07-16 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='amountrecipe',
            options={'ordering': ['-pk'], 'verbose_name': 'Количество ингридиента', 'verbose_name_plural': 'Количество ингредиентов'},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='media/', verbose_name='Фотография'),
        ),
        migrations.AddConstraint(
            model_name='amountrecipe',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_amount_recipe'),
        ),
    ]
