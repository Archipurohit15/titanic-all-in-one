from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_order_convenience_charge_order_delivery_distance_km'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='utr_number',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Awaiting payment'),
                    ('paid', 'Paid'),
                    ('shipped', 'Shipped'),
                    ('delivered', 'Delivered'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
    ]
