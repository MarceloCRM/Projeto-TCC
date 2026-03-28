from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('formularios', '0003_resposta_por_respostaformulario'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Alternativa',
            new_name='RespostaPergunta',
        ),
        migrations.AlterModelOptions(
            name='respostapergunta',
            options={
                'verbose_name': 'Resposta da Pergunta',
                'verbose_name_plural': 'Respostas das Perguntas',
            },
        ),
    ]
