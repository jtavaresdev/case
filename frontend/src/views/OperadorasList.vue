<template>
    <div>
        <h2>Operadoras de Saúde</h2>

        <div class="search-box">
            <input
                v-model="search"
                @input="handleSearch"
                placeholder="Buscar por razão social ou CNPJ..."
                class="search-input"
            />
        </div>

        <div class="chart-container">
            <h3>Distribuição de Despesas por UF</h3>
            <canvas ref="chartCanvas"></canvas>
        </div>

        <div v-if="loading" class="loading">
            <div class="spinner"></div>
            Carregando...
        </div>

        <div v-else-if="error" class="error">
            ⚠️ {{ error }}
            <button @click="loadOperadoras" class="btn-retry">
                Tentar novamente
            </button>
        </div>

        <div v-else-if="operadoras.length > 0" class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>CNPJ</th>
                        <th>Razão Social</th>
                        <th>UF</th>
                        <th>Modalidade</th>
                        <th>Total Despesas</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="op in operadoras" :key="op.cnpj">
                        <td>{{ formatCNPJ(op.cnpj) }}</td>
                        <td>{{ op.razao_social }}</td>
                        <td>{{ op.uf }}</td>
                        <td>{{ op.modalidade }}</td>
                        <td>R$ {{ formatNumber(op.total_despesas) }}</td>
                        <td>
                            <router-link
                                :to="`/operadora/${op.cnpj}`"
                                class="btn-view"
                            >
                                Ver Detalhes
                            </router-link>
                        </td>
                    </tr>
                </tbody>
            </table>

            <div class="pagination">
                <button
                    @click="changePage(page - 1)"
                    :disabled="page === 1"
                    class="btn-page"
                >
                    ← Anterior
                </button>
                <span>Página {{ page }} de {{ totalPages }}</span>
                <button
                    @click="changePage(page + 1)"
                    :disabled="page === totalPages"
                    class="btn-page"
                >
                    Próxima →
                </button>
            </div>
        </div>

        <div v-else class="empty-state">
            <p>📋 Nenhuma operadora encontrada</p>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { Chart } from "chart.js/auto";
import axios from "axios";

const operadoras = ref([]);
const loading = ref(false);
const error = ref(null);
const search = ref("");
const page = ref(1);
const totalPages = ref(1);
const chartCanvas = ref(null);
let chartInstance = null;
let searchTimeout = null;

const loadOperadoras = async () => {
    loading.value = true;
    error.value = null;

    try {
        const response = await axios.get("/api/operadoras", {
            params: {
                page: page.value,
                limit: 20,
                search: search.value || undefined,
            },
        });

        operadoras.value = response.data.data;
        totalPages.value = response.data.total_pages;
    } catch (err) {
        error.value =
            "Erro ao carregar operadoras. Verifique se a API está rodando.";
        console.error(err);
    } finally {
        loading.value = false;
    }
};

const loadChart = async () => {
    try {
        const response = await axios.get("/api/estatisticas");
        const top5 = response.data.top_5_operadoras;

        if (chartInstance) {
            chartInstance.destroy();
        }

        const ctx = chartCanvas.value.getContext("2d");
        chartInstance = new Chart(ctx, {
            type: "bar",
            data: {
                labels: top5.map((item) => item.uf),
                datasets: [
                    {
                        label: "Total de Despesas (R$)",
                        data: top5.map((item) =>
                            parseFloat(item.total_despesas),
                        ),
                        backgroundColor: "#2563eb",
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            },
        });
    } catch (err) {
        console.error("Erro ao carregar gráfico:", err);
    }
};

const handleSearch = () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        page.value = 1;
        loadOperadoras();
    }, 500);
};

const changePage = (newPage) => {
    page.value = newPage;
    loadOperadoras();
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
    loadOperadoras();
    loadChart();
});
</script>

<style scoped>
h2 {
    margin-bottom: 1.5rem;
    color: #1e293b;
}

.search-box {
    margin-bottom: 2rem;
}

.search-input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 1rem;
}

.search-input:focus {
    outline: none;
    border-color: #2563eb;
}

.chart-container {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-container h3 {
    margin-bottom: 1rem;
    color: #475569;
}

.chart-container canvas {
    height: 300px !important;
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

.btn-retry {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background: #dc2626;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.table-container {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table {
    width: 100%;
    border-collapse: collapse;
}

.table th {
    background: #f8fafc;
    padding: 1rem;
    text-align: left;
    font-weight: 600;
    color: #475569;
    border-bottom: 2px solid #e2e8f0;
}

.table td {
    padding: 1rem;
    border-bottom: 1px solid #e2e8f0;
}

.table tbody tr:hover {
    background: #f8fafc;
}

.btn-view {
    padding: 0.5rem 1rem;
    background: #2563eb;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    font-size: 0.875rem;
}

.btn-view:hover {
    background: #1d4ed8;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem;
}

.btn-page {
    padding: 0.5rem 1rem;
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.btn-page:disabled {
    background: #cbd5e1;
    cursor: not-allowed;
}

.empty-state {
    text-align: center;
    padding: 3rem;
    color: #64748b;
    font-size: 1.125rem;
}
</style>
