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

// Configuração do multer
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadPath),
  filename: (req, file, cb) => cb(null, Date.now() + '-' + file.originalname)
});
const upload = multer({ storage });

// Middlewares
app.use(express.json());
app.use(cors());
app.use('/uploads', express.static(uploadPath));

// Rotas de usuários
app.post('/usuarios', async (req, res) => {
  try {
    const user = await prisma.user.create({ data: req.body });
    res.status(201).json(user);
  } catch (error) {
    console.error('Erro ao criar usuário:', error);
    res.status(500).json({ error: 'Erro ao criar usuário' });
  }
});

app.get('/usuarios', async (req, res) => {
  const users = await prisma.user.findMany();
  res.status(200).json(users);
});

// Login
app.post('/login', async (req, res) => {
  const { ra, password } = req.body;
  try {
    const user = await prisma.user.findUnique({ where: { ra } });
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

// Certificados por RA
app.get('/usuarios/:ra/certificados', async (req, res) => {
  const { ra } = req.params;
  try {
    const user = await prisma.user.findUnique({
      where: { ra },
      include: { certificados: true }
    });
    if (!user) return res.status(404).json({ error: 'Usuário não encontrado' });
    res.status(200).json(user.certificados);
  } catch (error) {
    console.error('Erro ao buscar certificados:', error);
    res.status(500).json({ error: 'Erro interno no servidor' });
  }
});

// Cadastro de certificado (upload + IA + Prisma)
app.post('/certificados/upload', upload.single('arquivo'), async (req, res) => {
  const { ra } = req.body;
  const file = req.file;

  if (!file) return res.status(400).json({ error: 'Arquivo não enviado' });

  try {
    const user = await prisma.user.findUnique({ where: { ra } });
    if (!user) return res.status(404).json({ error: 'Usuário não encontrado' });

    // 1. Executa a IA para extrair os dados do certificado
    const scriptPath = path.join(__dirname, '..', '..', 'IA', 'main.py');
    const caminhoPDF = path.join(uploadPath, file.filename);
    const nomeAluno = user.name || 'Aluno Desconhecido';

    const buffer = await fs.promises.readFile(caminhoPDF);
    const fileHashSHA256 = crypto.createHash('sha256').update(buffer).digest('hex');

    const { stdout, stderr } = await execPromise(
      `python "${scriptPath}" "${caminhoPDF}" "${nomeAluno}"`
    );
    if (stderr) console.error('Erro da IA:', stderr);

    let resultadoIA;
    try {
      resultadoIA = JSON.parse(stdout);
      // console.log('Resultado da IA:', resultadoIA);
    } catch (e) {
      return res.status(500).json({ error: 'Erro ao interpretar resultado da IA' });
    }

    if (!resultadoIA || (Array.isArray(resultadoIA) && resultadoIA.length === 0)) {
      return res.status(400).json({ error: 'IA não retornou dados de extração' });
    }

    // console.log("Tipo de resultadoIA:", Array.isArray(resultadoIA) ? "Array" : typeof resultadoIA);
    console.log("Dados IA:", resultadoIA);
    // console.log("dados.tipo_certificado:", resultadoIA[0]?.tipo_certificado);

    // 2. Salva os dados extraídos no banco (usando Prisma)
    const dados = Array.isArray(resultadoIA) ? resultadoIA[0] : resultadoIA;

    // Normalizações mínimas
    const horas = parseInt(dados.quantidade_horas || '0', 10) || 0;
    const relCurso = /^(sim|true|1|yes)$/i.test(String(dados.relacao_com_curso || '').trim());
    const dataISO = (() => {
      const s = String(dados.data_conclusao || '').trim();
      if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s;                 // "2023-10-20"
      const m = s.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);            // "20/10/2023"
      return m ? `${m[3]}-${m[2]}-${m[1]}` : null;
    })();
    const dataConclusao = dataISO ? new Date(`${dataISO}T12:00:00.000Z`) : null; // evita problema de fuso

    const certificado = await prisma.certificado.create({
      data: {
        titulo: dados.titulo || 'Certificado',
        tipoAtividade: dados.tipo_certificado || 'Desconhecido',
        dataEnvio: new Date(), // Data atual do upload
        horasAtribuidas: horas,
        urlPDF: `http://localhost:3000/uploads/${file.filename}`,
        status: 'Pendente',
        userId: user.id,
        instituicao: dados.instituicao || null,
        semestre: dados.semestre || null,
        relacaoComCurso: relCurso,
        nomeNoCertificado: dados.nome || null,
        extraidoRaw: dados,
        dataConclusao: dataConclusao,
        fileHashSHA256: fileHashSHA256
      }
    });

    // 3. Retorna o certificado salvo para o front
    res.status(201).json(certificado);
  } catch (error) {
    console.error('Erro ao salvar certificado:', error);
    res.status(500).json({ error: 'Erro interno ao salvar certificado' });
  }
});


// Cadastro de certificado (sem upload)
app.post('/certificados', async (req, res) => {
  const {
    ra, titulo, tipoAtividade,
    dataEnvio, horasAtribuidas, urlPDF, status
  } = req.body;
  try {
    const user = await prisma.user.findUnique({ where: { ra } });
    if (!user) return res.status(404).json({ error: 'Usuário não encontrado' });

    const certificado = await prisma.certificado.create({
      data: {
        titulo,
        tipoAtividade,
        dataEnvio: new Date(dataEnvio),
        horasAtribuidas,
        urlPDF,
        status,
        userId: user.id
      }
    });

    res.status(201).json(certificado);
  } catch (error) {
    console.error('Erro ao adicionar certificado:', error);
    res.status(500).json({ error: 'Erro interno ao adicionar certificado' });
  }
});

// Aprovar certificado
app.put('/certificados/:id/aprovar', async (req, res) => {
  try {
    const { id } = req.params;
    await prisma.certificado.update({
      where: { id },
      data: { status: 'Aprovado' }
    });
    res.status(200).json({ message: 'Certificado aprovado.' });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Erro ao aprovar certificado.' });
  }
});

// Rejeitar (excluir) certificado
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

// Certificados para validação (coordenador)
app.get('/certificados/validacao', async (req, res) => {
  try {
    const alunos = await prisma.user.findMany({
      where: { tipo: 'aluno' },
      include: { certificados: true }
    });
    res.status(200).json(alunos);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Erro ao buscar dados para validação' });
  }
});

// GET /certificados/busca
app.get('/certificados/busca', async (req, res) => {
  const { filtro, valor } = req.query;

  if (!filtro || !valor) {
    return res.status(400).json({ error: 'Parâmetros inválidos' });
  }

  try {
    let usuario = null;
    let certificados = [];

    if (filtro === 'ra' || filtro === 'name') {
      usuario = await prisma.user.findFirst({
        where: {
          [filtro]: {
            contains: valor,
            mode: 'insensitive'
          }
        },
        include: { certificados: true }
      });

      if (usuario) certificados = usuario.certificados;
    } else if (filtro === 'tipoAtividade' || filtro === 'titulo') {
      // Busca em todos os usuários que têm certificados correspondentes
      const resultado = await prisma.certificado.findMany({
        where: {
          [filtro]: {
            contains: valor,
            mode: 'insensitive'
          }
        },
        include: { user: true }
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



// Inicia servidor
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
