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

function parseNum(val) {
  if (!val) return 0;
  let s = val.toString().trim();
  const neg = s.startsWith('(') && s.endsWith(')');
  s = s.replace(/[()R$\s]/g, '').replace(/\./g, '').replace(',', '.');
  let n = parseFloat(s) || 0;
  return neg ? -Math.abs(n) : n;
}

function parsePct(val) {
  if (!val) return 0;
  let s = val.toString().trim().replace('%', '').replace(/\./g, '').replace(',', '.');
  return parseFloat(s) || 0;
}

const SIGLAS = new Set([
  'NNÓS', 'NNOS', 'MG', 'SP', 'PR', 'RJ', 'EUA', 'USA', 'PAR', 'CT', 'UVA', 
  'TRP', 'LATAM', 'BI', 'ADS', 'NH', 'IA', 'IVECO', 'DAF', 'BH', 'RH', 'NY', 
  'VOA', 'DRE', 'ROI', 'YTD', 'CRM', 'ERP', 'SODECIA', 'JAECCO', 'CNH', 'CNHI',
  'DM', 'DDN', 'POE', 'CPSL', 'NHCE'
]);

const LOWERCASE_WORDS = new Set([
  'de', 'da', 'do', 'das', 'dos', 'em', 'com', 'para', 'por', 'e', 'a', 'ao', 'aos', 'à', 'às'
]);

function cleanTitleCase(text) {
  if (!text) return text;
  const parts = text.split(/(\s*[-–—/\\+&|]\s*|\s*\(\s*|\s*\)\s*)/);
  const resParts = parts.map(part => {
    if (/^\s*[-–—/\\+&|]\s*$/.test(part) || /^\s*[\(\)]\s*$/.test(part)) return part;
    const tokens = part.match(/[\wÀ-ÿ]+|[^\w\sÀ-ÿ]+|\s+/g) || [];
    let isFirst = true;
    return tokens.map(token => {
      if (/^[\wÀ-ÿ]+$/.test(token)) {
        const upper = token.toUpperCase();
        let formatted = '';
        for (const s of SIGLAS) {
          if (upper === s.toUpperCase()) {
            formatted = s;
            break;
          }
        }
        if (!formatted) {
          if (!isFirst && LOWERCASE_WORDS.has(upper.toLowerCase())) {
            formatted = upper.toLowerCase();
          } else {
            formatted = token.charAt(0).toUpperCase() + token.slice(1).toLowerCase();
          }
        }
        isFirst = false;
        return formatted;
      } else {
        if (/[:.!]/.test(token)) isFirst = true;
        return token;
      }
    }).join('');
  });
  return resParts.join('');
}

function getProjectArea(titulo, lider = '') {
  const t = (titulo || '').toUpperCase();
  const l = (lider || '').toUpperCase();

  if (t.includes('CAMPUS BH') || t.includes('VEIGA DE ALMEIDA')) return 'Educação';
  if (t.includes('NNOS ACADEMY') || t.includes('INNOVATION')) return 'Innovation';
  if (t.includes('DEALER STANDARD') || t.startsWith('DM -') || t.includes('DDN') || t.includes('DEALER DEVELOPMENT')) return 'Dealer Development';
  if (t.includes('INSTRUTORES PORSCHE')) return 'HRD';
  if (t.includes('BACKOFFICE') || t.includes('CONSULTORIA PÓS-VENDAS') || t.includes('POE') || t.includes('INSTRUTORES CNH')) return 'Outsourcing';

  if (l.includes('BEATRIZ')) return 'HRD';
  if (l.includes('CAROLINE')) return 'Business Solutions';
  if (l.includes('JEFFERSON')) return 'Dealer Development';
  if (l.includes('VINICIUS')) return 'Outsourcing';
  if (l.includes('JOICE')) return 'Educação';
  if (l.includes('LEONARDO')) return 'Innovation';
  if (l.includes('FÁBIO') || l.includes('FABIO')) return 'Outsourcing';

  return 'Outsourcing';
}

