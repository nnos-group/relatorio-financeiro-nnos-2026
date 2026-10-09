import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const liderData = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../lider_data.json'), 'utf8'));
const allLiderProjs = [];
liderData.lideres.forEach(l => {
  l.projetos.forEach(p => {
    allLiderProjs.push({ titulo: p.titulo, lider: l.nome, area: p.area });
  });
});

console.log(`Total de projetos no Painel por Líder: ${allLiderProjs.length}`);
allLiderProjs.slice(0, 10).forEach(p => console.log(` - [${p.lider}] [${p.area}] ${p.titulo}`));
