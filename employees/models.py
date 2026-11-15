from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import F, Q


class Employee(models.Model):
    name = models.CharField(max_length=200, verbose_name='ФИО')
    vacation_days_available = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(28)],
        verbose_name='Доступно дней отпуска',
    )
    vacation_days_total = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(28)],
        verbose_name='Всего дней отпуска',
    )

    class Meta:
        db_table = 'employees'
        ordering = ('name', 'pk')
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        constraints = [
            models.CheckConstraint(
                condition=Q(
                    vacation_days_available__gte=0,
                    vacation_days_available__lte=28,
                    vacation_days_total__gte=0,
                    vacation_days_total__lte=28,
                ),
                name='employee_days_within_limit',
            ),
            models.CheckConstraint(
                condition=Q(
                    vacation_days_available__lte=F('vacation_days_total'),
                ),
                name='employee_available_days_not_over_total',
            ),
        ]

    def __str__(self) -> str:
        return self.name
