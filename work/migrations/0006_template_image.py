# Generated by Django 3.2.13 on 2025-03-27 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0005_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='template_images/'),
        ),
    ]
