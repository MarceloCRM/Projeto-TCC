import django.db.models.deletion
from django.db import migrations, models
from django.utils import timezone


def migrar_respostas_para_respostas_pergunta(apps, schema_editor):
    RespostaPergunta = apps.get_model('formularios', 'RespostaPergunta')
    db_alias = schema_editor.connection.alias

    for resposta_pergunta in (
        RespostaPergunta.objects.using(db_alias)
        .select_related('resposta', 'resposta__resposta_formulario')
        .all()
        .iterator()
    ):
        resposta_pergunta.resposta_formulario_id = resposta_pergunta.resposta.resposta_formulario_id
        resposta_pergunta.respondido_em = resposta_pergunta.resposta.enviado_em
        resposta_pergunta.save(update_fields=['resposta_formulario', 'respondido_em'])


def remover_duplicatas_respostas_pergunta(apps, schema_editor):
    RespostaPergunta = apps.get_model('formularios', 'RespostaPergunta')
    db_alias = schema_editor.connection.alias
    chaves_vistas = set()
    ids_para_remover = []

    for resposta_pergunta in (
        RespostaPergunta.objects.using(db_alias)
        .order_by('id')
        .values('id', 'resposta_formulario_id', 'pergunta_id')
        .iterator()
    ):
        chave = (
            resposta_pergunta['resposta_formulario_id'],
            resposta_pergunta['pergunta_id'],
        )
        if chave in chaves_vistas:
            ids_para_remover.append(resposta_pergunta['id'])
        else:
            chaves_vistas.add(chave)

    if ids_para_remover:
        RespostaPergunta.objects.using(db_alias).filter(id__in=ids_para_remover).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('formularios', '0004_rename_alternativa_respostapergunta'),
    ]

    operations = [
        migrations.AddField(
            model_name='respostapergunta',
            name='resposta_formulario',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='respostas_perguntas',
                to='formularios.respostaformulario',
                verbose_name='Resposta do Formulario',
            ),
        ),
        migrations.AddField(
            model_name='respostapergunta',
            name='respondido_em',
            field=models.DateTimeField(
                null=True,
                verbose_name='Respondido em',
            ),
        ),
        migrations.RunPython(
            migrar_respostas_para_respostas_pergunta,
            migrations.RunPython.noop,
        ),
        migrations.RunPython(
            remover_duplicatas_respostas_pergunta,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='respostapergunta',
            name='resposta_formulario',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='respostas_perguntas',
                to='formularios.respostaformulario',
                verbose_name='Resposta do Formulario',
            ),
        ),
        migrations.AlterField(
            model_name='respostapergunta',
            name='respondido_em',
            field=models.DateTimeField(
                default=timezone.now,
                verbose_name='Respondido em',
            ),
        ),
        migrations.AddConstraint(
            model_name='respostapergunta',
            constraint=models.UniqueConstraint(
                fields=('resposta_formulario', 'pergunta'),
                name='uniq_resposta_por_formulario_pergunta',
            ),
        ),
        migrations.RemoveField(
            model_name='respostapergunta',
            name='resposta',
        ),
        migrations.DeleteModel(
            name='Resposta',
        ),
    ]
