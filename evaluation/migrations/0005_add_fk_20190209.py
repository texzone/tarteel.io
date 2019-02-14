from django.db import migrations, models
import django.db.models.deletion


"""This migration converts recording_id from a
CharField to a ForeignKey named associated_recording
"""
class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0017_auto_20190101_1134'),
        ('evaluation', '0004_merge_20181223_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluation',
            name='recording_id',
            field=models.CharField(db_column="recording_id", max_length=32)
        ),
        migrations.RenameField(
            model_name='evaluation',
            old_name='recording_id',
            new_name='associated_recording'
        ),
        migrations.AlterField(
            model_name='evaluation',
            name='associated_recording',
            field=models.ForeignKey(to='restapi.AnnotatedRecording', on_delete=models.CASCADE, null=True)
        ),
    ]
