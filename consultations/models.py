from django.db import models

class LossReport(models.Model):
    name = models.CharField("Імя", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email")
    loss_amount = models.DecimalField("Сума потери", max_digits=10, decimal_places=2)
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.loss_amount} грн"
