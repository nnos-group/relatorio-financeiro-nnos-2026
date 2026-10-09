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

async function inspectTab(sheetId, tabName, range) {
  const t = await token();
  const res = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'${encodeURIComponent(tabName)}'!${range}`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const data = await res.json();
  console.log(`\n================== TAB: ${tabName} (${range}) ==================`);
  if (!data.values || data.values.length === 0) {
    console.log('No values');
    return;
  }
  data.values.slice(0, 10).forEach((r, idx) => {
    console.log(`Row ${idx + 1}:`, JSON.stringify(r.slice(0, 20)));
  });
}

async function run() {
  const sheetId = '1oyOo2Y5HXTEN_8LhW9ekMNRBssCxZ5uyCFFQnB9Z1PM';
  await inspectTab(sheetId, 'FATURAMENTO', 'A5:Z10');
  await inspectTab(sheetId, 'PEDIDOS', 'A1:T8');
  await inspectTab(sheetId, 'Base_Project Cards', 'A1:T8');
  await inspectTab(sheetId, 'Acompanhamento', 'A1:T8');
  await inspectTab(sheetId, 'FINANCEIRO', 'A1:T8');
}
run();
