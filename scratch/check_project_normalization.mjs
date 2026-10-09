import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const credPath = path.resolve(__dirname, '../../Booking - Dashboard Executivo de Performance/nnos-dashboard-9e61e1181de1.json');
const cred = JSON.parse(fs.readFileSync(credPath, 'utf8'));

async function token() {
  const iat = Math.floor(Date.now() / 1000);
  const exp = iat + 3600;
  const header = Buffer.from(JSON.stringify({ alg: 'RS256', typ: 'JWT' })).toString('base64url');
  const claim = Buffer.from(JSON.stringify({
    iss: cred.client_email,
    scope: 'https://www.googleapis.com/auth/spreadsheets.readonly',
    aud: 'https://oauth2.googleapis.com/token',
    exp, iat
  })).toString('base64url');
  const sign = crypto.createSign('RSA-SHA256');
  sign.update(header + '.' + claim);
  const sig = sign.sign(cred.private_key).toString('base64url');
  const body = `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${header}.${claim}.${sig}`;
  const r = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body
  });
  const data = await r.json();
  return data.access_token;
}

function norm(s) {
  return (s || '').toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().replace(/\s+/g, ' ');
}

async function run() {
  const t = await token();
  const sheetId = '1oyOo2Y5HXTEN_8LhW9ekMNRBssCxZ5uyCFFQnB9Z1PM';

  const liderData = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../lider_data.json'), 'utf8'));
  const painelProjs = [];
  liderData.leaders.forEach(l => {
    l.projetos.forEach(p => painelProjs.push({ titulo: p.titulo, lider: l.lider, area: p.area }));
  });

  // Consolidado
  const resCons = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'Detalhado - CONSOLIDADO'!A1:B1455`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dCons = await resCons.json();
  const consProjs = new Set((dCons.values || []).slice(1).map(r => norm(r[1])));

  // Faturamento
  const resFat = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FATURAMENTO'!A5:C713`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dFat = await resFat.json();
  const fatProjs = new Set((dFat.values || []).slice(1).map(r => norm(r[2])));

  console.log(`Verificando os 44 projetos do Painel:`);
  let matchesCons = 0;
  let matchesFat = 0;

  painelProjs.forEach(p => {
    const np = norm(p.titulo);
    const inCons = consProjs.has(np);
    const inFat = fatProjs.has(np);
    if (inCons) matchesCons++;
    if (inFat) matchesFat++;
    if (!inCons || !inFat) {
      console.log(`- "${p.titulo}" (${p.lider} | ${p.area}): inCons=${inCons}, inFat=${inFat}`);
    }
  });

  console.log(`\nResultado: matches Consolidado = ${matchesCons}/${painelProjs.length}, matches Faturamento = ${matchesFat}/${painelProjs.length}`);
}
run();
