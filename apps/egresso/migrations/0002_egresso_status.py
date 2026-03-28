from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('egresso', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='egresso',
            name='status',
            field=models.CharField(
                choices=[('ativo', 'Ativo'), ('inativo', 'Inativo')],
                default='ativo',
                max_length=10,
                verbose_name='Status',
            ),
        ),
    ]
