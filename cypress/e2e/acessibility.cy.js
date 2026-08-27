describe('Teste de acessibilidade', () => {
  
    beforeEach(() => {
        cy.visit('http://127.0.0.1:8000') 
        cy.injectAxe() 
    })

    it('avalia a página inteira', () => {
        cy.checkA11y() 
    })

    it('avalia elemento específico', () => {
        cy.checkA11y('.panel') // Testa apenas o bloco de login
    })

    it('avalia ignorando elementos', () => {
        cy.checkA11y({ exclude: ['img'] }) 
    })

    it('avalia limitando às regras oficiais (WCAG)', () => {
        cy.checkA11y(null, {
        runOnly: {
            type: 'tag',
            values: ['wcag2a', 'wcag2aa'], 
        },
        })
    })

    it('avalia com regras customizadas', () => {
        cy.checkA11y(null, {
        rules: {
            'color-contrast': { enabled: false }, 
            'image-alt': { enabled: true }, 
        },
        })
    })
})