Cypress.Commands.add('login', (username, password) => {
  cy.session([username, password], () => {
    cy.visit('/')
    cy.get('input[name="username"]').type(username)
    cy.get('input[name="password"]').type(password)
    cy.get('button[type="submit"]').click()
    cy.url().should('include', '/main_calendar_view')
  })
})

Cypress.Commands.add('criarAgendaUI', (nome) => {
  cy.visit('/schedules/main_calendar_view/?tab=agendas')
  cy.get('[data-cy="btn-novo"]').click()
  cy.get('[data-cy="form-nova-agenda"]').should('be.visible').within(() => {
    cy.get('[data-cy="input-nome-agenda"]').type(nome)
    cy.get('[data-cy="btn-salvar-agenda"]').click()
  })
})

Cypress.Commands.add('criarAtividadeUI', (agendaNome, titulo, tipo, categoria) => {
  cy.visit('/schedules/main_calendar_view/?tab=eventos')
  cy.get('[data-cy="btn-novo"]').click()
  cy.get('[data-cy="form-nova-atividade"]').should('be.visible').within(() => {
    cy.get('[data-cy="select-agenda"]').select(agendaNome)
    cy.get('[data-cy="input-titulo-atividade"]').type(titulo)
    cy.get('[data-cy="select-tipo"]').select(tipo)
    cy.get('[data-cy="select-categoria"]').select(categoria)
    if (tipo === 'event') cy.get('[data-cy="input-date"]').type('2026-06-30')
    cy.get('[data-cy="btn-salvar-atividade"]').click()
  })
})