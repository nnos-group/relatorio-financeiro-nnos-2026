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

async function inspectFinanceiro() {
  const t = await token();
  const sheetId = '1oyOo2Y5HXTEN_8LhW9ekMNRBssCxZ5uyCFFQnB9Z1PM';
  const res = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FINANCEIRO'!A4:AU50`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const data = await res.json();
  console.log('FINANCEIRO rows count:', (data.values || []).length);
  const rows = data.values || [];
  console.log('Row 4 (header months):', JSON.stringify(rows[0]));
  console.log('Row 6 (header cols):', JSON.stringify(rows[2]));
  console.log('Row 7 (sub-header):', JSON.stringify(rows[3]));

  console.log('\nSample project rows:');
  for (let i = 4; i < Math.min(rows.length, 30); i++) {
    const r = rows[i];
    if (r[0] && r[0].trim()) {
      console.log(`[${i+4}] Project: "${r[0]}" | Perfil: "${r[1]}" | Budget: "${r[2]}" | Prev YTD: "${r[3]}" | Fat YTD: "${r[4]}" | Prev Jan: "${r[6]}" | Fat Jan: "${r[7]}" | Prev Fev: "${r[9]}" | Fat Fev: "${r[10]}" | Prev Mar: "${r[12]}" | Fat Mar: "${r[13]}"`);
    }
  }
}
inspectFinanceiro();
