# Generated by Django 5.1.6 on 2025-03-23 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_is_identity_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.CharField(choices=[('English', 'English'), ('Spanish', 'Spanish')], default='English', max_length=7),
        ),
    ]
