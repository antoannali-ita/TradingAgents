# TradingAgents — prova controllata multi-agente

Questa branch mantiene intatto il framework originale e aggiunge una modalità
semplice per analizzare uno o più strumenti. Non invia ordini a broker.

## 1. Preparazione

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Nel file `.env` inserire esclusivamente la chiave del provider scelto. Non
caricare mai `.env` su GitHub: è già escluso tramite `.gitignore`.

Esempio OpenAI:

```dotenv
OPENAI_API_KEY=...
TRADINGAGENTS_LLM_PROVIDER=openai
TRADINGAGENTS_DEEP_THINK_LLM=gpt-5.5
TRADINGAGENTS_QUICK_THINK_LLM=gpt-5.4-mini
TRADINGAGENTS_OUTPUT_LANGUAGE=Italian
```

## 2. Prima prova: un titolo

```bash
python scripts/analyze_watchlist.py NVDA --date 2026-08-19 --checkpoint
```

## 3. Prova su più strumenti

```bash
python scripts/analyze_watchlist.py NVDA INTU B --date 2026-08-19 --checkpoint
```

Per un ETF quotato a Milano usare il ticker Yahoo Finance completo, per esempio
`SWDA.MI`. Per le criptovalute usare la forma `BTC-USD`.

## Output

- report dettagliato per ogni strumento;
- decisione finale multi-agente;
- file JSON riepilogativo della watchlist;
- eventuali errori isolati, senza interrompere gli altri titoli.

## Regola operativa

Il risultato è un secondo parere sperimentale. Prima di qualsiasi decisione va
confrontato con il motore proprietario, il portafoglio, le commissioni, gli
earnings e i limiti di rischio. Nessun risultato genera ordini automatici.
