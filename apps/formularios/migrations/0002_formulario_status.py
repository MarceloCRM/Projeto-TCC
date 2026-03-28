from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formularios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='formulario',
            name='status',
            field=models.CharField(
                choices=[('ativo', 'Ativo'), ('inativo', 'Inativo')],
                default='ativo',
                max_length=10,
            ),
        ),
    ]
