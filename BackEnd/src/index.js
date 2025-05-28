// index.js
import express from 'express'
import cors from 'cors'
import { PrismaClient } from '@prisma/client';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const PORT = 3000
const prisma = new PrismaClient();
const app = express()

app.use(express.json())
app.use(cors()) // ✅ Aqui o CORS

app.post('/usuarios', async (req, res) => {
  const user = await prisma.user.create({
    data: {
      name: req.body.name,
      email: req.body.email,
      password: req.body.password,
      ra: req.body.ra
    }
  });

  res.status(201).json(user);
})


app.get('/usuarios', async(req, res) =>{
    const users = await prisma.user.findMany()
    res.status(200).json(users)
})

app.put('/certificados/:id', async (req, res) => {
  const { id } = req.params;

  try {
    const certificadoAtualizado = await prisma.certificado.update({
      where: { id },
      data: req.body
    });

    res.status(200).json(certificadoAtualizado);
  } catch (error) {
    console.error('Erro ao atualizar certificado:', error);
    res.status(500).json({ error: 'Erro interno ao atualizar certificado' });
  }
});

app.post('/login', async (req, res) => {
  const { ra, password } = req.body;

  try {
    const user = await prisma.user.findUnique({
      where: { ra }
    });

    if (!user || user.password !== password) {
      return res.status(401).json({ error: 'Credenciais inválidas' });
    }

    // Remove a senha da resposta
    const { password: _, ...userSemSenha } = user;

    res.status(200).json(userSemSenha);
  } catch (error) {
    console.error('Erro no login:', error);
    res.status(500).json({ error: 'Erro interno no login' });
  }
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

app.get('/usuarios/:ra/certificados', async (req, res) => {
  const { ra } = req.params;

  try {
    const user = await prisma.user.findUnique({
      where: { ra },
      include: { certificados: true } // nome do relacionamento no schema.prisma
    });

    if (!user) {
      return res.status(404).json({ error: 'Usuário não encontrado' });
    }

    res.status(200).json(user.certificados);
  } catch (error) {
    console.error('Erro ao buscar certificados:', error);
    res.status(500).json({ error: 'Erro interno no servidor' });
  }
});

app.post('/certificados', async (req, res) => {
  const {
    ra,
    titulo,
    categoria,
    tipoAtividade,
    dataEnvio,
    horasAtribuidas,
    urlPDF,
    status
  } = req.body;

  try {
    const user = await prisma.user.findUnique({ where: { ra } });

    if (!user) {
      return res.status(404).json({ error: 'Usuário com esse RA não encontrado' });
    }

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

// Cria pasta 'uploads' se não existir
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const uploadPath = path.join(__dirname, '..', 'uploads');
if (!fs.existsSync(uploadPath)) {
  fs.mkdirSync(uploadPath);
}

// Configuração do multer
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadPath);
  },
  filename: function (req, file, cb) {
    const uniqueName = Date.now() + '-' + file.originalname;
    cb(null, uniqueName);
  }
});
const upload = multer({ storage });

// Torna os arquivos acessíveis publicamente
app.use('/uploads', express.static(uploadPath));

// Rota para upload e cadastro
app.post('/certificados/upload', upload.single('arquivo'), async (req, res) => {
  const {
    ra,
    titulo,
    categoria,
    tipoAtividade,
    dataEnvio,
    horasAtribuidas,
    status
  } = req.body;

  const file = req.file;

  if (!file) {
    return res.status(400).json({ error: 'Arquivo não enviado' });
  }

  try {
    const user = await prisma.user.findUnique({ where: { ra } });

    if (!user) {
      return res.status(404).json({ error: 'Usuário não encontrado' });
    }

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