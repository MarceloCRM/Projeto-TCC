import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.curso.models import Curso
from apps.egresso.models import Egresso
from apps.formularios.models import Formulario, FormularioEgresso, Opcao, Pergunta, Resposta


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados realistas para testes e estatísticas.'

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
            Curso.objects.create(nome='Engenharia de Computação'),
            Curso.objects.create(nome='Ciência da Computação'),
            Curso.objects.create(nome='Sistemas de Informação'),
            Curso.objects.create(nome='Análise e Desenvolvimento de Sistemas'),
        ]
        empresas = ['Google', 'Meta', 'Amazon', 'Nubank', 'Itaú', 'Inter', 'Localiza', 'Totvs', 'Freelancer', 'Nenhuma']
        nomes = [
            'Ana Silva', 'Bruno Oliveira', 'Carla Santos', 'Diego Souza', 'Eduarda Lima',
            'Fábio Pereira', 'Gabriela Costa', 'Henrique Rocha', 'Isabela Martins', 'João Ferreira',
            'Kátia Gomes', 'Lucas Almeida', 'Mariana Ribeiro', 'Natan Lopes', 'Olívia Mendes',
            'Paulo Borges', 'Quênia Cavalcanti', 'Rafael Teixeira', 'Sara Cardoso', 'Tiago Machado',
            'Úrsula Farias', 'Vítor Hugo', 'Wagner Jesus', 'Xuxa Meneghel', 'Yago Ramos', 'Zilda Arns'
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

        self.stdout.write('Criando Formulários e Perguntas...')

        f1 = Formulario.objects.create(
            titulo='Pesquisa de Satisfação de Ex-Alunos',
            descricao='Queremos saber sua opinião sobre o curso e sua trajetória profissional.',
            status=Formulario.STATUS_ATIVO,
        )

        p1_1 = Pergunta.objects.create(
            formulario=f1,
            texto='Como você avalia a qualidade do ensino do seu curso?',
            tipo=Pergunta.TIPO_ESCALA,
            ordem=1,
        )
        p1_2 = Pergunta.objects.create(
            formulario=f1,
            texto='Você está empregado atualmente? Se sim, qual sua principal área de atuação hoje?',
            tipo=Pergunta.TIPO_ESCOLHA,
            ordem=2,
        )
        Opcao.objects.create(pergunta=p1_2, texto='Desenvolvimento Web')
        Opcao.objects.create(pergunta=p1_2, texto='Data Science')
        Opcao.objects.create(pergunta=p1_2, texto='Infraestrutura/Cloud')
        Opcao.objects.create(pergunta=p1_2, texto='Gestão de Projetos')
        Opcao.objects.create(pergunta=p1_2, texto='Outro')
        Opcao.objects.create(pergunta=p1_2, texto='Atualmente não estou empregado')

        Pergunta.objects.create(
            formulario=f1,
            texto='Quanto tempo você levou para conseguir o primeiro emprego na área (em meses)?',
            tipo=Pergunta.TIPO_NUMERO,
            ordem=3,
        )
        Pergunta.objects.create(
            formulario=f1,
            texto='Deixe um comentário sobre como o curso ajudou na sua carreira.',
            tipo=Pergunta.TIPO_TEXTO,
            ordem=4,
        )

        f2 = Formulario.objects.create(
            titulo='Acompanhamento Profissional 2026',
            descricao='Atualização anual de dados dos egressos.',
            status=Formulario.STATUS_ATIVO,
        )

        p2_1 = Pergunta.objects.create(
            formulario=f2,
            texto='Você utiliza as tecnologias aprendidas no curso no seu dia a dia?',
            tipo=Pergunta.TIPO_ESCOLHA,
            ordem=1,
        )
        Opcao.objects.create(pergunta=p2_1, texto='Sim, diariamente')
        Opcao.objects.create(pergunta=p2_1, texto='Sim, ocasionalmente')
        Opcao.objects.create(pergunta=p2_1, texto='Raramente')
        Opcao.objects.create(pergunta=p2_1, texto='Não utilizo')

        Pergunta.objects.create(
            formulario=f2,
            texto='Qual seu nível de satisfação com seu cargo atual?',
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
                                'Poderia ter mais aulas práticas.',
                                'Os professores são muito bons.',
                                'Aprendi muito sobre lógica.',
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