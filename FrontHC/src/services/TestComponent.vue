<script lang="ts">
import { ref, onMounted } from 'vue';
import { getTestMessage } from '@/services/api';

const message = ref('');

onMounted(async () => {
    try {
        const data = await getTestMessage();
        message.value = data.message;
    } catch (error) {
        message.value = 'Erro ao conectar com o backend!';
    }
});
</script>

<template>
    <div>
        <h2>Teste de Conexao</h2>
        <p>{{ message }}</p>
    </div>
</template>