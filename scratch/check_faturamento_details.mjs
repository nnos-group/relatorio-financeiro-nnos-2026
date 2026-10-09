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

async function run() {
  const t = await token();
  const sheetId = '1oyOo2Y5HXTEN_8LhW9ekMNRBssCxZ5uyCFFQnB9Z1PM';

  // Check FATURAMENTO unique values
  const resFat = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FATURAMENTO'!A5:N300`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dFat = await resFat.json();
  const fatRows = dFat.values || [];
  console.log('FATURAMENTO rows fetched:', fatRows.length);
  const colA = new Set();
  const colB = new Set();
  const projsFat = new Set();
  fatRows.slice(1).forEach(r => {
    if (r[0]) colA.add(r[0].trim());
    if (r[1]) colB.add(r[1].trim());
    if (r[2]) projsFat.add(r[2].trim());
  });
  console.log('Col A (REALIZADO) values:', Array.from(colA));
  console.log('Col B (FATURADO) values:', Array.from(colB));
  console.log('Unique projects in FATURAMENTO:', projsFat.size);

  // Check FINANCEIRO projects vs lider projects
  const resFin = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FINANCEIRO'!A6:AU200`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dFin = await resFin.json();
  const finRows = dFin.values || [];
  const finProjs = [];
  finRows.forEach(r => {
    if (r[0] && r[0] !== 'PROJETO' && r[1] === 'TOTAL') {
      finProjs.push(r[0].trim());
    }
  });
  console.log('FINANCEIRO TOTAL projects:', finProjs);
}
run();
