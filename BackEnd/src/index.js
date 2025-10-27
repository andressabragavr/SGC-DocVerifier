// index.js
import express from 'express';
import cors from 'cors';
import { PrismaClient } from '@prisma/client';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { exec } from 'child_process';
import util from 'util';
import crypto from 'crypto';
import axios from 'axios';
import dotenv from 'dotenv';
import { z } from 'zod';
dotenv.config();

const app = express();
const PORT = 3000;
const prisma = new PrismaClient();
const execPromise = util.promisify(exec);

// Diretório de upload
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const uploadPath = path.join(__dirname, '..', 'uploads');
if (!fs.existsSync(uploadPath)) {
  fs.mkdirSync(uploadPath);
}

const AGENT_BASE = process.env.AGENT_BASE ?? 'http://localhost:5055';
const AGENT_API_KEY = process.env.AGENT_API_KEY ?? '';

// Helpers de status
export const STATUS = {
  PENDENTE: 'PENDENTE',
  ACEITO: 'ACEITO',
  RECUSADO: 'RECUSADO',
  AJUSTAR: 'AJUSTAR',
};

// Multer
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadPath),
  filename: (req, file, cb) => cb(null, Date.now() + '-' + file.originalname),
});
const upload = multer({ storage });

// Schemas
const userCreateSchema = z.object({
  name: z.string().trim().min(2, 'Nome é obrigatório'),
  email: z.string().trim().email('E-mail inválido'),
  password: z.string().trim().min(6, 'Senha deve ter ao menos 6 caracteres'),
  ra: z.string().trim().min(3, 'RA é obrigatório'),
  curso: z.string().trim().min(2, 'Curso é obrigatório'),
  tipo: z.enum(['aluno', 'coordenador']).default('aluno'),
});

// Middlewares
app.use(express.json());
app.use(cors());
app.use('/uploads', express.static(uploadPath));

/* =========================
 *      ROTAS DE USUÁRIO
 * ========================= */
app.post('/usuarios', async (req, res) => {
  try {
    const data = userCreateSchema.parse(req.body);
    const user = await prisma.user.create({ data });
    res.status(201).json(user);
  } catch (err) {
    if (err?.issues) {
      return res.status(400).json({ error: 'Dados inválidos', details: err.issues });
    }
    res.status(500).json({ error: 'Erro ao criar usuário' });
  }
});

app.get('/usuarios', async (req, res) => {
  const users = await prisma.user.findMany();
  res.status(200).json(users);
});

// Login (RA ou e-mail)
app.post('/login', async (req, res) => {
  const { ra, email, password } = req.body;
  try {
    const loginValue = String(email || ra || '').trim();
    if (!loginValue || !password) {
      return res.status(400).json({ error: 'Informe RA ou e-mail e a senha.' });
    }
    const isEmail = loginValue.includes('@');
    const user = isEmail
      ? await prisma.user.findFirst({
          where: { email: { equals: loginValue, mode: 'insensitive' } },
        })
      : await prisma.user.findUnique({ where: { ra: loginValue } });

    if (!user || user.password !== password) {
      return res.status(401).json({ error: 'Credenciais inválidas' });
    }
    const { password: _, ...userSemSenha } = user;
    res.status(200).json(userSemSenha);
  } catch (error) {
    console.error('Erro no login:', error);
    res.status(500).json({ error: 'Erro interno no login' });
  }
});

/* =====================================================
 *     HISTÓRICO DO ALUNO (MOSTRA APENAS ACEITOS)
 * ===================================================== */
app.get('/usuarios/:ra/certificados', async (req, res) => {
  const { ra } = req.params;
  try {
    const user = await prisma.user.findUnique({ where: { ra } });
    if (!user) return res.status(404).json({ error: 'Usuário não encontrado' });

    const certificados = await prisma.certificado.findMany({
      where: { userId: user.id, status: STATUS.ACEITO },
      orderBy: { dataEnvio: 'desc' },
    });

    res.status(200).json(certificados);
  } catch (error) {
    console.error('Erro ao buscar certificados:', error);
    res.status(500).json({ error: 'Erro interno no servidor' });
  }
});

