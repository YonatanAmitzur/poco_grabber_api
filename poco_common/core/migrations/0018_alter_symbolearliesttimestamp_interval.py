# Generated by Django 3.2 on 2021-11-21 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_alter_symbolearliesttimestamp_interval'),
    ]

    operations = [
        migrations.AlterField(
            model_name='symbolearliesttimestamp',
            name='interval',
            field=models.CharField(db_index=True, max_length=2),
        ),
    ]
