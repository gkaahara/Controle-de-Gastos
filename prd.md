# PRD — App de Controle de Gastos

## 1. Vision & Overview

Aplicação web para controle de gastos residenciais com suporte a múltiplas fontes de renda, cartões de crédito, divisão proporcional de despesas e dashboards mensais. Desenvolvida em Flask com armazenamento em JSON.

## 2. Problem Definition

Famílias com múltiplas fontes de renda e despesas compartilhadas (casa, cartão de crédito) enfrentam dificuldade em:
- Rastrear gastos por categoria
- Dividir contas proporcionalmente à renda de cada membro
- Visualizar resumo mensal de forma consolidada
- Controlar faturas de cartão de crédito

## 3. Product Objectives

- MVP funcional em Flask com persistência JSON
- Cadastro estruturado de categorias, gastos, salários e cartões
- Divisão proporcional automática baseada em salários
- Dashboard mensal e relatórios por categoria
- Zero dependência de banco de dados externo (JSON-only)

## 4. Architecture Overview

```
[Flask App] → [JSON File Store] → [Local Filesystem]
     ↑
[HTML/CSS/JS Frontend (Jinja2)]
```

- Backend: Flask (Python 3)
- Persistência: Arquivos JSON no filesystem
- Frontend: Server-side rendering com Jinja2 + vanilla JS
- Cálculos: Regra de três baseada em proporção salarial

## 5. Functional Requirements

### FR-01: Cadastro de Categorias (P3)
CRUD de categorias de gasto (ex: Alimentação, Transporte, Lazer).

### FR-02: Cadastro de Gastos da Casa (P4)
CRUD de despesas domésticas com valor, categoria, data, e responsável.

### FR-03: Cadastro de Gastos de Cartão de Crédito (P4)
CRUD de faturas com parcelamento, bandeira, vencimento.

### FR-04: Cadastro de Salários (P4)
Registro de renda de cada membro da casa para cálculo proporcional.

### FR-05: Divisão Proporcional (P5)
Cálculo automático de quanto cada membro deve pagar baseado na proporção salarial.

### FR-06: Dashboard / Resumo Mensal (P5)
Visão consolidada do mês: total gasto, por categoria, saldo restante.

### FR-07: Relatório por Categoria (P3)
Filtro e exibição de gastos agregados por categoria em período selecionado.

### FR-08: Modelo de Dados JSON (P5)
Estrutura de schemas JSON para persistência de todas as entidades.

## 6. Non-Functional Requirements

- **NFR-01**: Armazenamento 100% local em JSON (sem banco de dados)
- **NFR-02**: Interface responsiva (mobile-first)
- **NFR-03**: Tempo de resposta < 2s para operações CRUD
- **NFR-04**: Suporte a múltiplos membros na mesma casa
- **NFR-05**: Cálculos financeiros com precisão de 2 casas decimais

## 7. Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-01: Perda de dados JSON | Baixa | Alto | Backup manual automático |
| R-02: Concorrência de escrita | Média | Médio | Lock de arquivo |
| R-03: Escalabilidade JSON limitada | Baixa | Baixo | MVP aceita limite |
| R-04: Precisão em divisão proporcional | Baixa | Alto | Testes com valores quebrados |
| R-05: Complexidade de parcelamento | Média | Médio | Simplificar para parcelas fixas |
