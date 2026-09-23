from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0010_ingredient_reorder_threshold'),
    ]

    operations = [
        migrations.AddField(model_name='order',name='subtotal',field=models.DecimalField(decimal_places=2,default=0.0,max_digits=10)),
        migrations.AddField(model_name='order',name='discount_amount',field=models.DecimalField(decimal_places=2,default=0.0,max_digits=10)),
        migrations.AddField(model_name='order',name='service_charge_amount',field=models.DecimalField(decimal_places=2,default=0.0,max_digits=10)),
        migrations.AddField(model_name='order',name='tax_amount',field=models.DecimalField(decimal_places=2,default=0.0,max_digits=10)),
        migrations.AddField(model_name='order',name='tip_amount',field=models.DecimalField(decimal_places=2,default=0.0,max_digits=10)),
        migrations.AddField(model_name='order',name='adjustment_note',field=models.CharField(blank=True,max_length=255)),
        migrations.AddField(model_name='payment',name='refund_reason',field=models.CharField(blank=True,max_length=255)),
        migrations.AddField(model_name='payment',name='refunded_at',field=models.DateTimeField(blank=True,null=True)),
        migrations.AddField(model_name='payment',name='refunded_by',field=models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='refunded_payments',to=settings.AUTH_USER_MODEL)),
    ]
