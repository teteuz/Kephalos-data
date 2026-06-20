<div align="center">

# KEPHALOS DATA

**A concise, universal collective intelligence engine for predictive simulation.**
<br/>
<em>A Simple and General Multi-Agent Prediction Platform — Rehearse the Future</em>

[![Docker](https://img.shields.io/badge/Docker-Build-2496ED?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/)
[![Discord](https://img.shields.io/badge/Discord-Join-5865F2?style=flat-square&logo=discord&logoColor=white)](http://discord.gg/ePf5aPaHnA)

</div>

## Project Overview

**KEPHALOS DATA** is a next-generation AI prediction engine powered by multi-agent simulation. It extracts seed information from reality (e.g., breaking news, policy drafts, financial signals) to build a high-fidelity parallel digital world. In that world, thousands of agents with independent personalities, long-term memory, and behavioral logic interact and evolve socially. You can inject variables from a "god-view" to precisely forecast trajectories — **rehearse the future in a digital sandbox and improve decision-making through repeated simulations**.

> You provide: seed materials (data reports, narrative scenarios, or other context) and a natural language prediction goal.
> KEPHALOS DATA returns: a detailed prediction report and an interactive high-fidelity simulated world

### Our Vision

KEPHALOS DATA aims to build a collective intelligence mirror of reality, capturing emergent behavior from individual interactions and breaking through traditional forecasting limits:

- **Macro**: a rehearsal lab for decision-makers to test policies and public strategies with zero risk
- **Micro**: a creative sandbox for individuals to explore scenarios — from narrative outcomes to imaginative what-if analysis — in a fun and accessible way

## Screenshots

<div align="center">
<table>
<tr>
<td><img src="./static/image/Screenshot/运行截图1.png" alt="Screenshot 1" width="100%"/></td>
<td><img src="./static/image/Screenshot/运行截图2.png" alt="Screenshot 2" width="100%"/></td>
</tr>
<tr>
<td><img src="./static/image/Screenshot/运行截图3.png" alt="Screenshot 3" width="100%"/></td>
<td><img src="./static/image/Screenshot/运行截图4.png" alt="Screenshot 4" width="100%"/></td>
</tr>
<tr>
<td><img src="./static/image/Screenshot/运行截图5.png" alt="Screenshot 5" width="100%"/></td>
<td><img src="./static/image/Screenshot/运行截图6.png" alt="Screenshot 6" width="100%"/></td>
</tr>
</table>
</div>

## Workflow

1. **Graph Building**: Seed extraction & individual/collective memory injection & GraphRAG construction
2. **Environment Setup**: Entity relationship extraction & persona generation & agent configuration
3. **Simulation**: Dual-platform parallel simulation & auto-parse prediction requirements & dynamic temporal memory updates
4. **Report Generation**: ReportAgent with rich toolset for deep interaction with post-simulation environment
5. **Deep Interaction**: Chat with any agent in the simulated world & interact with ReportAgent

## Quick Start

### Option 1: Source Code Deployment (Recommended)

#### Prerequisites

| Tool | Version | Description | Check |
|------|---------|-------------|-------|
| **Node.js** | 18+ | Frontend runtime, includes npm | `node -v` |
| **Python** | ≥3.11, ≤3.12 | Backend runtime | `python --version` |
| **uv** | Latest | Python package manager | `uv --version` |

#### 1. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env and fill in the required API keys
```

**Required Environment Variables:**

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

ZEP_API_KEY=your_zep_api_key
```

#### 2. Install Dependencies

```bash
npm run setup:all
```

Or step by step:

```bash
npm run setup
npm run setup:backend
```

#### 3. Start Services

```bash
npm run dev
```

**Service URLs:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5001`

**Start Individually:**

```bash
npm run backend
npm run frontend
```

### Option 2: Docker Deployment

```bash
cp .env.example .env
docker compose up -d
```

Reads `.env` from root directory by default, maps ports `3000 (frontend) / 5001 (backend)`.

## Acknowledgments

KEPHALOS DATA's simulation engine is powered by **[OASIS](https://github.com/camel-ai/oasis)**. We sincerely thank the CAMEL-AI team for their open-source contributions.
