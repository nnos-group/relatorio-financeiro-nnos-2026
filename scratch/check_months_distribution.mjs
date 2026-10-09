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

  // 1. Detalhado - CONSOLIDADO
  const resCons = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'Detalhado - CONSOLIDADO'!A1:AF2500`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dCons = await resCons.json();
  const consRows = dCons.values || [];
  console.log('Detalhado - CONSOLIDADO total rows:', consRows.length);

  const monthsFromDates = new Map();
  let totalFaturar = 0;
  let rowsComFaturar = 0;

  function parseNum(val) {
    if (!val) return 0;
    let s = val.toString().trim();
    const neg = s.startsWith('(') && s.endsWith(')');
    s = s.replace(/[()R$\s]/g, '').replace(/\./g, '').replace(',', '.');
    let n = parseFloat(s) || 0;
    return neg ? -Math.abs(n) : n;
  }

  for (let i = 1; i < consRows.length; i++) {
    const r = consRows[i];
    const proj = (r[1] || '').trim();
    const dtIni = (r[6] || '').trim();
    const dtFim = (r[7] || '').trim();
    const faturarVal = parseNum(r[12]);
    if (faturarVal > 0) {
      rowsComFaturar++;
      totalFaturar += faturarVal;

      // Extract month
      let m = '';
      if (dtIni && dtIni.includes('/')) {
        const parts = dtIni.split('/');
        if (parts.length === 3) m = parts[1]; // month
      } else if (dtFim && dtFim.includes('/')) {
        const parts = dtFim.split('/');
        if (parts.length === 3) m = parts[1];
      }
      monthsFromDates.set(m, (monthsFromDates.get(m) || 0) + faturarVal);
    }
  }

  console.log(`Linhas com FATURAR: ${rowsComFaturar}, Total Previsto FATURAR: R$ ${totalFaturar.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
  console.log('Distribuição por Mês da Data Inicial:', Object.fromEntries(monthsFromDates));

  // 2. FATURAMENTO
  const resFat = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FATURAMENTO'!A5:N1500`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dFat = await resFat.json();
  const fatRows = dFat.values || [];
  console.log('\nFATURAMENTO total rows:', fatRows.length);

  const fatPorMesRealizado = new Map();
  const fatPorMesFaturado = new Map();
  let totalFat = 0;

  for (let i = 1; i < fatRows.length; i++) {
    const r = fatRows[i];
    const mesReal = (r[0] || '').trim().toUpperCase();
    const mesFat = (r[1] || '').trim().toUpperCase();
    const valor = parseNum(r[5]);
    if (valor > 0) {
      totalFat += valor;
      fatPorMesRealizado.set(mesReal, (fatPorMesRealizado.get(mesReal) || 0) + valor);
      fatPorMesFaturado.set(mesFat, (fatPorMesFaturado.get(mesFat) || 0) + valor);
    }
  }

  console.log(`Total FATURAMENTO: R$ ${totalFat.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
  console.log('FATURAMENTO agrupado por Col A (REALIZADO):', Object.fromEntries(fatPorMesRealizado));
  console.log('FATURAMENTO agrupado por Col B (FATURADO):', Object.fromEntries(fatPorMesFaturado));
}
run();
