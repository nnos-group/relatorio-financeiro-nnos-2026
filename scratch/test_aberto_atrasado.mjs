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

  const resFat = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'FATURAMENTO'!A5:N713`, {
    headers: { authorization: `Bearer ${t}` }
  });
  const dFat = await resFat.json();
  const rows = dFat.values || [];

  let totRealizado = 0;
  let totAberto = 0;
  let totAtrasado = 0;
  let totIgnoradoPerfil = 0;

  const abertosPorMes = {};
  const atrasadosPorMes = {};

  for (let i = 1; i < rows.length; i++) {
    const r = rows[i];
    const mesRaw = (r[0] || '').trim().toUpperCase();
    const proj = (r[2] || '').trim();
    const perfil = (r[3] || '').trim().toUpperCase();
    const val = parseNum(r[5]);
    const status = (r[7] || '').trim();
    const diasStr = (r[10] || '').trim();
    const dias = parseInt(diasStr) || 0;
    const pagtoStr = (r[11] || '').trim().toUpperCase();

    if (!proj || val <= 0) continue;

    // REGRA 1: Não entra no cálculo de faturamento linhas com PERFIL LOGÍSTICA E MATERIAL
    if (perfil.includes('LOGÍSTICA') || perfil.includes('LOGISTICA') || perfil.includes('MATERIAL')) {
      totIgnoradoPerfil += val;
      continue;
    }

    const mes = MESES_MAP[mesRaw];
    if (!mes) continue;

    totRealizado += val;

    // Verificar se não teve confirmação de pagamento
    const isNaoPago = (status.toLowerCase() !== 'pago');

    if (isNaoPago) {
      // Verificar se passou do prazo de vencimento (Atrasado) ou está dentro do prazo (Em Aberto)
      const isAtrasado = dias > 0 || pagtoStr.includes('ATRASO');
      if (isAtrasado) {
        totAtrasado += val;
        atrasadosPorMes[mes] = (atrasadosPorMes[mes] || 0) + val;
      } else {
        totAberto += val;
        abertosPorMes[mes] = (abertosPorMes[mes] || 0) + val;
      }
    }
  }

  console.log(`FATURAMENTO (Sem Logística e Material): R$ ${totRealizado.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
  console.log(`Ignorado (Logística + Material): R$ ${totIgnoradoPerfil.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
  console.log(`EM ABERTO (Dentro do vencimento e s/ pgto): R$ ${totAberto.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
  console.log(`ATRASADO (Passou do vencimento): R$ ${totAtrasado.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
  console.log('\nEm Aberto por Mês:', abertosPorMes);
  console.log('Atrasado por Mês:', atrasadosPorMes);
}
run();
