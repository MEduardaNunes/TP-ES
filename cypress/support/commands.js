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

/**
 * Clica em uma aba e aguarda que ela fique visível.
 * Resolve o problema de timing quando as abas são carregadas dinamicamente.
 * 
 * @param {string} dataCy - O valor do data-cy do botão da aba (ex: 'tab-eventos')
 * @param {number} timeout - Timeout em ms (default: 5000)
 * 
 * @example
 * cy.switchTab('tab-eventos')
 * cy.switchTab('tab-tarefas', 6000)
 */
Cypress.Commands.add('switchTab', (dataCy, timeout = 6000) => {
  // Clica no botão da aba
  cy.get(`[data-cy="${dataCy}"]`).click()

  // Extrai o ID da aba do atributo content-id
  cy.get(`[data-cy="${dataCy}"]`)
    .invoke('attr', 'content-id')
    .then((tabId) => {
      // Aguarda que a aba tenha a classe 'show' (indicando que está visível)
      cy.get(`#${tabId}.show`, { timeout }).should('exist')
    })
})