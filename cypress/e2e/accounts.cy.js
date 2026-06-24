describe('Fluxo de conta', () => {
  const username = `cypress_${Date.now()}`;
  const password = 'SenhaCypress123';

  it ('CT01: cria conta', () => {
    cy.visit('/sign-up/');
    cy.contains('Cadastrar novo usuário').should('be.visible');

    cy.get('input[name="username"]').type(username);
    cy.get('input[name="password"]').type(password);
    cy.get('input[name="password_confirm"]').type(password);

    cy.get('form[action*="register"] button[type="submit"]').click();

    cy.location('pathname', { timeout: 10000 }).should('eq', '/');
    cy.contains('Usuário criado com sucesso').should('be.visible');
  });

  it('CT02: faz login', () => {
    cy.visit('')
    cy.get('input[name="username"]').type(username)
    cy.get('input[name="password"]').type(password)
    cy.get('button[type="submit"]').click()
    cy.location('pathname', { timeout: 10000 }).should('include', '/schedules/main_calendar_view');
  });

  it('CT03: deve confirmar a exclusão da conta', () => {
    cy.login(username, password)
    cy.visit('/edit-user/');

    cy.window().then((win) => {
      cy.stub(win, 'confirm').returns(false).as('confirmStub');
    });

    cy.get('.button-danger').click();

    cy.get('@confirmStub').should(
      'have.been.calledWith',
      'Tem certeza que deseja excluir sua conta? Essa ação é irreversível.'
    );

    cy.contains('Usuário deletado com sucesso').should('not.exist');
  });
});
