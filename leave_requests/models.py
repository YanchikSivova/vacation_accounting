from __future__ import annotations

from datetime import date

from django.db import models
from django.db.models import F, Q

from employees.models import Employee
from vacations.models import VacationType


class LeaveRequestQuerySet(models.QuerySet):
    def active(self) -> LeaveRequestQuerySet:
        return self.filter(
            status__in=(
                self.model.Status.PENDING,
                self.model.Status.APPROVED,
            ),
        )

    def cancelled(self) -> LeaveRequestQuerySet:
        return self.filter(status=self.model.Status.CANCELLED)

    def completed(self) -> LeaveRequestQuerySet:
        return self.filter(status=self.model.Status.COMPLETED)

    def for_date(self, selected_date: date) -> LeaveRequestQuerySet:
        return self.filter(
            start_date__lte=selected_date,
            end_date__gte=selected_date,
        )


class LeaveRequestManager(
    models.Manager.from_queryset(LeaveRequestQuerySet),
):
    pass


class LeaveRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает согласования'
        APPROVED = 'approved', 'Согласована'
        CANCELLED = 'cancelled', 'Отменена'
        COMPLETED = 'completed', 'Завершена'

    objects = LeaveRequestManager()
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='leave_requests',
        verbose_name='Сотрудник',
    )
    vacation = models.ForeignKey(
        VacationType,
        on_delete=models.PROTECT,
        related_name='leave_requests',
        verbose_name='Тип отпуска',
    )
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    duration = models.PositiveIntegerField(
        verbose_name='Продолжительность',
        help_text='Количество календарных дней отпуска.',
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус',
    )

    class Meta:
        db_table = 'leave_requests'
        ordering = ('start_date', 'pk')
        verbose_name = 'Заявка на отпуск'
        verbose_name_plural = 'Заявки на отпуск'
        constraints = [
            models.CheckConstraint(
                condition=Q(duration__gt=0),
                name='leave_request_duration_positive',
            ),
            models.CheckConstraint(
                condition=Q(start_date__lte=F('end_date')),
                name='leave_request_start_before_end',
            ),
            models.CheckConstraint(
                condition=Q(
                    status__in=(
                        'pending',
                        'approved',
                        'cancelled',
                        'completed',
                    ),
                ),
                name='leave_request_status_valid',
            ),
        ]

    def __str__(self) -> str:
        return f'Заявка №{self.pk}: {self.employee} — {self.vacation}'
