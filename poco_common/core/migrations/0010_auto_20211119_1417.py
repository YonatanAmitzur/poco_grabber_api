# Generated by Django 3.2 on 2021-11-19 14:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import poco_common.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_grabbersettingsrecords'),
    ]

    operations = [
        migrations.AddField(
            model_name='grabbersettingsrecords',
            name='slug_record',
            field=models.CharField(default=poco_common.core.models.make_slug, max_length=32),
        ),
        migrations.AlterField(
            model_name='grabbersettingsrecords',
            name='inserted_by_user',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='grabber_settings_record_inserted_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='grabbersettingsrecords',
            name='is_running',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='grabbersettingsrecords',
            name='slug',
            field=models.CharField(default=None, max_length=32),
        ),
    ]
