from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0008_cashier_shift'),
    ]

    operations = [
        migrations.AddField(
            model_name='restauranttable',
            name='status_changed_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
