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

function normStr(s) {
  return (s || '').toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().replace(/\s+/g, ' ');
}

const MESES = [
  'JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO',
  'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'
];

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

async function testCleanData() {
  const t = await token();
  const sheetId = '1oyOo2Y5HXTEN_8LhW9ekMNRBssCxZ5uyCFFQnB9Z1PM';

  const liderData = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../lider_data.json'), 'utf8'));
  const listaProjetos = [];
  const projNormMap = new Map();

  liderData.leaders.forEach(l => {
    l.projetos.forEach(p => {
      const pObj = {
        titulo: p.titulo,
        lider: l.nome,
        area: p.area,
        previsto: { TOTAL: 0 },
        realizado: { TOTAL: 0 },
        aberto: { TOTAL: 0 },
        atrasado: { TOTAL: 0 }
      };
      MESES.forEach(m => {
        pObj.previsto[m] = 0;
        pObj.realizado[m] = 0;
        pObj.aberto[m] = 0;
        pObj.atrasado[m] = 0;
      });
      listaProjetos.push(pObj);
      projNormMap.set(normStr(p.titulo), pObj);
    });
  });

  // Previsto de Detalhado - CONSOLIDADO
  const resCons = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'Detalhado - CONSOLIDADO'!A1:AF1455`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dCons = await resCons.json();
  const rowsCons = dCons.values || [];

  for (let i = 1; i < rowsCons.length; i++) {
    const r = rowsCons[i];
    const rawProj = (r[1] || '').trim();
    const dtIni = (r[6] || '').trim();
    const dtFim = (r[7] || '').trim();
    const val = parseNum(r[12]);
    if (!rawProj || val <= 0) continue;

    let mesNum = '';
    if (dtIni.includes('/')) mesNum = dtIni.split('/')[1];
    else if (dtFim.includes('/')) mesNum = dtFim.split('/')[1];
    const mesNome = MESES_MAP[mesNum] || 'JANEIRO';

    const pObj = projNormMap.get(normStr(rawProj));
    if (pObj) {
      pObj.previsto[mesNome] = (pObj.previsto[mesNome] || 0) + val;
      pObj.previsto.TOTAL += val;
    }
  }

  // Realizado de FATURAMENTO (Excluindo LOGÍSTICA e MATERIAL)
  const resFat = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FATURAMENTO'!A5:N713`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dFat = await resFat.json();
  const rowsFat = dFat.values || [];

  for (let i = 1; i < rowsFat.length; i++) {
    const r = rowsFat[i];
    const mesRaw = (r[0] || '').trim().toUpperCase();
    const rawProj = (r[2] || '').trim();
    const perfil = (r[3] || '').trim().toUpperCase();
    const val = parseNum(r[5]);
    const status = (r[7] || '').trim();
    const diasStr = (r[10] || '').trim();
    const dias = parseInt(diasStr) || 0;
    const pagtoStr = (r[11] || '').trim().toUpperCase();

    if (!rawProj || val <= 0) continue;

    // REGRA DO USUÁRIO: NÃO ENTRA NO CÁLCULO DE FATURAMENTO LINHAS COM PERFIL LOGÍSTICA E MATERIAL
    if (perfil.includes('LOGÍSTICA') || perfil.includes('LOGISTICA') || perfil.includes('MATERIAL')) {
      continue;
    }

    const mesNome = MESES_MAP[mesRaw];
    if (!mesNome) continue;

    const pObj = projNormMap.get(normStr(rawProj));
    if (pObj) {
      pObj.realizado[mesNome] = (pObj.realizado[mesNome] || 0) + val;
      pObj.realizado.TOTAL += val;

      const isNaoPago = (status.toLowerCase() !== 'pago');
      if (isNaoPago) {
        const isAtrasado = dias > 0 || pagtoStr.includes('ATRASO');
        if (isAtrasado) {
          pObj.atrasado[mesNome] = (pObj.atrasado[mesNome] || 0) + val;
          pObj.atrasado.TOTAL += val;
        } else {
          pObj.aberto[mesNome] = (pObj.aberto[mesNome] || 0) + val;
          pObj.aberto.TOTAL += val;
        }
      }
    }
  }

  console.log('=== TOTAIS GLOBAIS APÓS REGRAS ===');
  let totPrev = listaProjetos.reduce((a, p) => a + p.previsto.TOTAL, 0);
  let totReal = listaProjetos.reduce((a, p) => a + p.realizado.TOTAL, 0);
  let totAberto = listaProjetos.reduce((a, p) => a + p.aberto.TOTAL, 0);
  let totAtrasado = listaProjetos.reduce((a, p) => a + p.atrasado.TOTAL, 0);

  console.log(`Previsto: R$ ${totPrev.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
  console.log(`Realizado (sem Log/Mat): R$ ${totReal.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
  console.log(`Em Aberto (a vencer): R$ ${totAberto.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
  console.log(`Atrasado: R$ ${totAtrasado.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);

  MESES.forEach(m => {
    let pM = listaProjetos.reduce((a, p) => a + p.previsto[m], 0);
    let rM = listaProjetos.reduce((a, p) => a + p.realizado[m], 0);
    let abM = listaProjetos.reduce((a, p) => a + p.aberto[m], 0);
    let atM = listaProjetos.reduce((a, p) => a + p.atrasado[m], 0);
    console.log(`[${m}] Prev: R$ ${pM.toFixed(0)} | Real: R$ ${rM.toFixed(0)} | Aberto: R$ ${abM.toFixed(0)} | Atrasado: R$ ${atM.toFixed(0)}`);
  });
}
testCleanData();
