from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='menu_items/'),
        ),
    ]
