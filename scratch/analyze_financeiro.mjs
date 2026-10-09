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
  const res = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FINANCEIRO'!A6:AU500`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const data = await res.json();
  const rows = data.values || [];
  console.log('Total rows in FINANCEIRO A6:AU500:', rows.length);
  
  const totalRows = [];
  rows.forEach((r, idx) => {
    const proj = (r[0] || '').trim();
    const perfil = (r[1] || '').trim();
    if (proj && proj !== 'PROJETO' && perfil === 'TOTAL') {
      totalRows.push({
        rowNum: idx + 6,
        proj,
        budget: r[2],
        prevYtd: r[3],
        fatYtd: r[4],
        jan: { prev: r[6], fat: r[7] },
        fev: { prev: r[9], fat: r[10] },
        mar: { prev: r[12], fat: r[13] },
        abr: { prev: r[15], fat: r[16] },
        mai: { prev: r[18], fat: r[19] },
        jun: { prev: r[21], fat: r[22] },
        jul: { prev: r[24], fat: r[25] },
        ago: { prev: r[27], fat: r[28] },
        set: { prev: r[30], fat: r[31] },
        out: { prev: r[33], fat: r[34] },
        nov: { prev: r[36], fat: r[37] },
        dez: { prev: r[39], fat: r[40] }
      });
    }
  });

  console.log(`Found ${totalRows.length} project TOTAL rows:`);
  totalRows.slice(0, 15).forEach(tr => {
    console.log(`- ${tr.proj} (Row ${tr.rowNum}) | PrevYTD: ${tr.prevYtd} | FatYTD: ${tr.fatYtd} | Jan: [P:${tr.jan.prev}, F:${tr.jan.fat}] | Fev: [P:${tr.fev.prev}, F:${tr.fev.fat}]`);
  });

  // Also check if there are project rows that don't say TOTAL
  const allProjs = new Set();
  rows.forEach(r => {
    const proj = (r[0] || '').trim();
    if (proj && proj !== 'PROJETO') allProjs.add(proj);
  });
  console.log(`Unique project names in FINANCEIRO: ${allProjs.size}`);
}
run();
