# Generated by Django 4.2.1 on 2023-08-13 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Reciepts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reciept', models.ImageField(null=True, upload_to='department_reciepts')),
                ('time', models.DateField(auto_now=True)),
            ],
        ),
    ]