/* =====================================================
 *            UPLOAD + EXTRAÇÃO + VALIDAÇÃO
 * ===================================================== */
app.post('/certificados/upload', upload.single('arquivo'), async (req, res) => {
  const { ra } = req.body;
  const file = req.file;
  if (!file) return res.status(400).json({ error: 'Arquivo não enviado' });

  try {
    const user = await prisma.user.findUnique({ where: { ra } });
    if (!user) return res.status(404).json({ error: 'Usuário não encontrado' });

    // Executa script de extração local (OCR/LLM inicial)
    const scriptPath = path.join(__dirname, '..', '..', 'IA', 'main.py');
    const caminhoPDF = path.join(uploadPath, file.filename);
    const nomeAluno = user.name || 'Aluno Desconhecido';
    const raAluno = user.ra;
    const cursoAluno = user.curso || 'Curso Desconhecido';

    // Hash p/ duplicidade forte
    const buffer = await fs.promises.readFile(caminhoPDF);
    const fileHashSHA256 = crypto.createHash('sha256').update(buffer).digest('hex');
    const jaExiste = await prisma.certificado.findFirst({ where: { fileHashSHA256 } });
    if (jaExiste) {
      return res.status(409).json({
        error: 'Arquivo já enviado anteriormente (duplicata forte).',
        certificadoId: jaExiste.id,
      });
    }

    const { stdout, stderr } = await execPromise(
      `python "${scriptPath}" "${caminhoPDF}" "${nomeAluno}" "${raAluno}" "${cursoAluno}"`
    );
    if (stderr) console.error('Erro da IA:', stderr);

    let resultadoIA;
    try {
      resultadoIA = JSON.parse(stdout);
    } catch {
      return res.status(500).json({ error: 'Erro ao interpretar resultado da IA' });
    }
    if (!resultadoIA || (Array.isArray(resultadoIA) && resultadoIA.length === 0)) {
      return res.status(400).json({ error: 'IA não retornou dados de extração' });
    }

    const dados = Array.isArray(resultadoIA) ? resultadoIA[0] : resultadoIA;

    // Normalizações mínimas
    const horas = parseInt(dados.quantidade_horas || '0', 10) || 0;
    const relCurso = /^(sim|true|1|yes)$/i.test(String(dados.relacao_com_curso || '').trim());
    const dataISO = (() => {
      const s = String(dados.data_conclusao || '').trim();
      if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s;
      const m = s.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
      return m ? `${m[3]}-${m[2]}-${m[1]}` : null;
    })();
    const dataConclusao = dataISO ? new Date(`${dataISO}T12:00:00.000Z`) : null;

    // Cria o registro inicialmente como PENDENTE
    const certificado = await prisma.certificado.create({
      data: {
        titulo: dados.titulo || 'Certificado',
        tipoAtividade: dados.tipo_certificado || 'Desconhecido',
        dataEnvio: new Date(),
        horasAtribuidas: horas,
        urlPDF: `http://localhost:3000/uploads/${file.filename}`,
        status: STATUS.PENDENTE,
        userId: user.id,
        instituicao: dados.instituicao || null,
        semestre: dados.semestre || null,
        relacaoComCurso: relCurso,
        nomeNoCertificado: dados.nome || null,
        extraidoRaw: dados,
        dataConclusao,
        fileHashSHA256,
      },
    });

    // Valida com o AGENTE (OCR ativo no primeiro passo)
    const result = await validateWithAgent(certificado.id, { skipOCR: false });

    // Atualiza status conforme resposta do agente e responde ao front
    if (result.status === STATUS.ACEITO) {
      const atualizado = await prisma.certificado.update({
        where: { id: certificado.id },
        data: { status: STATUS.ACEITO },
      });
      return res.status(201).json({
        message: 'Certificado cadastrado com sucesso!',
        certificado: atualizado,
      });
    }

    if (result.status === STATUS.RECUSADO) {
      // remove para não aparecer em lugar nenhum
      await prisma.certificado.delete({ where: { id: certificado.id } });
      return res.status(400).json({
        message: `Não foi possível cadastrar o certificado devido a: ${result.justificativa || 'motivo não informado'}`,
      });
    }

    if (result.status === STATUS.AJUSTAR) {
      // mantém PENDENTE e solicita complementação
      const uniq = Array.from(new Set(result.campos_faltantes || []));
      await prisma.certificado.update({
        where: { id: certificado.id },
        data: { status: STATUS.AJUSTAR },
      });
      return res.status(202).json({
        message: `As seguintes informações são necessárias para o cadastro do certificado: ${(result.campos_faltantes || []).join(', ')}`,
        needsInfo: true,
        requiredFields: uniq,
        certificadoId: certificado.id,
      });
    }

    return res.status(500).json({ error: 'Resposta inesperada do agente' });
  } catch (error) {
    console.error('Erro no upload/validação:', error?.response?.data || error.message);
    res.status(500).json({ error: 'Erro interno ao salvar/validar certificado' });
  }
});

