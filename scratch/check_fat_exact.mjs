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

  const res = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FATURAMENTO'!A5:N1294`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const data = await res.json();
  const rows = data.values || [];
  
  rows.forEach((r, idx) => {
    if ((r[0] || '').trim() === '1' || (r[0] || '').trim().length === 1) {
      console.log(`[FAT Row ${idx+5}]`, JSON.stringify(r.slice(0, 8)));
    }
    if ((r[0] || '').trim() === 'Total geral' || (r[1] || '').trim() === 'Total geral') {
      console.log(`[Total Row ${idx+5}]`, JSON.stringify(r.slice(0, 8)));
    }
  });

  // Check last row with content
  let lastIdx = 0;
  rows.forEach((r, idx) => {
    if (r.some(c => c && c.trim())) lastIdx = idx;
  });
  console.log(`Last non-empty row index: ${lastIdx + 5}, content:`, JSON.stringify(rows[lastIdx].slice(0, 8)));
}
run();
