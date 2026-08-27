describe('Testes E2E - Login', () => {
  const usuario = 'Maria';
  const senha = '123456';

  it('deve realizar login com sucesso pela interface', () => {
    cy.visit('/');

    cy.get('[data-cy="titulo-login"]')
      .should('contain', 'Já sou usuário');

    cy.get('[data-cy="username"]').type(usuario);
    cy.get('[data-cy="password"]').type(senha);
    cy.get('[data-cy="login-button"]').click();

    cy.url().should('include', '/schedules/main_calendar_view');
  });
});


describe('Testes de API - Login', () => {
  const usuario = 'Maria';
  const senha = '123456';

  it('deve realizar login com sucesso pela API', () => {
    cy.request({
      method: 'POST',
      url: '/api/login/',
      body: {
        username: usuario,
        password: senha
      }
    }).then((resposta) => {

      expect(resposta.status).to.eq(200);

      expect(resposta.body.message)
        .to.eq('Login realizado com sucesso');
    });
  });
});