import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const credPath = path.resolve(__dirname, '../Booking - Dashboard Executivo de Performance/nnos-dashboard-9e61e1181de1.json');
if (!fs.existsSync(credPath)) {
  console.error('[ERRO] Credenciais do Google não encontradas em:', credPath);
  process.exit(1);
}

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
  if (!data.access_token) {
    throw new Error('Falha ao obter access token: ' + JSON.stringify(data));
  }
  return data.access_token;
}

async function run() {
  const t = await token();
  const sheetId = '1oyOo2Y5HXTEN_8LhW9ekMNRBssCxZ5uyCFFQnB9Z1PM';
  const url = `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'Prospecção'!A1:F100`;
  const res = await fetch(url, { headers: { authorization: `Bearer ${t}` } });
  const json = await res.json();
  const rows = json.values || [];

  const monthMap = {
    '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr', '05': 'Mai', '06': 'Jun',
    '07': 'Jul', '08': 'Ago', '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
  };

  const items = [];
  for (let i = 1; i < rows.length; i++) {
    const r = rows[i];
    if (!r || r.length === 0 || (r[0] && r[0].toLowerCase().includes('total geral'))) continue;
    let proj = (r[0] || '').trim();
    let ativ = (r[1] || '').trim();
    let local = (r[2] || '').trim();
    const dtIni = (r[3] || '').trim();
    const dtFim = (r[4] || '').trim();
    const valStr = (r[5] || '').toString().trim().replace(/\./g, '').replace(',', '.');
    const valor = parseFloat(valStr) || 0;

    // Normalização de linhas vazias identificadas no Google Sheets
    if (!ativ && dtIni === '24/01/2026' && valor === 1486.20) {
      ativ = 'Reunião Diretoria NNÓS (24/Jan)';
      local = 'Nova Lima | MG';
    } else if (!ativ && dtIni === '09/09/2026' && valor === 170.04) {
      ativ = 'Alimentação Visita Volvo';
      local = 'Curitiba | PR';
    }

    if (!ativ && valor === 0) continue;

    // Padronizar separador de localidade
    local = local.replace(/\s*\|\s*/g, ' - ');
    if (!local) local = 'Brasil';

    // Mês da atividade
    const mNum = dtIni.split('/')[1];
    const mes = monthMap[mNum] || 'Outro';

    // Internacional vs Nacional
    const lLow = local.toLowerCase();
    const isIntl = lLow.includes('eua') || 
                   lLow.includes('las vegas') || 
                   lLow.includes('china') || 
                   lLow.includes('paraguai') || 
                   lLow.includes('paraguay') || 
                   lLow.includes('par') || 
                   lLow.includes('nova iorque');
    const tipo = isIntl ? 'intl' : 'nac';

    // Categorização gerencial consistente
    let categoria = 'Outros';
    const aLow = ativ.toLowerCase();
    if (aLow.includes('planejamento') || aLow.includes('reunião diretoria') || aLow.includes('diretoria uva')) {
      categoria = 'Planejamento & Diretoria';
    } else if (isIntl) {
      categoria = 'Viagens Internacionais';
    } else if (aLow.includes('prospec') || aLow.includes('prospeção')) {
      categoria = 'Prospecção';
    } else if (aLow.includes('almoço') || aLow.includes('jantar') || aLow.includes('café') || aLow.includes('alimentação')) {
      categoria = 'Refeições de Negócio';
    } else if (aLow.includes('agrishow') || aLow.includes('accelera') || aLow.includes('manus ia') || aLow.includes('nnós day')) {
      categoria = 'Eventos & Feiras';
    } else if (aLow.includes('visita') || aLow.includes('service game') || aLow.includes('clientes sodecia')) {
      categoria = 'Visitas Técnicas';
    } else if (aLow.includes('workshop') || aLow.includes('rh leadership') || aLow.includes('back office')) {
      categoria = 'Treinamentos';
    }

    items.push({
      id: items.length + 1,
      projeto: proj,
      nome: ativ,
      local: local,
      mes: mes,
      tipo: tipo,
      valor: valor,
      categoria: categoria,
      dtIni: dtIni,
      dtFim: dtFim
    });
  }

  const outPath = path.resolve(__dirname, 'prospeccao_data.json');
  fs.writeFileSync(outPath, JSON.stringify(items, null, 2), 'utf8');
  console.log(`[OK] Extraídos ${items.length} registros com sucesso para ${outPath}`);
  const total = items.reduce((acc, it) => acc + it.valor, 0);
  console.log(`[OK] Valor Total Consolidado: R$ ${total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`);
}

run().catch(err => {
  console.error('[ERRO]', err);
  process.exit(1);
});
