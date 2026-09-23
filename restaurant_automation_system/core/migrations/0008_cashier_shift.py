from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0007_merge_20260921_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashierShift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opening_float', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('counted_cash', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('expected_cash', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('variance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed')], default='open', max_length=10)),
                ('opened_at', models.DateTimeField(auto_now_add=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('cashier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cashier_shifts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='payment',
            name='processed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_payments', to=settings.AUTH_USER_MODEL),
        ),
    ]
