# Generated by Django 5.1.3 on 2024-12-01 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyApp', '0003_project_projectmember'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='due_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
