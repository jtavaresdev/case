<template>
    <div class="app">
        <header class="header">
            <h1>ANS - Operadoras de Saúde</h1>
            <nav>
                <router-link to="/">Home</router-link>
            </nav>
        </header>
        <main class="main">
            <router-view />
        </main>
    </div>
</template>

<style scoped>
.app {
    min-height: 100vh;
}

.header {
    background: #2563eb;
    color: white;
    padding: 1.5rem 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header h1 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.header nav a {
    color: white;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
}

.header nav a:hover {
    background: rgba(255, 255, 255, 0.1);
}

.main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 2rem;
}
</style>
