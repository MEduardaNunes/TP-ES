import Contador from './Contador';

describe('Componente Contador', () => {
  it('deve iniciar zerado e incrementar o valor ao clicar', () => {
    cy.mount(<Contador />);
    
    cy.get('[data-cy="valor"]').should('have.text', '0');
    cy.get('[data-cy="botao-incrementar"]').click();
    cy.get('[data-cy="valor"]').should('have.text', '1');
  });
});