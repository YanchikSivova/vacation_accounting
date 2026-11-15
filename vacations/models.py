from django.db import models


class VacationType(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название типа отпуска',
    )
    deducts_vacation_days = models.BooleanField(
        default=False,
        verbose_name='Уменьшает остаток дней',
    )

    class Meta:
        db_table = 'vacation_types'
        ordering = ('pk',)
        verbose_name = 'Тип отпуска'
        verbose_name_plural = 'Типы отпуска'

    def __str__(self) -> str:
        return self.name
