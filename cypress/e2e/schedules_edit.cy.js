describe('Fluxo de schedules - Edição', () => {
  const username = 'admin';
  const password = 'admin123';

  const timestamp = Date.now();
  const scheduleName = `Agenda Cypress ${timestamp}`;
  const newScheduleName = `Agenda Editada ${timestamp}`;

  before(() => {
    const managePyPath = `${Cypress.config('projectRoot')}/tp_es/manage.py`;
    cy.exec(
      `python "${managePyPath}" shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user, _ = User.objects.get_or_create(username='${username}'); user.set_password('${password}'); user.save()"`
    );
  });

  beforeEach(() => {
    cy.login(username, password); 
  });

it('CT01: edita nome de agenda e verifica alteração', () => {
    cy.criarAgendaUI(scheduleName);

    cy.visit('/schedules/main_calendar_view/');
    cy.switchTab('tab-agendas');
    cy.contains(scheduleName).should('be.visible');

    cy.contains('.list-card--schedule', scheduleName)
      .find('[data-cy="edit-btn"]')
      .click();

    cy.get('#edit-agenda-modal').should('not.have.class', 'hidden').within(() => {
      cy.get('[data-cy="name-schedule-input"]').clear().type(newScheduleName);
      cy.get('[data-cy="btn-salvar-edicao-agenda"]').click();
    });

    cy.get('#edit-agenda-modal').should('have.class', 'hidden');

    cy.reload();
    
    cy.switchTab('tab-agendas');
    cy.contains(newScheduleName).should('be.visible');
    cy.contains(scheduleName).should('not.exist');
  });

  it('CT02: adiciona evento na agenda criada e edita seu título', () => {
    const localTimestamp = Date.now(); 
    const agendaParaEvento = `Agenda CT02 ${localTimestamp}`;
    const eventTitle = `Evento Cypress ${localTimestamp}`;
    const newEventTitle = `Evento Editado ${localTimestamp}`;

    // Garante que a agenda existe para o evento ser criado e editado
    cy.criarAgendaUI(agendaParaEvento);

    cy.visit('/schedules/main_calendar_view/');
    cy.switchTab('tab-eventos');

    cy.get('[data-cy="btn-novo"]').click();

    cy.get('[data-cy="select-agenda"]')
      .should('not.have.value', '') 
      .select(agendaParaEvento);

    cy.get('[data-cy="form-nova-atividade"]').within(() => {
      cy.get('[data-cy="input-titulo-atividade"]').type(eventTitle);
      cy.get('[data-cy="select-tipo"]').select('event');
      cy.get('[data-cy="select-categoria"]').select('meeting');
      cy.get('[data-cy="input-date"]').type('2026-06-30'); // Data alterada para Junho (mês atual)
      cy.get('[data-cy="input-start-time"]').type('10:00');
      cy.get('[data-cy="input-end-time"]').type('11:00');
      cy.get('[data-cy="btn-salvar-atividade"]').click();
    });

    cy.contains('Atividade criada com sucesso.').should('be.visible');
    cy.reload();
    cy.switchTab('tab-eventos');

    cy.get('[data-cy="container-eventos"]').contains(eventTitle).should('be.visible');

    cy.contains('[data-cy="item-evento"]', eventTitle)
      .find('[data-cy="btn-editar-atividade"]')
      .click();

    cy.get('[data-cy="form-editar-atividade"]').should('be.visible').within(() => {
      cy.get('[data-cy="input-editar-titulo-atividade"]').clear().type(newEventTitle);
      cy.get('[data-cy="btn-salvar-edicao-atividade"]').click();
    });

    cy.get('[data-cy="form-editar-atividade"]').should('not.be.visible');

    cy.reload();
    cy.switchTab('tab-eventos');

    cy.contains(newEventTitle).should('be.visible');
    cy.contains(eventTitle).should('not.exist');
  });
});