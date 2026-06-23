describe('Fluxo de conta', () => {
  const username = `cypress_${Date.now()}`;
  const password = 'SenhaCypress123';

  it('cria conta, faz login e cancela a exclusão', () => {
    cy.visit('/sign-up/');
    cy.contains('Cadastrar novo usuário').should('be.visible');

    cy.get('input[name="username"]').type(username);
    cy.get('input[name="password"]').type(password);
    cy.get('input[name="password_confirm"]').type(password);

    cy.get('form[action*="register"] button[type="submit"]').click();

    cy.location('pathname', { timeout: 10000 }).should('eq', '/');
    cy.contains('Usuário criado com sucesso').should('be.visible');

    cy.get('input[name="username"]').clear().type(username);
    cy.get('input[name="password"]').type(password);
    cy.get('form[action*="login"] button[type="submit"]').click();

    cy.location('pathname', { timeout: 10000 }).should('include', '/schedules/main_calendar_view');

    cy.visit('/user/');
    cy.contains('Espaço do Usuário').should('be.visible');
    cy.contains(username).should('be.visible');

    let confirmMessage = '';
    cy.on('window:confirm', (message) => {
      confirmMessage = message;
      expect(message).to.contain('Tem certeza que deseja excluir sua conta?');
      return false;
    });

    cy.get('form.delete-form button[type="submit"]').click();

    cy.then(() => {
      expect(confirmMessage).to.not.be.empty;
    });

    cy.location('pathname', { timeout: 10000 }).should('eq', '/user/');
    cy.contains('Espaço do Usuário').should('be.visible');
    cy.contains(username).should('be.visible');
  });
});
