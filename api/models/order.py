from django.db import models
from django_extensions.db.models import TimeStampedModel
from djmoney.models.fields import MoneyField

class Order(TimeStampedModel):
	class STATE:
		CREATED = 0
		PREPARED = 1
		PICKUP = 2
		DELIVERED = 3
		CANCELLED = 4
		FAILED = 5

	ORDER_STATUSES = (
        (STATE.CREATED, 'Created'),
        (STATE.PREPARED, 'Prepared'),
        (STATE.PICKUP, 'Pickup'),
        (STATE.DELIVERED, 'Delivered'),
        (STATE.CANCELLED, 'Cancelled'),
        (STATE.FAILED, 'Failed'),
    )

	class PAYMENT_STATUS:
		UNPAID = 0
		PAID = 1

	PAYMENT_STATUSES = (
		(PAYMENT_STATUS.UNPAID, 'Unpaid'),
		(PAYMENT_STATUS.PAID, 'Paid'),
	)

	class PAYMENT_TYPE:
		ONLINE = 0
		COD = 1

	PAYMENT_TYPES = (
		(PAYMENT_TYPE.ONLINE, 'Online'),
		(PAYMENT_TYPE.COD, 'Cash on Delivery'),
	)

	customer = models.ForeignKey('User', related_name="orders", on_delete=models.CASCADE)
	provider = models.ForeignKey('User', related_name="deliveries", blank=True, null=True, on_delete=models.SET_NULL)
	courier = models.ForeignKey('User', related_name="packages", blank=True, null=True, on_delete=models.SET_NULL)
	status = models.IntegerField(choices=ORDER_STATUSES, default=STATE.CREATED)
	payment_status = models.SmallIntegerField(choices=PAYMENT_STATUSES, default=PAYMENT_STATUS.UNPAID)
	payment_types = models.SmallIntegerField(choices=PAYMENT_TYPES, default=PAYMENT_TYPE.ONLINE)


class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    discount_percent = models.FloatField()
    discount_price = MoneyField(max_digits=6, decimal_places=2, default_currency='USD')
    price = MoneyField(max_digits=6, decimal_places=2, default_currency='USD')

    def save(self, *args, **kwargs):
        self.price = self.product.price
        super(OrderItem, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

	
