from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('core','0012_auditlog')]
    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='cost_per_unit',
            field=models.DecimalField(decimal_places=2,default=0,max_digits=10),
        ),
        migrations.CreateModel(
            name='Wastage',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('quantity',models.FloatField()),
                ('reason',models.CharField(max_length=255)),
                ('created_at',models.DateTimeField(auto_now_add=True)),
                ('ingredient',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='wastage_records',to='core.ingredient')),
                ('recorded_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
