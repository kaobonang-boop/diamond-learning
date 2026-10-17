from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syllabus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='is_core',
            field=models.BooleanField(default=True, help_text='Compulsory for every student at this level. Untick for optional/elective subjects that students choose for themselves when they sign up.'),
        ),
    ]
