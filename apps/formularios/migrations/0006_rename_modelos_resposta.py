import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formularios', '0005_respostapergunta_direta'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RespostaFormulario',
            new_name='FormularioEgresso',
        ),
        migrations.RenameModel(
            old_name='RespostaPergunta',
            new_name='Resposta',
        ),
        migrations.RemoveConstraint(
            model_name='resposta',
            name='uniq_resposta_por_formulario_pergunta',
        ),
        migrations.RenameField(
            model_name='resposta',
            old_name='resposta_formulario',
            new_name='formulario_egresso',
        ),
        migrations.AlterModelOptions(
            name='resposta',
            options={
                'verbose_name': 'Resposta',
                'verbose_name_plural': 'Respostas',
            },
        ),
        migrations.AlterField(
            model_name='resposta',
            name='formulario_egresso',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='respostas',
                to='formularios.formularioegresso',
                verbose_name='Formulario do Egresso',
            ),
        ),
        migrations.AddConstraint(
            model_name='resposta',
            constraint=models.UniqueConstraint(
                fields=('formulario_egresso', 'pergunta'),
                name='uniq_resposta_por_formulario_egresso_pergunta',
            ),
        ),
    ]
