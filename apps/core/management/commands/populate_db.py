import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

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

        self.stdout.write('Criando Egressos...')
        cursos = ['Engenharia de Computação', 'Ciência da Computação', 'Sistemas de Informação', 'Análise e Desenvolvimento de Sistemas']
        empresas = ['Google', 'Meta', 'Amazon', 'Nubank', 'Itaú', 'Inter', 'Localiza', 'Totvs', 'Freelancer', 'Nenhuma']
        nomes = [
            'Ana Silva', 'Bruno Oliveira', 'Carla Santos', 'Diego Souza', 'Eduarda Lima',
            'Fábio Pereira', 'Gabriela Costa', 'Henrique Rocha', 'Isabela Martins', 'João Ferreira',
            'Katia Gomes', 'Lucas Almeida', 'Mariana Ribeiro', 'Natan Lopes', 'Olívia Mendes',
            'Paulo Borges', 'Quênia Cavalcanti', 'Rafael Teixeira', 'Sara Cardoso', 'Tiago Machado',
            'Ursula Farias', 'Vitor Hugo', 'Wagner Jesus', 'Xuxa Meneghel', 'Yago Ramos', 'Zilda Arns'
        ]

        egressos = []
        for i, nome in enumerate(nomes):
            egresso = Egresso.objects.create(
                nome_completo=nome,
                email=f'{nome.lower().replace(" ", ".")}@exemplo.com',
                whatsapp=f'119{random.randint(10000000, 99999999)}',
                curso=random.choice(cursos),
                ano_conclusao=random.randint(2018, 2024),
                situacao_profissional=random.choice([c[0] for c in Egresso.SITUACAO_PROFISSIONAL]),
                empresa_atual=random.choice(empresas) if random.random() > 0.3 else '',
                faixa_salarial=random.choice([c[0] for c in Egresso.FAIXA_SALARIAL]),
                status=Egresso.STATUS_ATIVO
            )
            egressos.append(egresso)

        self.stdout.write(f'{len(egressos)} egressos criados.')

        self.stdout.write('Criando Formulários e Perguntas...')
        
        # Formulário 1: Satisfação do Curso
        f1 = Formulario.objects.create(
            titulo='Pesquisa de Satisfação de Ex-Alunos',
            descricao='Queremos saber sua opinião sobre o curso e sua trajetória profissional.',
            status=Formulario.STATUS_ATIVO
        )
        
        p1_1 = Pergunta.objects.create(formulario=f1, texto='Como você avalia a qualidade do ensino do seu curso?', tipo=Pergunta.TIPO_ESCALA, ordem=1)
        p1_2 = Pergunta.objects.create(formulario=f1, texto='Qual sua principal área de atuação hoje?', tipo=Pergunta.TIPO_ESCOLHA, ordem=2)
        Opcao.objects.create(pergunta=p1_2, texto='Desenvolvimento Web')
        Opcao.objects.create(pergunta=p1_2, texto='Data Science')
        Opcao.objects.create(pergunta=p1_2, texto='Infraestrutura/Cloud')
        Opcao.objects.create(pergunta=p1_2, texto='Gestão de Projetos')
        Opcao.objects.create(pergunta=p1_2, texto='Outro')
        
        p1_3 = Pergunta.objects.create(formulario=f1, texto='Quanto tempo você levou para conseguir o primeiro emprego na área (em meses)?', tipo=Pergunta.TIPO_NUMERO, ordem=3)
        p1_4 = Pergunta.objects.create(formulario=f1, texto='Deixe um comentário sobre como o curso ajudou na sua carreira.', tipo=Pergunta.TIPO_TEXTO, ordem=4)

        # Formulário 2: Perfil Profissional 2026
        f2 = Formulario.objects.create(
            titulo='Acompanhamento Profissional 2026',
            descricao='Atualização anual de dados dos egressos.',
            status=Formulario.STATUS_ATIVO
        )
        
        p2_1 = Pergunta.objects.create(formulario=f2, texto='Você utiliza as tecnologias aprendidas no curso no seu dia a dia?', tipo=Pergunta.TIPO_ESCOLHA, ordem=1)
        Opcao.objects.create(pergunta=p2_1, texto='Sim, diariamente')
        Opcao.objects.create(pergunta=p2_1, texto='Sim, ocasionalmente')
        Opcao.objects.create(pergunta=p2_1, texto='Raramente')
        Opcao.objects.create(pergunta=p2_1, texto='Não utilizo')

        p2_2 = Pergunta.objects.create(formulario=f2, texto='Qual seu nível de satisfação com seu cargo atual?', tipo=Pergunta.TIPO_ESCALA, ordem=2)
        p2_3 = Pergunta.objects.create(formulario=f2, texto='Qual o nome da sua empresa atual?', tipo=Pergunta.TIPO_TEXTO, ordem=3)

        self.stdout.write('Criando Respostas...')
        
        formularios = [f1, f2]
        for f in formularios:
            perguntas = f.perguntas.all()
            # Fazer 80% dos egressos responderem cada formulário
            for egresso in random.sample(egressos, int(len(egressos) * 0.8)):
                formulario_egresso = FormularioEgresso.objects.create(
                    formulario=f,
                    egresso=egresso,
                    utilizado=True
                )
                respondido_em = timezone.now() - timedelta(days=random.randint(0, 30))

                for p in perguntas:
                    valor = ""
                    if p.tipo == Pergunta.TIPO_TEXTO:
                        if p.texto == 'Qual o nome da sua empresa atual?':
                            valor = egresso.empresa_atual or "Nenhuma"
                        else:
                            valor = random.choice(['O curso foi excelente!', 'Poderia ter mais aulas práticas.', 'Os professores são muito bons.', 'Aprendi muito sobre lógica.', 'Gostaria de ter visto mais tecnologias modernas.'])
                    elif p.tipo == Pergunta.TIPO_NUMERO:
                        valor = str(random.randint(0, 12))
                    elif p.tipo == Pergunta.TIPO_ESCALA:
                        valor = str(random.randint(1, 5))
                    elif p.tipo == Pergunta.TIPO_ESCOLHA:
                        opcoes = list(p.opcoes.all())
                        if opcoes:
                            valor = random.choice(opcoes).texto
                    
                    Resposta.objects.create(
                        formulario_egresso=formulario_egresso,
                        pergunta=p,
                        valor=valor,
                        respondido_em=respondido_em
                    )

        self.stdout.write(self.style.SUCCESS('Banco de dados populado com sucesso!'))
