from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lancamento',
            name='competencia',
            field=models.DateField(blank=True, help_text='Para recorrencias: primeiro dia do mes de referencia.', null=True),
        ),
        migrations.AddConstraint(
            model_name='lancamento',
            constraint=models.UniqueConstraint(
                condition=Q(item_contrato__isnull=False, competencia__isnull=False),
                fields=('item_contrato', 'competencia', 'tipo'),
                name='uniq_item_contrato_competencia_tipo',
            ),
        ),
    ]
