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

Configurazione Gemini consigliata per la prima prova:

```dotenv
GOOGLE_API_KEY=incolla_qui_la_chiave_solo_in_locale
TRADINGAGENTS_LLM_PROVIDER=google
TRADINGAGENTS_DEEP_THINK_LLM=gemini-3.5-flash
TRADINGAGENTS_QUICK_THINK_LLM=gemini-3.1-flash-lite
TRADINGAGENTS_OUTPUT_LANGUAGE=Italian
TRADINGAGENTS_MAX_DEBATE_ROUNDS=1
TRADINGAGENTS_MAX_RISK_ROUNDS=1
TRADINGAGENTS_CHECKPOINT_ENABLED=true
```

Il livello gratuito ha quote per progetto. Per evitare di saturarle, iniziare
con un solo ticker e senza aumentare i round di dibattito o rischio.

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
