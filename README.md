# Trabalho Prático de Engenharia de Software

## Membros e papéis
- Beatriz Camilly Gulart Pereira: fullstack
- Maria Eduarda Nunes e Carvalho de Vasconcelos Costa: fullstack
- Isabela Fernandes Guerra de Morais: fullstack
- Alessandro Mesa Teppa: fullstack

## Objetivo do sistema
O objetivo do sistema é criar um calendário que permita a organização de atividades acadêmicas, profissionais e pessoais. Para isso, ele possibilitará a criação de grupos (como turmas, equipes ou outros), com diferentes níveis de permissão entre administradores e participantes. O sistema oferecerá gerenciamento de eventos (aulas, reuniões, tarefas, provas, etc.), bem como acompanhamento de progresso, priorização de atividades e organização visual por cores, o que facilitará a identificação e o planejamento das atividades ao longo do tempo.

## Tecnologias
- Linguagem: python
- Framework: django
- Banco de dados: sqlite
- Agentes de IA:

## Histórias de usuário
1. Como usuário do sistema, eu gostaria de me cadastrar/editar/visualizar/deletar meu usuário no sistema como professor ou aluno
2. Como professor, eu gostaria de cadastrar/editar/visualizar/deletar uma turma, com o nome da matéria, os dias da semana, o horário, o tipo (obrigatória, optativa, formação livre) e seus eventos (aulas, provas e trabalhos)
3. Como professor, eu gostaria de cadastrar/editar/visualizar/deletar aulas com: material da aula (link ou arquivo), dia da aula e horário
4. Como professor, eu gostaria de cadastrar/editar/visualizar/deletar trabalhos com: especificação, quantidade de pessoas, quantidade de pontos e dia e horário de entrega
5. Como professor, eu gostaria de cadastrar/editar/visualizar/deletar provas com: quantidade de pontos, matéria, dia e horário
6. Como professor, eu gostaria de cadastrar/visualizar/deletar alunos em uma turma
7. Como aluno, eu gostaria de visualizar minhas turmas e seus eventos
8. Como aluno, eu gostaria de dar check em trabalhos e provas já realizados/estudados
9. Como aluno, eu gostaria de filtrar meus eventos de acordo com: a turma, se é aula/trabalho/prova, e se tem check ou não
