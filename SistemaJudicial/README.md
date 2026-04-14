# ⚖️ Sistema Judicial Inteligente

Sistema de simulación judicial con IA, estructuras de datos avanzadas y una interfaz web temática.

---

## 🚀 Cómo Ejecutar

### 1. Instalar dependencias

```bash
cd backend
pip install flask flask-cors
```

### 2. (Opcional) Configurar API Key de Anthropic

```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # Linux/Mac
set ANTHROPIC_API_KEY=sk-ant-...         # Windows CMD
```
Sin API Key el sistema funciona en **modo demo** con análisis jurídico local.

### 3. Iniciar el backend

```bash
cd backend
python app.py
```
El servidor corre en: `http://localhost:5000`

### 4. Abrir el frontend

Abra `frontend/index.html` en su navegador.  
O use Live Server en VS Code.

---

## 🏗️ Arquitectura del Sistema

```
judicial_system/
├── backend/
│   ├── data_structures.py   ← Las 5 estructuras de datos
│   ├── models.py            ← Case, Evidence (dominio)
│   ├── legal_advisor.py     ← IA + Base de leyes (Array)
│   ├── court_system.py      ← Orquestador principal
│   ├── app.py               ← Flask REST API
│   └── requirements.txt
└── frontend/
    └── index.html           ← UI completa (HTML+CSS+JS)
```

---

## 📦 Estructuras de Datos Implementadas

| Estructura | Clase | Uso en el Sistema |
|---|---|---|
| **Queue (Cola FIFO)** | `CaseQueue` | Casos esperando ser procesados |
| **Stack (Pila LIFO)** | `EvidenceStack` | Evidencias del caso |
| **Array** | `LegalArticlesArray` | Base de artículos del Código Penal |
| **Linked List** | `CaseHistoryList` | Historial completo de casos |
| **Doubly Linked List** | `StagePipeline` | Flujo bidireccional de etapas |

---

## 🤖 Módulo de IA

`LegalAdvisor` conecta con `claude-sonnet-4-20250514` (Anthropic API).

- Analiza evidencia del caso (pila LIFO convertida a contexto)
- Consulta artículos del Código Penal (array)
- Sugiere veredicto con justificación
- Modo fallback con análisis local si no hay API Key

---

## 🌐 Endpoints REST

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/cases` | Listar todos los casos |
| POST | `/api/cases` | Crear nuevo caso |
| GET | `/api/cases/:id` | Detalle de un caso |
| POST | `/api/cases/:id/advance` | Avanzar etapa |
| POST | `/api/cases/:id/revert` | Retroceder etapa |
| POST | `/api/cases/:id/evidence` | Agregar evidencia |
| POST | `/api/cases/:id/ask` | Consultar IA |
| POST | `/api/cases/:id/resolve` | Emitir sentencia |
| GET | `/api/metrics` | Estadísticas del sistema |
| GET | `/api/laws` | Base legal (Array) |
| GET | `/api/queue` | Ver cola FIFO |
| GET | `/api/history` | Ver lista enlazada |

---

## 🎨 Diseño

Tema **judicial oscuro** con:
- Tipografía: Cormorant Garamond (serif) + Josefin Sans
- Paleta: Fondos oscuros #0a0c10 + Dorado #c8a96e
- Animaciones CSS, textura de ruido, pipeline visual de etapas
- Chat con el Dr. Justus renderizado en Markdown

---

*Desarrollado con Python + Flask + HTML/CSS/JS puro*
