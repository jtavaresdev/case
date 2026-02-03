<template>
    <div>
        <button @click="$router.push('/')" class="btn-back">← Voltar</button>

        <div v-if="loading" class="loading">
            <div class="spinner"></div>
            Carregando detalhes...
        </div>

        <div v-else-if="error" class="error">⚠️ {{ error }}</div>

        <div v-else-if="operadora" class="detail-container">
            <div class="card">
                <h2>{{ operadora.razao_social }}</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>CNPJ:</strong>
                        <span>{{ formatCNPJ(operadora.cnpj) }}</span>
                    </div>
                    <div class="info-item">
                        <strong>Registro ANS:</strong>
                        <span>{{ operadora.registro_ans }}</span>
                    </div>
                    <div class="info-item">
                        <strong>UF:</strong>
                        <span>{{ operadora.uf }}</span>
                    </div>
                    <div class="info-item">
                        <strong>Modalidade:</strong>
                        <span>{{ operadora.modalidade }}</span>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>Histórico de Despesas</h3>

                <div v-if="operadora.despesas && operadora.despesas.length > 0">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Ano</th>
                                <th>Trimestre</th>
                                <th>Valor (R$)</th>
                                <th>Descrição</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr
                                v-for="(desp, idx) in operadora.despesas"
                                :key="idx"
                            >
                                <td>{{ desp.ano }}</td>
                                <td>{{ desp.trimestre }}º Trimestre</td>
                                <td>
                                    R$ {{ formatNumber(desp.valor_despesas) }}
                                </td>
                                <td>{{ desp.descricao || "-" }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div v-else class="empty-state">Nenhuma despesa registrada</div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";

const route = useRoute();
const operadora = ref(null);
const loading = ref(false);
const error = ref(null);

const loadOperadora = async () => {
    loading.value = true;
    error.value = null;

    try {
        const cnpj = route.params.cnpj;
        const response = await axios.get(`/api/operadoras/${cnpj}/despesas`);
        operadora.value = response.data;
    } catch (err) {
        error.value = "Operadora não encontrada ou erro ao carregar dados";
        console.error(err);
    } finally {
        loading.value = false;
    }
};

const formatCNPJ = (cnpj) => {
    if (!cnpj) return "";
    return cnpj.replace(
        /^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,
        "$1.$2.$3/$4-$5",
    );
};

const formatNumber = (value) => {
    return parseFloat(value).toLocaleString("pt-BR", {
        minimumFractionDigits: 2,
    });
};

onMounted(() => {
    loadOperadora();
});
</script>

<style scoped>
.btn-back {
    padding: 0.75rem 1.5rem;
    background: #64748b;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    margin-bottom: 1.5rem;
    font-size: 1rem;
}

.btn-back:hover {
    background: #475569;
}

.detail-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.card {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card h2 {
    color: #1e293b;
    margin-bottom: 1.5rem;
}

.card h3 {
    color: #475569;
    margin-bottom: 1rem;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.info-item strong {
    color: #64748b;
    font-size: 0.875rem;
}

.info-item span {
    color: #1e293b;
    font-size: 1rem;
}

.loading {
    text-align: center;
    padding: 3rem;
    color: #64748b;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #e2e8f0;
    border-top-color: #2563eb;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.error {
    background: #fee;
    color: #c00;
    padding: 1.5rem;
    border-radius: 6px;
    text-align: center;
}

.table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
}

.table th {
    background: #f8fafc;
    padding: 0.75rem;
    text-align: left;
    font-weight: 600;
    color: #475569;
    border-bottom: 2px solid #e2e8f0;
}

.table td {
    padding: 0.75rem;
    border-bottom: 1px solid #e2e8f0;
}

.empty-state {
    text-align: center;
    padding: 2rem;
    color: #64748b;
}
</style>
