from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import TransactionQuerySet
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ("income", "Income"),
        ("expense", "Expense"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    objects = TransactionQuerySet.as_manager()

    def __str__(self):
        return f"{self.type} of {self.amount} on {self.date} by {self.user}"

    class Meta:
        ordering = ["-date"]


class MonthlySummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()  # Storing the first day of the month
    total_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Summary for {self.user.username} - {self.month.strftime('%B %Y')}"

    @classmethod
    def update_monthly_summary(cls, user):
        today = timezone.now()
        first_day_of_current_month = today.replace(day=1)

        # Calculate monthly income, expenses, and balance for the user
        monthly_income = (
            Transaction.objects.filter(
                user=user, type="income", date__gte=first_day_of_current_month
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        monthly_expenses = (
            Transaction.objects.filter(
                user=user, type="expense", date__gte=first_day_of_current_month
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        total_balance = (
            Transaction.objects.filter(user=user).aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )

        # Update or create monthly summary
        summary, created = cls.objects.update_or_create(
            user=user,
            month=first_day_of_current_month,
            defaults={
                "total_income": monthly_income,
                "total_expenses": monthly_expenses,
                "total_balance": total_balance,
            },
        )
        return summary
