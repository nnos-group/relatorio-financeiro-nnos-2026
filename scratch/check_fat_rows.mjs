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

  const res = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FATURAMENTO'!A1:N100`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const data = await res.json();
  const rows = data.values || [];
  
  // Find where col A has '1' or ''
  rows.forEach((r, idx) => {
    if (r[0] === '1' || idx < 10) {
      console.log(`[Row ${idx+1}] A: "${r[0]}" | B: "${r[1]}" | C: "${r[2]}" | F: "${r[5]}" | H: "${r[7]}" | N: "${r[13]}"`);
    }
  });

  // Check rows beyond 100 where col A is '1'
  const res2 = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FATURAMENTO'!A100:N350`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const d2 = await res2.json();
  console.log('\nScanning rows 100-350 for col A = "1" or totals:');
  (d2.values || []).forEach((r, idx) => {
    if (r[0] === '1' || (r[1] && r[1].includes('Total')) || (r[2] && r[2].includes('Total'))) {
      console.log(`[Row ${idx+100}] A: "${r[0]}" | B: "${r[1]}" | C: "${r[2]}" | F: "${r[5]}"`);
    }
  });
}
run();
