# Generated for the Phase 2 restaurant workflow.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='category',
            field=models.CharField(default='Mains', max_length=80),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='image_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='prep_station',
            field=models.CharField(
                choices=[
                    ('kitchen', 'Kitchen'),
                    ('grill', 'Grill'),
                    ('bar', 'Bar'),
                    ('dessert', 'Dessert'),
                ],
                default='kitchen',
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name='RestaurantTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=20, unique=True)),
                ('seats', models.PositiveIntegerField(default=2)),
                ('area', models.CharField(blank=True, max_length=80)),
                ('status', models.CharField(
                    choices=[
                        ('available', 'Available'),
                        ('reserved', 'Reserved'),
                        ('occupied', 'Occupied'),
                        ('ordering', 'Ordering'),
                        ('preparing', 'Preparing'),
                        ('ready_to_bill', 'Ready to bill'),
                        ('cleaning', 'Cleaning'),
                    ],
                    default='available',
                    max_length=20,
                )),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='customer_name',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='order',
            name='customer_phone',
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name='order',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='order_type',
            field=models.CharField(
                choices=[
                    ('dine_in', 'Dine in'),
                    ('takeaway', 'Takeaway'),
                    ('delivery', 'Delivery'),
                    ('online', 'Online'),
                ],
                default='dine_in',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('confirmed', 'Confirmed'),
                    ('preparing', 'Preparing'),
                    ('ready', 'Ready'),
                    ('served', 'Served'),
                    ('awaiting_payment', 'Awaiting payment'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                ],
                default='confirmed',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='order',
            name='table',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='orders',
                to='core.restauranttable',
            ),
        ),
        migrations.AlterField(
            model_name='order',
            name='salesclerk',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='auth.user',
            ),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='notes',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='status',
            field=models.CharField(
                choices=[
                    ('queued', 'Queued'),
                    ('preparing', 'Preparing'),
                    ('ready', 'Ready'),
                    ('served', 'Served'),
                    ('cancelled', 'Cancelled'),
                ],
                default='queued',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='menu_item',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to='core.menuitem',
            ),
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=120)),
                ('phone', models.CharField(max_length=40)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('party_size', models.PositiveIntegerField()),
                ('reservation_at', models.DateTimeField()),
                ('notes', models.TextField(blank=True)),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('confirmed', 'Confirmed'),
                        ('seated', 'Seated'),
                        ('completed', 'Completed'),
                        ('cancelled', 'Cancelled'),
                        ('no_show', 'No show'),
                    ],
                    default='pending',
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('table', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='reservations',
                    to='core.restauranttable',
                )),
            ],
        ),
    ]