/* =====================================================
 *    COMPLEMENTO DE INFORMAÇÕES (pula OCR no agente)
 * ===================================================== */
app.post('/certificados/:id/complementar', async (req, res) => {
  const { id } = req.params;
  const { complemento } = req.body; // { campo: valor, ... }

  if (!complemento || typeof complemento !== 'object') {
    return res.status(400).json({ error: 'Envie um objeto "complemento" com os campos faltantes.' });
  }

  try {
    const cert = await prisma.certificado.findUnique({ where: { id } });
    if (!cert) return res.status(404).json({ error: 'Certificado não encontrado' });

    // Merge em extraidoRaw
    const novoRaw = { ...(cert.extraidoRaw || {}), ...complemento };

    // Se vier campos top-level, refletir nos campos principais também
    const patch = { extraidoRaw: novoRaw };
    if (complemento.titulo) patch.titulo = String(complemento.titulo);
    if (complemento.tipoAtividade || complemento.tipo_certificado)
      patch.tipoAtividade = String(complemento.tipoAtividade || complemento.tipo_certificado);
    if (complemento.horasAtribuidas || complemento.quantidade_horas)
      patch.horasAtribuidas = parseInt(complemento.horasAtribuidas || complemento.quantidade_horas, 10) || 0;
    if (complemento.nome || complemento.nomeNoCertificado)
      patch.nomeNoCertificado = String(complemento.nome || complemento.nomeNoCertificado);
    if (complemento.instituicao) patch.instituicao = String(complemento.instituicao);

    if (complemento.dataConclusao || complemento.data_conclusao) {
      const raw = String(complemento.dataConclusao || complemento.data_conclusao);
      const iso =
        /^\d{4}-\d{2}-\d{2}$/.test(raw)
          ? raw
          : (raw.match(/^(\d{2})\/(\d{2})\/(\d{4})$/) ? `${raw.slice(6, 10)}-${raw.slice(3, 5)}-${raw.slice(0, 2)}` : null);
      if (iso) patch.dataConclusao = new Date(`${iso}T12:00:00.000Z`);
    }

    await prisma.certificado.update({ where: { id }, data: patch });

    // Chama agente SEM OCR
    const result = await validateWithAgent(id, { skipOCR: true });

    if (result.status === STATUS.ACEITO) {
      const atualizado = await prisma.certificado.update({
        where: { id },
        data: { status: STATUS.ACEITO },
      });
      return res.status(200).json({
        message: 'Certificado cadastrado com sucesso!',
        certificado: atualizado,
      });
    }

    if (result.status === STATUS.RECUSADO) {
      await prisma.certificado.delete({ where: { id } });
      return res.status(400).json({
        message: `Não foi possível cadastrar o certificado devido a: ${result.justificativa || 'motivo não informado'}`,
      });
    }

    if (result.status === STATUS.AJUSTAR) {
      const uniq = Array.from(new Set(result.campos_faltantes || []));
      await prisma.certificado.update({
        where: { id },
        data: { status: STATUS.AJUSTAR },
      });
      return res.status(202).json({
        message: `Ainda faltam informações: ${(result.campos_faltantes || []).join(', ')}`,
        needsInfo: true,
        requiredFields: uniq,
        certificadoId: id,
      });
    }

    return res.status(500).json({ error: 'Resposta inesperada do agente' });
  } catch (error) {
    console.error('Erro ao complementar informações:', error);
    res.status(500).json({ error: 'Erro interno ao complementar informações' });
  }
});