async function run() {
  const t = await token();
  const sheetId = '1oyOo2Y5HXTEN_8LhW9ekMNRBssCxZ5uyCFFQnB9Z1PM';

  // 1. Fetch grid de líderes e projetos (Col A:S)
  const urlGrid = `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'Painel por Líder'!A1:S185`;
  const resGrid = await fetch(urlGrid, { headers: { authorization: `Bearer ${t}` } });
  const dataGrid = await resGrid.json();
  const rowsGrid = dataGrid.values || [];

  // 2. Fetch tabelas de mais e menos rentáveis + metas (Col U:AG)
  const urlTables = `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/'Painel por Líder'!U1:AG65`;
  const resTables = await fetch(urlTables, { headers: { authorization: `Bearer ${t}` } });
  const dataTables = await resTables.json();
  const rowsTables = dataTables.values || [];

  const leaderNames = [
    'BEATRIZ PICORELLI',
    'CAROLINE AMIEVA',
    'JEFFERSON SOUZA',
    'JOICE LAGE',
    'LEONARDO CAMPOS',
    'VINICIUS SOUZA',
    'FÁBIO CANASSA'
  ];

  const leaders = [];
  let currentLeader = null;

  for (let r = 0; r < rowsGrid.length; r++) {
    const row = rowsGrid[r] || [];
    const col0 = (row[0] || '').trim();

    const matchedLeader = leaderNames.find(l => col0 === l);
    if (matchedLeader) {
      const parts = matchedLeader.split(' ');
      const iniciais = (parts[0][0] + (parts[1] ? parts[1][0] : '')).toUpperCase();
      currentLeader = {
        id: leaders.length + 1,
        nome: cleanTitleCase(matchedLeader),
        nomeRaw: matchedLeader,
        iniciais,
        total: null,
        projetos: []
      };
      leaders.push(currentLeader);
      continue;
    }

    if (!currentLeader) continue;

    const offsets = [0, 5, 10, 15];
    const isMetricRow = offsets.some(off => (row[off] || '').trim() === 'RECEITA');
    if (isMetricRow) {
      const titleRow = rowsGrid[r - 2] && offsets.some(off => (rowsGrid[r - 2][off] || '').trim().length > 0 && (rowsGrid[r - 2][off] || '').trim() !== 'RECEITA')
        ? rowsGrid[r - 2]
        : (rowsGrid[r - 1] || []);

      offsets.forEach(off => {
        const rawTitle = (titleRow[off] || '').trim();
        const recLabel = (rowsGrid[r] && rowsGrid[r][off] ? rowsGrid[r][off].trim() : '');
        if (recLabel === 'RECEITA' && rawTitle) {
          const receita = parseNum(rowsGrid[r] ? rowsGrid[r][off + 1] : 0);
          const receitaPct = parsePct(rowsGrid[r] ? rowsGrid[r][off + 3] : '100%');
          const impostos = parseNum(rowsGrid[r+1] ? rowsGrid[r+1][off + 1] : 0);
          const impostosPct = parsePct(rowsGrid[r+1] ? rowsGrid[r+1][off + 3] : 0);
          const custos = parseNum(rowsGrid[r+2] ? rowsGrid[r+2][off + 1] : 0);
          const custosPct = parsePct(rowsGrid[r+2] ? rowsGrid[r+2][off + 3] : 0);
          const logistica = parseNum(rowsGrid[r+3] ? rowsGrid[r+3][off + 1] : 0);
          const logisticaPct = parsePct(rowsGrid[r+3] ? rowsGrid[r+3][off + 3] : 0);
          const repasse = parseNum(rowsGrid[r+4] ? rowsGrid[r+4][off + 1] : 0);
          const repassePct = parsePct(rowsGrid[r+4] ? rowsGrid[r+4][off + 3] : 0);
          const margem = parseNum(rowsGrid[r+5] ? rowsGrid[r+5][off + 1] : 0);
          const margemPct = parsePct(rowsGrid[r+5] ? rowsGrid[r+5][off + 3] : 0);

          let statusCor = 'emerald';
          if (margem < 0) statusCor = 'rose';
          else if (margemPct < 22) statusCor = 'amber';
          else if (margemPct <= 30) statusCor = 'sky';

          const pArea = getProjectArea(rawTitle, currentLeader.nomeRaw);
          const card = {
            titulo: cleanTitleCase(rawTitle),
            tituloRaw: rawTitle,
            area: pArea,
            receita,
            receitaPct,
            impostos,
            impostosPct,
            custos,
            custosPct,
            logistica,
            logisticaPct,
            repasse,
            repassePct,
            margem,
            margemPct,
            statusCor
          };

          if (rawTitle.startsWith('TOTAL -')) {
            currentLeader.total = card;
          } else {
            currentLeader.projetos.push(card);
          }
        }
      });
    }
  }

  // 3. Processar "20 PROJETOS MAIS RENTÁVEIS" (Cols U:Z => cols 0:5 em rowsTables)
  const maisRentaveis = [];
  for (let r = 3; r <= 22; r++) {
    const row = rowsTables[r] || [];
    const rank = parseInt(row[0]) || (r - 2);
    const proj = (row[1] || '').trim();
    const lider = (row[2] || '').trim();
    const receita = parseNum(row[3]);
    const margem = parseNum(row[4]);
    const margemPct = parsePct(row[5]);
    if (proj) {
      maisRentaveis.push({
        ranking: rank,
        projeto: cleanTitleCase(proj),
        lider: cleanTitleCase(lider),
        area: getProjectArea(proj, lider),
        receita,
        margem,
        margemPct
      });
    }
  }

  // 4. Processar "10 PROJETOS MENOS RENTÁVEIS" (Cols AB:AG => cols 7:12 em rowsTables)
  const menosRentaveis = [];
  for (let r = 3; r <= 12; r++) {
    const row = rowsTables[r] || [];
    const rank = parseInt(row[7]) || (r - 2);
    const proj = (row[8] || '').trim();
    const lider = (row[9] || '').trim();
    const receita = parseNum(row[10]);
    const margem = parseNum(row[11]);
    const margemPct = parsePct(row[12]);
    if (proj) {
      menosRentaveis.push({
        ranking: rank,
        projeto: cleanTitleCase(proj),
        lider: cleanTitleCase(lider),
        area: getProjectArea(proj, lider),
        receita,
        margem,
        margemPct
      });
    }
  }

  // 5. Processar "CONTROLE DE METAS POR ÁREA | 2026"
  const metasAreas = [];
  // Linhas 30 a 42 de 'Painel por Líder' correspondem a rowsTables índices 29 a 42
  for (let r = 30; r <= 42; r += 2) {
    const row = rowsTables[r] || [];
    const area = (row[0] || '').trim();
    if (!area) continue;
    const metaVal = parseNum(row[3]);
    const realizadoVal = parseNum(row[5]);
    const atingidoPct = (row[7] || '').trim();
    const faltaVal = parseNum(row[8]);
    const faltaPct = (row[10] || '').trim();
    metasAreas.push({
      area: cleanTitleCase(area),
      meta: metaVal,
      realizado: realizadoVal,
      atingidoPct,
      falta: faltaVal,
      faltaPct,
      isTotal: area.includes('META GERAL')
    });
  }

  // Totais Globais
  const globalReceita = leaders.reduce((acc, l) => acc + (l.total ? l.total.receita : 0), 0);
  const globalCustos = leaders.reduce((acc, l) => acc + (l.total ? l.total.custos : 0), 0);
  const globalImpostos = leaders.reduce((acc, l) => acc + (l.total ? l.total.impostos : 0), 0);
  const globalLogistica = leaders.reduce((acc, l) => acc + (l.total ? l.total.logistica : 0), 0);
  const globalRepasse = leaders.reduce((acc, l) => acc + (l.total ? l.total.repasse : 0), 0);
  const globalMargem = leaders.reduce((acc, l) => acc + (l.total ? l.total.margem : 0), 0);
  const globalMargemPct = globalReceita > 0 ? (globalMargem / globalReceita * 100) : 0;
  const totalProjetos = leaders.reduce((acc, l) => acc + l.projetos.length, 0);

  const payload = {
    updatedAt: new Date().toISOString(),
    macro: {
      receita: globalReceita,
      custos: globalCustos,
      custosPct: globalReceita > 0 ? (globalCustos / globalReceita * 100) : 0,
      impostos: globalImpostos,
      impostosPct: globalReceita > 0 ? (globalImpostos / globalReceita * 100) : 0,
      logistica: globalLogistica,
      logisticaPct: globalReceita > 0 ? (globalLogistica / globalReceita * 100) : 0,
      repasse: globalRepasse,
      repassePct: globalReceita > 0 ? (globalRepasse / globalReceita * 100) : 0,
      margem: globalMargem,
      margemPct: globalMargemPct,
      totalLideres: leaders.length,
      totalProjetos
    },
    leaders,
    maisRentaveis,
    menosRentaveis,
    metasAreas
  };

  const outPath = path.resolve(__dirname, 'lider_data.json');
  fs.writeFileSync(outPath, JSON.stringify(payload, null, 2), 'utf8');
  console.log(`[OK] Extraídos ${leaders.length} líderes com ${totalProjetos} projetos com sucesso.`);
  console.log(`[OK] 20 mais rentáveis: ${maisRentaveis.length} registros.`);
  console.log(`[OK] 10 menos rentáveis: ${menosRentaveis.length} registros.`);
  console.log(`[OK] Metas por Área: ${metasAreas.length} registros.`);
  console.log(`[OK] Receita Bruta Global: R$ ${globalReceita.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`);
  console.log(`[OK] Salvo em: ${outPath}`);
}

run().catch(err => {
  console.error('[ERRO]', err);
  process.exit(1);
});
