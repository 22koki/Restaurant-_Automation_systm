from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0009_restauranttable_status_changed_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='reorder_threshold',
            field=models.FloatField(default=5.0),
        ),
    ]