/* =====================================================
 *        ROTAS ADICIONAIS / UTILITÁRIAS
 * ===================================================== */

// Cadastro manual (sem upload)
app.post('/certificados', async (req, res) => {
  const { ra, titulo, tipoAtividade, dataEnvio, horasAtribuidas, urlPDF, status } = req.body;
  try {
    const user = await prisma.user.findUnique({ where: { ra } });
    if (!user) return res.status(404).json({ error: 'Usuário não encontrado' });

    const statusValido = Object.values(STATUS).includes(status) ? status : STATUS.PENDENTE;

    const certificado = await prisma.certificado.create({
      data: {
        titulo,
        tipoAtividade,
        dataEnvio: new Date(dataEnvio),
        horasAtribuidas,
        urlPDF,
        status: statusValido,
        userId: user.id,
      },
    });

    res.status(201).json(certificado);
  } catch (error) {
    console.error('Erro ao adicionar certificado:', error);
    res.status(500).json({ error: 'Erro interno ao adicionar certificado' });
  }
});

// Remover certificado
app.delete('/certificados/:id', async (req, res) => {
  try {
    const { id } = req.params;
    await prisma.certificado.delete({ where: { id } });
    res.status(200).json({ message: 'Certificado removido com sucesso.' });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Erro ao remover certificado.' });
  }
});

// Busca (admin / coord)
app.get('/certificados/busca', async (req, res) => {
  const { filtro, valor } = req.query;
  if (!filtro || !valor) return res.status(400).json({ error: 'Parâmetros inválidos' });

  try {
    let usuario = null;
    let certificados = [];

    if (filtro === 'ra' || filtro === 'name') {
      usuario = await prisma.user.findFirst({
        where: { [filtro]: { contains: valor, mode: 'insensitive' } },
        include: { certificados: true },
      });
      if (usuario) certificados = usuario.certificados;
    } else if (filtro === 'tipoAtividade' || filtro === 'titulo') {
      const resultado = await prisma.certificado.findMany({
        where: { [filtro]: { contains: valor, mode: 'insensitive' } },
        include: { user: true },
      });
      if (resultado.length > 0) {
        usuario = resultado[0].user;
        certificados = resultado;
      }
    }

    if (!usuario || certificados.length === 0) {
      return res.status(404).json({ error: 'Nenhum resultado encontrado' });
    }
    res.json({ usuario, certificados });
  } catch (error) {
    console.error('Erro ao buscar certificados:', error);
    res.status(500).json({ error: 'Erro interno no servidor' });
  }
});

// Duplicatas fortes
app.get('/certificados/duplicatas', async (req, res) => {
  const { hash, excludeId } = req.query;
  if (!hash) return res.status(400).json({ error: 'Parâmetro "hash" é obrigatório' });

  try {
    const where = { fileHashSHA256: hash, ...(excludeId ? { NOT: { id: String(excludeId) } } : {}) };
    const duplicatas = await prisma.certificado.findMany({
      where,
      select: {
        id: true,
        userId: true,
        instituicao: true,
        nomeNoCertificado: true,
        dataConclusao: true,
        horasAtribuidas: true,
        titulo: true,
        tipoAtividade: true,
      },
    });
    res.status(200).json(duplicatas);
  } catch (error) {
    console.error('Erro ao buscar duplicatas:', error);
    res.status(500).json({ error: 'Erro interno no servidor' });
  }
});

