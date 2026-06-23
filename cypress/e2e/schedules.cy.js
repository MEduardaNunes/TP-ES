describe('Fluxo de schedules', () => {
  const username = 'admin';
  const password = 'admin123';

  const timestamp = Date.now();
  const scheduleName = `Agenda Cypress ${timestamp}`;
  const taskTitle = `Tarefa Cypress 24-06 ${timestamp}`;

 // Cadastro do usuário admin
  before(() => {
    const managePyPath = `${Cypress.config('projectRoot')}/tp_es/manage.py`;

    cy.exec(
      [
        `python "${managePyPath}" shell -c`,
        '"from django.contrib.auth import get_user_model; ',
        'User = get_user_model(); ',
        'user, _ = User.objects.get_or_create(username=\'admin\'); ',
        'user.set_password(\'admin123\'); ',
        'user.save()"',
      ].join(' ')
    );
  });

  it('cria agenda, adiciona tarefa em 24/06 e marca como concluida', () => {
    cy.visit('/');

    cy.get('input[name="username"]').type(username);
    cy.get('input[name="password"]').type(password);
    cy.get('form[action*="login"] button[type="submit"]').click();

    cy.location('pathname', { timeout: 10000 }).should('include', '/schedules/main_calendar_view');

    cy.get('[data-cy="tab-agendas"]').click();
    cy.get('[data-cy="btn-novo"]').click();

    cy.get('#agenda-modal').should('not.have.class', 'hidden');
    cy.get('#agenda-form input[name="name"]').type(scheduleName);
    cy.get('#agenda-form textarea[name="description"]').type('Agenda criada pelo teste E2E de schedules.');
    cy.get('#agenda-form button[type="submit"]').contains('Criar').click();

    cy.location('search', { timeout: 10000 }).should('include', 'tab=agendas');
    cy.contains('.list-card--schedule', scheduleName).should('be.visible');

    cy.get('[data-cy="tab-tarefas"]').click();
    cy.get('[data-cy="btn-novo"]').click();

    cy.get('[data-cy="form-nova-atividade"]').should('be.visible');
    cy.get('[data-cy="select-agenda"]').select(scheduleName);
    cy.get('[data-cy="input-titulo-atividade"]').type(taskTitle);
    cy.get('[data-cy="select-tipo"]').should('have.value', 'task');
    cy.get('[data-cy="select-categoria"]').select('assignment');
    cy.get('[data-cy="input-date"]').type('2026-06-24');
    cy.get('[data-cy="input-notas"]').type('Tarefa criada para validar conclusao no E2E.');
    cy.get('[data-cy="btn-salvar-atividade"]').click();

    cy.visit('/schedules/main_calendar_view/?mes=6&ano=2026&tab=tarefas');
    cy.get('[data-cy="lista-tarefas-pendentes"]')
      .contains('[data-cy="item-tarefa"]', taskTitle)
      .as('tarefaPendente')
      .should('be.visible');

    cy.get('@tarefaPendente')
      .find('[data-cy="checkbox-tarefa"]')
      .check({ force: true });

    cy.location('search', { timeout: 10000 }).should('include', 'tab=tarefas');
    cy.get('[data-cy="subtab-tarefas-concluidas"]').click();

    cy.get('#tarefas-concluidas')
      .should('be.visible')
      .contains(taskTitle)
      .should('be.visible');
  });
});