import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.curso.models import Curso
from apps.egresso.models import Egresso
from apps.formularios.models import Formulario, FormularioEgresso, Opcao, Pergunta, Resposta


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados realistas para testes e estatisticas.'

    def handle(self, *args, **options):
        self.stdout.write('Limpando o banco de dados atual...')
        Resposta.objects.all().delete()
        FormularioEgresso.objects.all().delete()
        Opcao.objects.all().delete()
        Pergunta.objects.all().delete()
        Formulario.objects.all().delete()
        Egresso.objects.all().delete()
        Curso.objects.all().delete()

        self.stdout.write('Criando Egressos...')
        cursos = [
            Curso.objects.create(nome='Engenharia de Computacao'),
            Curso.objects.create(nome='Ciencia da Computacao'),
            Curso.objects.create(nome='Sistemas de Informacao'),
            Curso.objects.create(nome='Analise e Desenvolvimento de Sistemas'),
        ]
        empresas = ['Google', 'Meta', 'Amazon', 'Nubank', 'Itau', 'Inter', 'Localiza', 'Totvs', 'Freelancer', 'Nenhuma']
        nomes = [
            'Ana Silva', 'Bruno Oliveira', 'Carla Santos', 'Diego Souza', 'Eduarda Lima',
            'Fabio Pereira', 'Gabriela Costa', 'Henrique Rocha', 'Isabela Martins', 'Joao Ferreira',
            'Katia Gomes', 'Lucas Almeida', 'Mariana Ribeiro', 'Natan Lopes', 'Olivia Mendes',
            'Paulo Borges', 'Quenia Cavalcanti', 'Rafael Teixeira', 'Sara Cardoso', 'Tiago Machado',
            'Ursula Farias', 'Vitor Hugo', 'Wagner Jesus', 'Xuxa Meneghel', 'Yago Ramos', 'Zilda Arns'
        ]

        egressos = []
        for nome in nomes:
            egresso = Egresso.objects.create(
                nome_completo=nome,
                email=f'{nome.lower().replace(" ", ".")}@exemplo.com',
                whatsapp=f'119{random.randint(10000000, 99999999)}',
                curso=random.choice(cursos),
                ano_conclusao=random.randint(2018, 2024),
                status=Egresso.STATUS_ATIVO,
            )
            egressos.append(egresso)

        self.stdout.write(f'{len(egressos)} egressos criados.')

        self.stdout.write('Criando Formularios e Perguntas...')

        f1 = Formulario.objects.create(
            titulo='Pesquisa de Satisfacao de Ex-Alunos',
            descricao='Queremos saber sua opiniao sobre o curso e sua trajetoria profissional.',
            status=Formulario.STATUS_ATIVO,
        )

        p1_1 = Pergunta.objects.create(
            formulario=f1,
            texto='Como voce avalia a qualidade do ensino do seu curso?',
            tipo=Pergunta.TIPO_ESCALA,
            ordem=1,
        )
        p1_2 = Pergunta.objects.create(
            formulario=f1,
            texto='Qual sua principal area de atuacao hoje?',
            tipo=Pergunta.TIPO_ESCOLHA,
            ordem=2,
        )
        Opcao.objects.create(pergunta=p1_2, texto='Desenvolvimento Web')
        Opcao.objects.create(pergunta=p1_2, texto='Data Science')
        Opcao.objects.create(pergunta=p1_2, texto='Infraestrutura/Cloud')
        Opcao.objects.create(pergunta=p1_2, texto='Gestao de Projetos')
        Opcao.objects.create(pergunta=p1_2, texto='Outro')

        Pergunta.objects.create(
            formulario=f1,
            texto='Quanto tempo voce levou para conseguir o primeiro emprego na area (em meses)?',
            tipo=Pergunta.TIPO_NUMERO,
            ordem=3,
        )
        Pergunta.objects.create(
            formulario=f1,
            texto='Deixe um comentario sobre como o curso ajudou na sua carreira.',
            tipo=Pergunta.TIPO_TEXTO,
            ordem=4,
        )

        f2 = Formulario.objects.create(
            titulo='Acompanhamento Profissional 2026',
            descricao='Atualizacao anual de dados dos egressos.',
            status=Formulario.STATUS_ATIVO,
        )

        p2_1 = Pergunta.objects.create(
            formulario=f2,
            texto='Voce utiliza as tecnologias aprendidas no curso no seu dia a dia?',
            tipo=Pergunta.TIPO_ESCOLHA,
            ordem=1,
        )
        Opcao.objects.create(pergunta=p2_1, texto='Sim, diariamente')
        Opcao.objects.create(pergunta=p2_1, texto='Sim, ocasionalmente')
        Opcao.objects.create(pergunta=p2_1, texto='Raramente')
        Opcao.objects.create(pergunta=p2_1, texto='Nao utilizo')

        Pergunta.objects.create(
            formulario=f2,
            texto='Qual seu nivel de satisfacao com seu cargo atual?',
            tipo=Pergunta.TIPO_ESCALA,
            ordem=2,
        )
        Pergunta.objects.create(
            formulario=f2,
            texto='Qual o nome da sua empresa atual?',
            tipo=Pergunta.TIPO_TEXTO,
            ordem=3,
        )

        self.stdout.write('Criando Respostas...')

        formularios = [f1, f2]
        for formulario in formularios:
            perguntas = formulario.perguntas.all()
            for egresso in random.sample(egressos, int(len(egressos) * 0.8)):
                formulario_egresso = FormularioEgresso.objects.create(
                    formulario=formulario,
                    egresso=egresso,
                    utilizado=True,
                )
                respondido_em = timezone.now() - timedelta(days=random.randint(0, 30))

                for pergunta in perguntas:
                    valor = ''
                    if pergunta.tipo == Pergunta.TIPO_TEXTO:
                        if pergunta.texto == 'Qual o nome da sua empresa atual?':
                            valor = random.choice(empresas)
                        else:
                            valor = random.choice([
                                'O curso foi excelente!',
                                'Poderia ter mais aulas praticas.',
                                'Os professores sao muito bons.',
                                'Aprendi muito sobre logica.',
                                'Gostaria de ter visto mais tecnologias modernas.',
                            ])
                    elif pergunta.tipo == Pergunta.TIPO_NUMERO:
                        valor = str(random.randint(0, 12))
                    elif pergunta.tipo == Pergunta.TIPO_ESCALA:
                        valor = str(random.randint(1, 5))
                    elif pergunta.tipo == Pergunta.TIPO_ESCOLHA:
                        opcoes = list(pergunta.opcoes.all())
                        if opcoes:
                            valor = random.choice(opcoes).texto

                    Resposta.objects.create(
                        formulario_egresso=formulario_egresso,
                        pergunta=pergunta,
                        valor=valor,
                        respondido_em=respondido_em,
                    )

        self.stdout.write(self.style.SUCCESS('Banco de dados populado com sucesso!'))
