from django.core.validators import MaxValueValidator
from django.db import models, transaction
from django.db.models import F, Q
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode


class Employee(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='ФИО',
        help_text='Укажите фамилию, имя и отчество сотрудника.',
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        editable=False,
        verbose_name='URL-идентификатор',
    )
    vacation_days_available = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(28)],
        verbose_name='Доступно дней отпуска',
        help_text='Остаток оплачиваемых дней отпуска (от 0 до 28).',
    )
    vacation_days_total = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(28)],
        verbose_name='Всего дней отпуска',
        help_text='Общий лимит оплачиваемых дней за год (от 0 до 28).',
    )
    vacation_days_used = models.GeneratedField(
        expression=F('vacation_days_total') - F('vacation_days_available'),
        output_field=models.PositiveSmallIntegerField(),
        db_persist=True,
        verbose_name='Использовано дней отпуска',
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

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base_slug = slugify(unidecode(self.name)) or 'employee'
            if self.pk is None:
                using = kwargs.get('using')
                with transaction.atomic(using=using):
                    super().save(*args, **kwargs)
                    self.slug = self._slug_for(base_slug)
                    super().save(
                        update_fields=['slug'],
                        using=using,
                    )
                return

            self.slug = self._slug_for(base_slug)
            update_fields = kwargs.get('update_fields')
            if update_fields is not None:
                kwargs['update_fields'] = set(update_fields) | {'slug'}

        super().save(*args, **kwargs)

    def _slug_for(self, base_slug: str) -> str:
        suffix = f'-{self.pk}'
        return f'{base_slug[:255 - len(suffix)]}{suffix}'

    def get_absolute_url(self) -> str:
        return reverse('employees:slug_detail', kwargs={'slug': self.slug})

    def __str__(self) -> str:
        return self.name
