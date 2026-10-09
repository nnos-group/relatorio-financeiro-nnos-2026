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

const MESES_MAP = {
  '01': 'JANEIRO', '1': 'JANEIRO', 'JAN': 'JANEIRO', 'JANEIRO': 'JANEIRO',
  '02': 'FEVEREIRO', '2': 'FEVEREIRO', 'FEV': 'FEVEREIRO', 'FEVEREIRO': 'FEVEREIRO',
  '03': 'MARÇO', '3': 'MARÇO', 'MAR': 'MARÇO', 'MARÇO': 'MARÇO', 'MARCO': 'MARÇO',
  '04': 'ABRIL', '4': 'ABRIL', 'ABR': 'ABRIL', 'ABRIL': 'ABRIL',
  '05': 'MAIO', '5': 'MAIO', 'MAI': 'MAIO', 'MAIO': 'MAIO',
  '06': 'JUNHO', '6': 'JUNHO', 'JUN': 'JUNHO', 'JUNHO': 'JUNHO',
  '07': 'JULHO', '7': 'JULHO', 'JUL': 'JULHO', 'JULHO': 'JULHO',
  '08': 'AGOSTO', '8': 'AGOSTO', 'AGO': 'AGOSTO', 'AGOSTO': 'AGOSTO',
  '09': 'SETEMBRO', '9': 'SETEMBRO', 'SET': 'SETEMBRO', 'SETEMBRO': 'SETEMBRO',
  '10': 'OUTUBRO', 'OUT': 'OUTUBRO', 'OUTUBRO': 'OUTUBRO',
  '11': 'NOVEMBRO', 'NOV': 'NOVEMBRO', 'NOVEMBRO': 'NOVEMBRO',
  '12': 'DEZEMBRO', 'DEZ': 'DEZEMBRO', 'DEZEMBRO': 'DEZEMBRO',
  'ADIANTAMENTO': 'JANEIRO'
};

async function run() {
  const t = await token();
  const sheetId = '1oyOo2Y5HXTEN_8LhW9ekMNRBssCxZ5uyCFFQnB9Z1PM';

  // Fetch Detalhado - CONSOLIDADO
  const resCons = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'Detalhado - CONSOLIDADO'!A1:AF1455`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dCons = await resCons.json();
  const rowsCons = dCons.values || [];

  // Fetch FATURAMENTO
  const resFat = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FATURAMENTO'!A5:N713`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dFat = await resFat.json();
  const rowsFat = dFat.values || [];

  // Previsto por Projeto e por Mês
  const prevMap = {}; // { proj: { total: 0, meses: { JANEIRO: 0, ... } } }
  for (let i = 1; i < rowsCons.length; i++) {
    const r = rowsCons[i];
    const proj = (r[1] || '').trim().toUpperCase();
    const dtIni = (r[6] || '').trim();
    const dtFim = (r[7] || '').trim();
    const val = parseNum(r[12]);
    if (!proj || val <= 0) continue;

    let mesNum = '';
    if (dtIni.includes('/')) mesNum = dtIni.split('/')[1];
    else if (dtFim.includes('/')) mesNum = dtFim.split('/')[1];
    const mesNome = MESES_MAP[mesNum] || 'JANEIRO';

    if (!prevMap[proj]) {
      prevMap[proj] = { total: 0, meses: {} };
    }
    prevMap[proj].total += val;
    prevMap[proj].meses[mesNome] = (prevMap[proj].meses[mesNome] || 0) + val;
  }

  // Realizado por Projeto e por Mês (usando Col A REALIZADO)
  const realMap = {}; // { proj: { total: 0, meses: { JANEIRO: 0, ... } } }
  for (let i = 1; i < rowsFat.length; i++) {
    const r = rowsFat[i];
    const mesRaw = (r[0] || '').trim().toUpperCase();
    const proj = (r[2] || '').trim().toUpperCase();
    const val = parseNum(r[5]);
    if (!proj || val <= 0) continue;

    const mesNome = MESES_MAP[mesRaw] || 'OUTROS';

    if (!realMap[proj]) {
      realMap[proj] = { total: 0, meses: {} };
    }
    realMap[proj].total += val;
    realMap[proj].meses[mesNome] = (realMap[proj].meses[mesNome] || 0) + val;
  }

  console.log(`Projetos com Previsto: ${Object.keys(prevMap).length}`);
  console.log(`Projetos com Realizado: ${Object.keys(realMap).length}`);

  // Test comparison for sample projects
  const sampleProjs = ['INSTRUTORES PORSCHE', 'BACKOFFICE PORSCHE', 'BACKOFFICE CNHI', 'PARTS ACADEMY', 'DEALER STANDARD CONSTRUCION'];
  sampleProjs.forEach(p => {
    const pr = prevMap[p] || { total: 0, meses: {} };
    const re = realMap[p] || { total: 0, meses: {} };
    console.log(`\nPROJETO: ${p}`);
    console.log(`  Previsto Total: R$ ${pr.total.toFixed(2)} | Realizado Total: R$ ${re.total.toFixed(2)}`);
    console.log(`  Jan -> Prev: R$ ${(pr.meses['JANEIRO']||0).toFixed(2)} | Real: R$ ${(re.meses['JANEIRO']||0).toFixed(2)}`);
    console.log(`  Fev -> Prev: R$ ${(pr.meses['FEVEREIRO']||0).toFixed(2)} | Real: R$ ${(re.meses['FEVEREIRO']||0).toFixed(2)}`);
    console.log(`  Mar -> Prev: R$ ${(pr.meses['MARÇO']||0).toFixed(2)} | Real: R$ ${(re.meses['MARÇO']||0).toFixed(2)}`);
  });
}
run();
