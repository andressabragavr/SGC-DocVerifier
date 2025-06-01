// index.js
import express from 'express';
import cors from 'cors';
import { PrismaClient } from '@prisma/client';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const app = express();
const PORT = 3000;
const prisma = new PrismaClient();

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

// Cadastro de certificado (upload)
app.post('/certificados/upload', upload.single('arquivo'), async (req, res) => {
  const {
    ra, titulo, categoria, tipoAtividade,
    dataEnvio, horasAtribuidas, status
  } = req.body;
  const file = req.file;
  if (!file) return res.status(400).json({ error: 'Arquivo não enviado' });

  try {
    const user = await prisma.user.findUnique({ where: { ra } });
    if (!user) return res.status(404).json({ error: 'Usuário não encontrado' });

    const certificado = await prisma.certificado.create({
      data: {
        titulo,
        categoria,
        tipoAtividade,
        dataEnvio: new Date(dataEnvio),
        horasAtribuidas: parseInt(horasAtribuidas),
        urlPDF: `http://localhost:3000/uploads/${file.filename}`,
        status,
        userId: user.id
      }
    });

    res.status(201).json(certificado);
  } catch (error) {
    console.error('Erro ao salvar certificado:', error);
    res.status(500).json({ error: 'Erro interno ao salvar certificado' });
  }
});

// Cadastro de certificado (sem upload)
app.post('/certificados', async (req, res) => {
  const {
    ra, titulo, categoria, tipoAtividade,
    dataEnvio, horasAtribuidas, urlPDF, status
  } = req.body;
  try {
    const user = await prisma.user.findUnique({ where: { ra } });
    if (!user) return res.status(404).json({ error: 'Usuário não encontrado' });

    const certificado = await prisma.certificado.create({
      data: {
        titulo,
        categoria,
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
