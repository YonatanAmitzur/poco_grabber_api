# Generated by Django 3.2 on 2021-11-21 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20211121_0917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='symbolearliesttimestamp',
            name='interval',
            field=models.CharField(db_index=True, max_length=2),
        ),
    ]
