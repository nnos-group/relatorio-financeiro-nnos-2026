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

function parseNum(val) {
  if (!val) return 0;
  let s = val.toString().trim();
  const neg = s.startsWith('(') && s.endsWith(')');
  s = s.replace(/[()R$\s]/g, '').replace(/\./g, '').replace(',', '.');
  let n = parseFloat(s) || 0;
  return neg ? -Math.abs(n) : n;
}

async function run() {
  const t = await token();
  const sheetId = '1oyOo2Y5HXTEN_8LhW9ekMNRBssCxZ5uyCFFQnB9Z1PM';

  // Fetch FATURAMENTO
  const resFat = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FATURAMENTO'!A5:N713`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dFat = await resFat.json();
  const rows = dFat.values || [];

  console.log('Header Row 5:', JSON.stringify(rows[0]));

  const perfis = new Set();
  const statuses = new Set();
  const pagtos = new Set();

  for (let i = 1; i < rows.length; i++) {
    const r = rows[i];
    if (r[3]) perfis.add(r[3].trim());
    if (r[7]) statuses.add(r[7].trim());
    if (r[11]) pagtos.add(r[11].trim());
  }

  console.log('\nPerfis encontrados em FATURAMENTO:');
  console.log(Array.from(perfis));

  console.log('\nStatus encontrados em FATURAMENTO (Col H):');
  console.log(Array.from(statuses));

  console.log('\nPagtos encontrados em FATURAMENTO (Col L):');
  console.log(Array.from(pagtos).slice(0, 15));

  // Exemplos de linhas não pagas
  console.log('\nExemplos de linhas NÃO PAGAS:');
  let countNonPago = 0;
  for (let i = 1; i < rows.length; i++) {
    const r = rows[i];
    const status = (r[7] || '').trim();
    if (status.toLowerCase() !== 'pago' && countNonPago < 10) {
      console.log(`[Row ${i+5}] Realizado: "${r[0]}" | Proj: "${r[2]}" | Perfil: "${r[3]}" | Valor: "${r[5]}" | Status: "${r[7]}" | Venc: "${r[8]}" | DtPgto: "${r[9]}" | Dias: "${r[10]}" | Pagto: "${r[11]}"`);
      countNonPago++;
    }
  }

  // Exemplos de linhas com LOGÍSTICA / MATERIAL
  console.log('\nExemplos de linhas LOGÍSTICA / MATERIAL:');
  let countLog = 0;
  for (let i = 1; i < rows.length; i++) {
    const r = rows[i];
    const perfil = (r[3] || '').trim().toUpperCase();
    if ((perfil.includes('LOGÍSTICA') || perfil.includes('LOGISTICA') || perfil.includes('MATERIAL')) && countLog < 5) {
      console.log(`[Row ${i+5}] Perfil: "${r[3]}" | Proj: "${r[2]}" | Valor: "${r[5]}" | Status: "${r[7]}"`);
      countLog++;
    }
  }
}
run();
