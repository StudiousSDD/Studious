# Generated by Django 4.2.2 on 2023-08-13 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0021_merge_0016_tag_note_tag_0020_todo'),
    ]

    operations = [
        migrations.AddField(
            model_name='todo',
            name='due_date',
            field=models.DateField(null=True),
        ),
    ]
