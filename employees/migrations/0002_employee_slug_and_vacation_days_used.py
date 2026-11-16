from django.db import migrations, models
from django.db.models import F
from django.utils.text import slugify
from unidecode import unidecode


def populate_employee_slugs(apps, schema_editor):
    Employee = apps.get_model('employees', 'Employee')
    database = schema_editor.connection.alias

    for employee in Employee.objects.using(database).all().iterator():
        base_slug = slugify(unidecode(employee.name)) or 'employee'
        suffix = f'-{employee.pk}'
        employee.slug = f'{base_slug[:255 - len(suffix)]}{suffix}'
        employee.save(using=database, update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='slug',
            field=models.SlugField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name='URL-идентификатор',
            ),
        ),
        migrations.AddField(
            model_name='employee',
            name='vacation_days_used',
            field=models.GeneratedField(
                db_persist=True,
                expression=F('vacation_days_total')
                - F('vacation_days_available'),
                output_field=models.PositiveSmallIntegerField(),
                verbose_name='Использовано дней отпуска',
            ),
        ),
        migrations.RunPython(
            populate_employee_slugs,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='employee',
            name='slug',
            field=models.SlugField(
                max_length=255,
                unique=True,
                verbose_name='URL-идентификатор',
            ),
        ),
    ]
