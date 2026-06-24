describe('Testes E2E - Domínio de Atividades', () => {
  const username = 'admin_atividades';
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

  it('CT01: Deve adicionar um novo Evento', () => {
    const agendaNome = `AgendaEvento-${Date.now()}`;
    const eventoNome = `Evento-${Date.now()}`;
    
    cy.criarAgendaUI(agendaNome);

    cy.visit('/schedules/main_calendar_view/');
    
    cy.switchTab('tab-eventos');
    cy.get('[data-cy="btn-novo"]').click();

    cy.get('[data-cy="form-nova-atividade"]').should('be.visible').within(() => {
      cy.get('[data-cy="select-agenda"]').select(agendaNome);
      cy.get('[data-cy="input-titulo-atividade"]').type(eventoNome);
      cy.get('[data-cy="select-tipo"]').select('event');
      cy.get('[data-cy="select-categoria"]').select('study');
      cy.get('[data-cy="input-date"]').type('2026-06-30');
      cy.get('[data-cy="btn-salvar-atividade"]').click();
    });

    cy.contains('Atividade criada com sucesso.').should('be.visible');
    cy.reload();
    cy.get('#eventos').contains(eventoNome).should('be.visible');
  });

  it('CT02: Não deve criar evento sem data (Validação Django)', () => {
    const agendaNome = `AgendaSemData-${Date.now()}`;
    const eventoNome = `EventoSemData-${Date.now()}`;
    cy.criarAgendaUI(agendaNome);

    cy.visit('/schedules/main_calendar_view/?tab=eventos');
    cy.get('[data-cy="btn-novo"]').click();

    cy.get('[data-cy="form-nova-atividade"]').invoke('attr', 'novalidate', 'novalidate');
    
    cy.get('[data-cy="form-nova-atividade"]').should('be.visible').within(() => {
      cy.get('[data-cy="select-agenda"]').select(agendaNome);
      cy.get('[data-cy="input-titulo-atividade"]').type(eventoNome);
      cy.get('[data-cy="select-tipo"]').select('event');
      cy.get('[data-cy="btn-salvar-atividade"]').click();
    });

    cy.contains('Eventos precisam de uma data.').should('be.visible');
  });

  it('CT03: Deve marcar uma tarefa pendente como concluída', () => {
    const agendaNome = `AgendaTask-${Date.now()}`;
    const tarefaNome = `Tarefa-${Date.now()}`;
    cy.criarAgendaUI(agendaNome);
    cy.criarAtividadeUI(agendaNome, tarefaNome, 'task', 'assignment');

    cy.visit('/schedules/main_calendar_view/');
    
    // Usa switchTab para garantir que a aba de tarefas está carregada
    cy.switchTab('tab-tarefas');

    cy.get('[data-cy="subtab-tarefas-pendentes"]').click();

    cy.get('[data-cy="lista-tarefas-pendentes"]')
      .contains('[data-cy="item-tarefa"]', tarefaNome)
      .within(() => {
        // Use the checkbox data-cy to avoid coupling to visual classes
        cy.get('[data-cy="checkbox-tarefa"]').check({ force: true });
      });

    cy.contains('Atividade marcada como realizada/estudada.').should('be.visible');

    cy.get('[data-cy="subtab-tarefas-concluidas"]').click();
    // Use data-cy selector for the concluded tasks container
    cy.get('[data-cy="tarefas-concluidas"]').should('be.visible').contains(tarefaNome).should('be.visible');
  });
});