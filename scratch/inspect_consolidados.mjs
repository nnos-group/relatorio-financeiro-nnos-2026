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

  // 1. Inspecionar Detalhado - CONSOLIDADO
  const resCons = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'Detalhado - CONSOLIDADO'!A1:Z50`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dCons = await resCons.json();
  console.log('=== Detalhado - CONSOLIDADO Headers ===');
  console.log('Row 1:', JSON.stringify(dCons.values[0]));
  console.log('Samples rows 2-10:');
  dCons.values.slice(1, 10).forEach((r, idx) => {
    console.log(`[${idx+2}] CC: "${r[0]}" | PROJETO: "${r[1]}" | DATA INI: "${r[6]}" | DATA FIM: "${r[7]}" | FATURAR: "${r[12]}" | REPASSE: "${r[13]}"`);
  });

  // Check columns of Detalhado - CONSOLIDADO up to column AF
  const resConsCols = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'Detalhado - CONSOLIDADO'!A1:AG5`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dConsCols = await resConsCols.json();
  console.log('\nAll column headers in Detalhado - CONSOLIDADO:');
  dConsCols.values[0].forEach((col, idx) => console.log(`Col ${idx} (${String.fromCharCode(65 + (idx < 26 ? idx : idx))}): "${col}"`));

  // 2. Inspecionar FATURAMENTO
  const resFat = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FATURAMENTO'!A5:N20`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dFat = await resFat.json();
  console.log('\n=== FATURAMENTO Samples ===');
  console.log('Row 5 (header):', JSON.stringify(dFat.values[0]));
  dFat.values.slice(1, 6).forEach((r, idx) => {
    console.log(`[${idx+6}] REALIZADO: "${r[0]}" | FATURADO: "${r[1]}" | PROJETO: "${r[2]}" | VALOR: "${r[5]}" | STATUS: "${r[7]}" | VENC: "${r[8]}" | PGTO: "${r[9]}" | ÁREA: "${r[13]}"`);
  });
}
run();
