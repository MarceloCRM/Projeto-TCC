import django.db.models.deletion
from django.db import migrations, models


def vincular_respostas_a_links(apps, schema_editor):
    Resposta = apps.get_model('formularios', 'Resposta')
    RespostaFormulario = apps.get_model('formularios', 'RespostaFormulario')
    db_alias = schema_editor.connection.alias

    for resposta in Resposta.objects.using(db_alias).all().iterator():
        link = (
            RespostaFormulario.objects.using(db_alias)
            .filter(
                formulario_id=resposta.formulario_id,
                egresso_id=resposta.egresso_id,
            )
            .order_by('id')
            .first()
        )

        if link is None:
            link = RespostaFormulario.objects.using(db_alias).create(
                formulario_id=resposta.formulario_id,
                egresso_id=resposta.egresso_id,
                utilizado=True,
            )
        elif not link.utilizado:
            link.utilizado = True
            link.save(update_fields=['utilizado'])

        resposta.resposta_formulario_id = link.id
        resposta.save(update_fields=['resposta_formulario'])


class Migration(migrations.Migration):

    dependencies = [
        ('formularios', '0002_formulario_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='resposta',
            name='resposta_formulario',
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='resposta',
                to='formularios.respostaformulario',
                verbose_name='Resposta do Formulario',
            ),
        ),
        migrations.RunPython(
            vincular_respostas_a_links,
            migrations.RunPython.noop,
        ),
        migrations.AlterUniqueTogether(
            name='resposta',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='resposta',
            name='egresso',
        ),
        migrations.RemoveField(
            model_name='resposta',
            name='formulario',
        ),
        migrations.AlterField(
            model_name='resposta',
            name='resposta_formulario',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='resposta',
                to='formularios.respostaformulario',
                verbose_name='Resposta do Formulario',
            ),
        ),
    ]
