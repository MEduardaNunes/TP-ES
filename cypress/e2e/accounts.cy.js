describe('Teste de Login', () => {
  const usuario = `Maria`;
  const senha = '123456';

  it('deve realizar login com sucesso', () => {
    cy.visit('/');
    cy.get('[data-cy="titulo-login"]').should('contain', 'Já sou usuário');
    
    cy.get('[data-cy="username"]').type(usuario);
    cy.get('[data-cy="password"]').type(senha);
    cy.get('[data-cy="login-button"]').click();
    
    cy.url().should('include', '/schedules/main_calendar_view');
  });
});
