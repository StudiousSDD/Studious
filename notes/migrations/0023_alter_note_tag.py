# Generated by Django 4.2.2 on 2023-08-14 03:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0022_todo_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='tag',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='notes.tag'),
        ),
    ]