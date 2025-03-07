import axios from "axios";
import api from "./api";

api.get("/usuarios")
  .then(response => console.log(response.data))
  .catch(error => console.error("Erro:", error));


const api = axios.create({
  baseURL: "http://localhost:3000", // URL do seu back-end
  timeout: 5000, // Tempo limite da requisição
  headers: { "Content-Type": "application/json" }
});

export default api;