// Util p/ janela de datas
function makeDateWindowCenter(dateStr) {
  if (!dateStr) return null;
  const dt = new Date(`${dateStr}T12:00:00.000Z`);
  if (isNaN(dt.getTime())) return null;
  const start = new Date(dt);
  start.setUTCDate(start.getUTCDate() - 90);
  const end = new Date(dt);
  end.setUTCDate(end.getUTCDate() + 90);
  return { start, end };
}

// Similares (anti-duplicidade fraca)
app.get('/certificados/similares', async (req, res) => {
  let { instituicao, nome, data, horas } = req.query;
  if (!instituicao && !nome && !data && !horas) {
    return res.status(400).json({ error: 'Forneça ao menos um parâmetro: instituicao|nome|data|horas' });
  }

  try {
    const OR = [];
    if (instituicao && String(instituicao).trim()) {
      OR.push({ instituicao: { contains: String(instituicao).trim(), mode: 'insensitive' } });
    }
    if (nome && String(nome).trim()) {
      OR.push({ nomeNoCertificado: { contains: String(nome).trim(), mode: 'insensitive' } });
    }
    const win = makeDateWindowCenter(data);
    if (win) OR.push({ dataConclusao: { gte: win.start, lte: win.end } });
    if (horas && !Number.isNaN(Number(horas))) OR.push({ horasAtribuidas: Number(horas) });

    if (OR.length === 0) {
      return res.status(400).json({ error: 'Parâmetros inválidos (nenhum filtro utilizável)' });
    }

    const candidatos = await prisma.certificado.findMany({
      where: { OR },
      select: {
        id: true,
        userId: true,
        instituicao: true,
        nomeNoCertificado: true,
        dataConclusao: true,
        horasAtribuidas: true,
        titulo: true,
        tipoAtividade: true,
        fileHashSHA256: true,
      },
      take: 120,
    });

    res.status(200).json(candidatos);
  } catch (error) {
    console.error('Erro ao buscar similares:', error);
    res.status(500).json({ error: 'Erro interno no servidor' });
  }
});

// Certificado por ID
app.get('/certificados/:id', async (req, res) => {
  const { id } = req.params;
  try {
    const cert = await prisma.certificado.findUnique({
      where: { id },
      include: { user: true },
    });
    if (!cert) return res.status(404).json({ error: 'Certificado não encontrado' });
    res.status(200).json(cert);
  } catch (error) {
    console.error('Erro ao buscar certificado por ID:', error);
    res.status(500).json({ error: 'Erro interno no servidor' });
  }
});

// Atualizador de status (utilitário interno)
async function setStatusCertificado(id, status) {
  return prisma.certificado.update({ where: { id }, data: { status } });
}

// (Rotas admin opcionais)
app.put('/certificados/:id/aceitar', async (req, res) => {
  const { id } = req.params;
  try {
    const cert = await setStatusCertificado(id, STATUS.ACEITO);
    res.status(200).json({ message: 'Certificado aceito.', certificado: cert });
  } catch (error) {
    console.error('Erro ao aceitar certificado:', error);
    res.status(500).json({ message: 'Erro ao aceitar certificado.' });
  }
});
app.put('/certificados/:id/recusar', async (req, res) => {
  const { id } = req.params;
  try {
    const cert = await setStatusCertificado(id, STATUS.RECUSADO);
    res.status(200).json({ message: 'Certificado recusado.', certificado: cert });
  } catch (error) {
    console.error('Erro ao recusar certificado:', error);
    res.status(500).json({ message: 'Erro ao recusar certificado.' });
  }
});
app.put('/certificados/:id/ajustar', async (req, res) => {
  const { id } = req.params;
  try {
    const cert = await setStatusCertificado(id, STATUS.AJUSTAR);
    res.status(200).json({ message: 'Certificado marcado para ajuste.', certificado: cert });
  } catch (error) {
    console.error('Erro ao ajustar certificado:', error);
    res.status(500).json({ message: 'Erro ao ajustar certificado.' });
  }
});

