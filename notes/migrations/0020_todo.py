# Generated by Django 4.2.2 on 2023-08-10 20:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0019_lecture_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToDo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('completed', models.BooleanField()),
                ('cls', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='notes.class')),
            ],
        ),
    ]
