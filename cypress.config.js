const { defineConfig } = require('cypress');
//const installLogsPrinter = require('cypress-terminal-report/src/installLogsPrinter');

module.exports = defineConfig({
  e2e: {
    /*
    setupNodeEvents(on, config) {
      installLogsPrinter(on);
      return config;
    }, // plugin cypress-terminal-report
    */
    baseUrl: process.env.CYPRESS_BASE_URL || 'http://127.0.0.1:8000',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    video: true,
  },

  component: {
    devServer: {
      framework: "react",
      bundler: "vite",
    },
  },
});
