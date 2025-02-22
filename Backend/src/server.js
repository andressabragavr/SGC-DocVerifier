"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const app = (0, express_1.default)();
const PORT = 3000;
// Middleware para permitir JSON
app.use(express_1.default.json());
// Rota simples
app.get("/", (req, res) => {
    res.send("Salve clã!");
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
