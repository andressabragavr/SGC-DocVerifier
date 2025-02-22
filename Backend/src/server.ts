import Fastify from 'fastify';
import cors from '@fastify/cors';
import { routes } from './routes';
import { chmod } from 'fs';
import express, { Request, Response } from "express";

const app = express();
const PORT = 3000;

// Middleware para permitir JSON
app.use(express.json());

// Rota simples
app.get("/", (req: Request, res: Response) => {
  res.send("Hello, Express com TypeScript!");
});

// Iniciar o servidor
app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});

//const app = Fastify({logger: true})

//const start = async () => {

   // await app.register(cors)
   // await app.register(routes);    

  //  try{
  //      await app.listen({port: 3333})
  //  }catch(err){
  //   process.exit(1)
  //  }
//}

//xstart();