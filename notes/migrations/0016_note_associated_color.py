# Generated by Django 4.2.2 on 2023-08-09 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0015_rename_event_lecture_cls_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='associated_color',
            field=models.CharField(default='true', max_length=255),
            preserve_default=False,
        ),
    ]