// Auditoria do agente
app.post('/auditoria', async (req, res) => {
  try {
    const { certificadoId, status, reason, evidence, stateSnap } = req.body;

    if (!certificadoId || !status || !reason) {
      return res.status(400).json({ error: 'certificadoId, status e reason são obrigatórios' });
    }
    if (!Object.values(STATUS).includes(status)) {
      return res.status(400).json({ error: 'status inválido' });
    }

    const exists = await prisma.certificado.findUnique({ where: { id: certificadoId } });
    if (!exists) return res.status(404).json({ error: 'Certificado não encontrado' });

    const log = await prisma.auditLog.create({
      data: {
        certificadoId,
        status,
        reason,
        evidence: evidence ?? [],
        stateSnap: stateSnap ?? null,
      },
    });

    res.status(201).json(log);
  } catch (error) {
    console.error('Erro ao salvar auditoria:', error);
    res.status(500).json({ error: 'Erro interno ao salvar auditoria' });
  }
});

// Issuer (cache simples)
app.get('/issuer', async (req, res) => {
  const name = String(req.query.name || '').trim();
  if (!name) return res.status(400).json({ error: 'name obrigatório' });
  const it = await prisma.issuer.findFirst({ where: { name: { equals: name, mode: 'insensitive' } } });
  res.json(it);
});
app.post('/issuer', async (req, res) => {
  const { name, isTrusted, trustLevel, notes } = req.body;
  if (!name) return res.status(400).json({ error: 'name obrigatório' });
  const it = await prisma.issuer.upsert({
    where: { name },
    update: { isTrusted: !!isTrusted, trustLevel: Number(trustLevel || 0), notes },
    create: { name, isTrusted: !!isTrusted, trustLevel: Number(trustLevel || 0), notes },
  });
  res.status(201).json(it);
});

/* =====================================================
 *          CHAMADA AO AGENTE (com skipOCR)
 * ===================================================== */
async function validateWithAgent(certId, { skipOCR = false } = {}) {
  const t0 = Date.now();
  try {
    const { data } = await axios.post(
      `${AGENT_BASE}/validate`,
      { cert_id: certId, skip_ocr: !!skipOCR },
      { headers: AGENT_API_KEY ? { 'X-Agent-Key': AGENT_API_KEY } : {}, timeout: 90_000 }
    );

    console.log('\n==== DocVerifier/Agent ====');
    console.log(`cert_id: ${certId}`);
    console.log(`skip_ocr: ${!!skipOCR}`);
    console.log(`status : ${data.status}`);
    console.log(`motivo : ${data.justificativa}`);
    const evids = Array.isArray(data.evidencias) ? data.evidencias.slice(0, 6) : [];
    if (evids.length) {
      console.log('evidências (top):');
      for (const ev of evids) {
        const campo = ev.campo ? ` [${ev.campo}]` : '';
        const score = ev.score != null ? ` (${ev.score})` : '';
        const snippet = (ev.snippet ?? ev.sub ?? ev.modo ?? '').toString().slice(0, 120);
        console.log(` - ${ev.tipo}${campo}${score} :: ${snippet}`);
      }
    }
    console.log(`tempo  : ${Date.now() - t0} ms`);
    console.log('===========================\n');

    return data; // {status, justificativa, evidencias, campos_faltantes?}
  } catch (err) {
    const payload = err?.response?.data ?? err.message ?? String(err);
    console.error('[Agent] falha ao validar:', payload);
    throw err;
  }
}

/* =========================
 *       BOOT DO APP
 * ========================= */
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
