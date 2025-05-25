// index.js
import express from 'express'
import cors from 'cors'
import { PrismaClient } from '@prisma/client';

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

app.put('/usuarios/:id', async (req, res) => {
    await prisma.user.update({
        where: {
            id: req.params.id
        },
        data: {
            email: req.body.email,
            name: req.body.name,
            age: req.body.age
        }
    })
    res.status(201).json(req.body)
})

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
