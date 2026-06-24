describe('Fluxo de schedules - Edição', () => {
  const username = 'admin';
  const password = 'admin123';

  const timestamp = Date.now();
  const scheduleName = `Agenda Cypress ${timestamp}`;
  const newScheduleName = `Edit Agenda Cypress ${timestamp}`;

  before(() => {
    const managePyPath = `${Cypress.config('projectRoot')}/tp_es/manage.py`;
    cy.exec(
      `python "${managePyPath}" shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user, _ = User.objects.get_or_create(username='${username}'); user.set_password('${password}'); user.save()"`
    );
  });

  beforeEach(() => {
    cy.login(username, password); // login chamado SÓ aqui, não dentro do it()
  });

  it('CT01: edita nome de agenda e verifica alteração', () => {
    cy.criarAgendaUI(scheduleName);

    cy.visit('/schedules/main_calendar_view/?tab=agendas');
    cy.contains(scheduleName).should('be.visible');

    // Escopa a busca do botão "Editar" dentro do card da agenda específica
    cy.contains('.list-card--schedule', scheduleName)
      .find('[data-cy="edit-btn"]')
      .click();

    cy.contains('Editar agenda').should('be.visible');
    cy.get('[data-cy="name-schedule-input"]').clear().type(newScheduleName);
    cy.get('[data-cy="btn-salvar-edicao-agenda"]').click();

    // Confirma que o modal fechou antes de seguir
    cy.get('#edit-agenda-modal').should('have.class', 'hidden');

    cy.visit('/schedules/main_calendar_view/?tab=agendas');
    cy.contains(newScheduleName).should('be.visible');
    cy.contains(scheduleName).should('not.exist'); // garante que o nome antigo não existe mais
  });

  it('CT02: adiciona evento na agenda criada e edita seu título', () => {
    const eventTitle = `Evento Cypress ${timestamp}`;
    const newEventTitle = `Edit ${eventTitle}`;

    // Garante que a agenda existe para o evento ser criado e editado
    cy.criarAgendaUI(newScheduleName);

    cy.visit('/schedules/main_calendar_view/?tab=eventos');
    cy.contains(newScheduleName).should('be.visible');

    cy.get('[data-cy="btn-novo"]').click();
    cy.get('[data-cy="form-nova-atividade"]').should('be.visible').within(() => {
      cy.get('[data-cy="select-agenda"]').select(newScheduleName);
      cy.get('[data-cy="input-titulo-atividade"]').type(eventTitle);
      cy.get('[data-cy="select-tipo"]').select('event');
      cy.get('[data-cy="select-categoria"]').select('meeting');
      cy.get('[data-cy="input-date"]').type('2026-07-01');
      cy.get('[data-cy="input-start-time"]').type('10:00');
      cy.get('[data-cy="input-end-time"]').type('11:00');
      cy.get('[data-cy="btn-salvar-atividade"]').click();
    });

    cy.visit('/schedules/main_calendar_view/?tab=eventos');
    cy.contains(eventTitle).should('be.visible');

    cy.contains('[data-cy="item-evento"]', eventTitle)
      .contains('Editar')
      .click();

    cy.get('[data-cy="form-editar-atividade"]').should('be.visible').within(() => {
      cy.get('[data-cy="input-editar-titulo-atividade"]').clear().type(newEventTitle);
      cy.get('[data-cy="btn-salvar-edicao-atividade"]').click();
    });

    cy.visit('/schedules/main_calendar_view/?tab=eventos');
    cy.contains(newEventTitle).should('be.visible');
    cy.contains(eventTitle).should('not.exist');
  });
});