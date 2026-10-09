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
  const urlFat = `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FATURAMENTO'!A5:N713`;
  const resFat = await fetch(urlFat, { headers: { authorization: `Bearer ${t}` } });
  const dFat = await resFat.json();
  const rows = dFat.values || [];

  console.log('Headers (Row 5):', rows[0]);

  let totalAFaturar = 0;
  let countAFaturar = 0;

  for (let i = 1; i < rows.length; i++) {
    const r = rows[i];
    const rowStr = r.join(' | ').toUpperCase();
    if (rowStr.includes('A FATURAR')) {
      const val = parseFloat((r[5] || '0').replace(/[()R$\s]/g, '').replace(/\./g, '').replace(',', '.')) || 0;
      totalAFaturar += val;
      countAFaturar++;
      console.log(`Linha ${i + 5}: Mes=${r[0]} | Col B=${r[1]} | Proj=${r[2]} | Perfil=${r[3]} | Valor=${r[5]} (num=${val}) | Status=${r[7]}`);
    }
  }

  console.log(`\nTotal de linhas com 'A FATURAR': ${countAFaturar}`);
  console.log(`Soma dos valores 'A FATURAR': R$ ${totalAFaturar.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`);
}

run().catch(console.error);
