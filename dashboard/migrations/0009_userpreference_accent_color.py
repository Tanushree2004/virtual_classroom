# Generated by Django 5.1.5 on 2025-04-05 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_userpreference'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpreference',
            name='accent_color',
            field=models.CharField(choices=[('blue', 'Blue'), ('green', 'Green'), ('purple', 'Purple'), ('pink', 'Pink'), ('red', 'Red')], default='blue', max_length=10),
        ),
    ]
