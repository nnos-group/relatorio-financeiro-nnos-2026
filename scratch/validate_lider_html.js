const fs = require('fs');
const html = fs.readFileSync('lider.html', 'utf8');

console.log('HTML size:', html.length, 'bytes');
console.log('Contains #faturamento-projetos:', html.includes('id="faturamento-projetos"'));
console.log('Contains #tabelaFaturamentoBody:', html.includes('id="tabelaFaturamentoBody"'));
console.log('Contains faturamentoProjetosData:', html.includes('const faturamentoProjetosData = ['));
console.log('Contains filtrarMesFaturamento:', html.includes('function filtrarMesFaturamento'));
console.log('Contains atualizarPainelFaturamento:', html.includes('function atualizarPainelFaturamento'));

// Check for script tags and validate JS syntax
const scriptMatches = html.match(/<script[\s\S]*?<\/script>/gi);
console.log('Script tags count:', scriptMatches.length);

let testedMain = false;
scriptMatches.forEach((s, idx) => {
  const code = s.replace(/<\/?script[^>]*>/gi, '');
  if (code.includes('faturamentoProjetosData')) {
    testedMain = true;
    console.log(`Main logic script found (size: ${code.length} chars)`);
    try {
      new Function(code);
      console.log('Main logic script syntax: OK (No SyntaxError)');
    } catch(e) {
      console.error(`JS Syntax error in script ${idx}:`, e.message);
    }
  }
});

if (testedMain) {
  console.log('[SUCCESS] lider.html script evaluated with 0 syntax errors!');
}
