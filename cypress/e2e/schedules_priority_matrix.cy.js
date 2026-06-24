describe('Fluxo da Matriz de Prioridade', () => {
  const username = 'admin_matriz';
  const password = 'admin123_password';

  before(() => {
    const managePyPath = `${Cypress.config('projectRoot')}/tp_es/manage.py`;
    cy.exec(
      `python "${managePyPath}" shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user, _ = User.objects.get_or_create(username='${username}'); user.set_password('${password}'); user.save()"`
    );
  });

  beforeEach(() => {
    cy.login(username, password);
  });

  it('CT01: Deve exibir a tarefa criada no quadrante correto da matriz de prioridades', () => {
    const agendaNome = `AgendaMatriz-${Date.now()}`;
    const tarefaNome = `TarefaUrgente-${Date.now()}`;
    
    // 1. Cria uma nova agenda pela UI
    cy.criarAgendaUI(agendaNome);

    // 2. Visita a página principal e abre o modal de criação de atividade
    cy.visit('/schedules/main_calendar_view/');
    cy.switchTab('tab-tarefas');
    cy.get('[data-cy="btn-novo"]').click();

    // 3. Preenche o formulário definindo a prioridade como "Urgente e importante"
    cy.get('[data-cy="form-nova-atividade"]').should('be.visible').within(() => {
      cy.get('[data-cy="select-agenda"]').select(agendaNome);
      cy.get('[data-cy="input-titulo-atividade"]').type(tarefaNome);
      cy.get('[data-cy="select-tipo"]').select('task');
      cy.get('[data-cy="select-categoria"]').select('exam');
      cy.get('#priority-select').select('urgent_important');
      cy.get('[data-cy="input-date"]').type('2026-06-30');
      cy.get('[data-cy="btn-salvar-atividade"]').click();
    });

    // 4. Aguarda confirmação
    cy.contains('Atividade criada com sucesso.').should('be.visible');

    // 5. Visita a aba "Matriz"
    cy.visit('/schedules/main_calendar_view/');
    cy.switchTab('tab-matriz');

    // 6. Verifica se a tarefa está presente no quadrante "Urgente e importante"
    cy.get('[data-cy="quadrante-matriz-urgent_important"]')
      .should('be.visible')
      .contains(tarefaNome)
      .should('be.visible');

    // 7. Verifica que a tarefa não está nos outros quadrantes
    cy.get('[data-cy="quadrante-matriz-urgent"]')
      .contains(tarefaNome)
      .should('not.exist');
    cy.get('[data-cy="quadrante-matriz-important"]')
      .contains(tarefaNome)
      .should('not.exist');
    cy.get('[data-cy="quadrante-matriz-not_urgent_not_important"]')
      .contains(tarefaNome)
      .should('not.exist');
  });
});
