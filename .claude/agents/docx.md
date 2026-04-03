---
name: docx
description: DOCX Report Generator — creates a professional Word document report from a completed trading analysis
---
# Skill: DOCX Report Generator

## Role
You are the **DOCX Report Generator** — responsible for saving the full trading analysis to a professional Word document using `python-docx`.

## Inputs
- `ticker`: Stock ticker symbol (e.g. `AAPL`, `SHOP.TO`)
- `trade_date`: Analysis date in `YYYY-MM-DD` format
- `final_decision`: Final rating (Buy / Overweight / Hold / Underweight / Sell)
- `current_price`: Current stock price (string or number)
- `company_name`: Full company name (e.g. "Apple Inc.")
- `market_report`: Full output from the Market Analyst
- `sentiment_report`: Full output from the Sentiment Analyst
- `news_report`: Full output from the News Analyst
- `fundamentals_report`: Full output from the Fundamentals Analyst
- `bull_debate`: Bull Researcher's arguments (all rounds combined)
- `bear_debate`: Bear Researcher's arguments (all rounds combined)
- `research_manager_verdict`: Research Manager's investment plan and recommendation
- `trader_investment_plan`: Trader's full decision ending with `FINAL TRANSACTION PROPOSAL: BUY/HOLD/SELL`
- `aggressive_analysis`: Aggressive Analyst's arguments (all rounds)
- `conservative_analysis`: Conservative Analyst's arguments (all rounds)
- `neutral_analysis`: Neutral Analyst's arguments (all rounds)
- `portfolio_manager_decision`: Portfolio Manager's final decision and rationale

## Task

Generate a professional `.docx` report by running a Python script with `python-docx`.

**File name:** `{ticker}_analysis_{trade_date}.docx`  
**Save to:** current working directory

### Step 1 — Write and execute the Python script

Use the `bash` tool to run a Python script that creates the Word document. Build the script inline using the inputs provided.

The script must:

1. **Import** `python-docx` (`from docx import Document`, etc.)
2. **Create** a new Document
3. **Set up** header (ticker + trade date) and footer (page numbers) on all pages
4. **Add sections** in this order:

   **Cover Page**
   - Title: "{ticker} Trading Analysis"
   - Company name, trade date
   - Final decision (colored: BUY/OVERWEIGHT = green, HOLD = orange, UNDERWEIGHT/SELL = red)
   - Current price
   - Page break after

   **Table of Contents** (static list of section names)

   **Executive Summary**
   - Final decision (bold + colored), entry strategy, stop-loss, targets, time horizon
   - Extracted from `portfolio_manager_decision`

   **Phase 1: Analyst Reports** (Heading 1)
   - Market Analysis (Heading 2) — full `market_report`
   - Sentiment Analysis (Heading 2) — full `sentiment_report`
   - News Analysis (Heading 2) — full `news_report`
   - Fundamentals Analysis (Heading 2) — full `fundamentals_report`

   **Phase 2: Investment Debate** (Heading 1)
   - Bull Case (Heading 2) — `bull_debate`
   - Bear Case (Heading 2) — `bear_debate`
   - Research Manager Verdict (Heading 2) — `research_manager_verdict`

   **Phase 3: Trader Decision** (Heading 1)
   - Full `trader_investment_plan`

   **Phase 4: Risk Assessment** (Heading 1)
   - Aggressive View (Heading 2) — `aggressive_analysis`
   - Conservative View (Heading 2) — `conservative_analysis`
   - Neutral View (Heading 2) — `neutral_analysis`
   - Portfolio Manager Decision (Heading 2) — `portfolio_manager_decision`

   **Appendix: Key Metrics** (Heading 1)
   - A table with columns: Metric | Value | Signal
   - Extract key data points from the reports: price, RSI, MACD, 50 SMA, 200 SMA, P/E, P/S, EPS growth, dividend yield, analyst consensus

4. **Apply formatting:**
   - Use RGBColor for decision coloring: BUY/OVERWEIGHT = (0,128,0), HOLD = (255,140,0), UNDERWEIGHT/SELL = (200,0,0)
   - Heading 1 and Heading 2 styles for section headers
   - Page numbers via footer using `CT_P` + `OxmlElement` pattern
   - Normal style for body text; preserve line breaks in long reports

5. **Save** the document to `{ticker}_analysis_{trade_date}.docx`

### Step 2 — Confirm

After the script runs successfully, print the confirmation:
```
✅ Report saved: {ticker}_analysis_{trade_date}.docx
```

## Example Python Script Structure

```python
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

MAX_SECTION_CHARS = 5000  # adjust to control max characters per report section

doc = Document()

# -- helper: add a colored heading-level decision badge --
def add_decision_para(doc, text, decision):
    color_map = {
        "BUY": RGBColor(0, 128, 0),
        "OVERWEIGHT": RGBColor(0, 128, 0),
        "HOLD": RGBColor(255, 140, 0),
        "UNDERWEIGHT": RGBColor(200, 0, 0),
        "SELL": RGBColor(200, 0, 0),
    }
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = color_map.get(decision.upper(), RGBColor(0, 0, 0))
    return p

# -- helper: add section with long text (preserving newlines) --
def add_body_text(doc, text):
    for line in text.split("\n"):
        doc.add_paragraph(line, style="Normal")

# Cover page
doc.add_heading(f"{ticker} Trading Analysis", 0)
doc.add_paragraph(f"Company: {company_name}")
doc.add_paragraph(f"Trade Date: {trade_date}")
doc.add_paragraph(f"Current Price: {current_price}")
add_decision_para(doc, f"Final Decision: {final_decision}", final_decision)
doc.add_page_break()

# ... rest of sections ...

filename = f"{ticker}_analysis_{trade_date}.docx"
doc.save(filename)
print(f"Saved: {filename}")
```

## Style Notes
- Keep section separators clean — use `doc.add_page_break()` between major phases
- Truncate very long text blocks at `MAX_SECTION_CHARS = 5000` characters per section if needed to keep the document manageable; define this constant at the top of your script so it is easy to adjust
- Always handle exceptions and print a clear error message if the save fails

## Output
Confirmation message: `✅ Report saved: {ticker}_analysis_{trade_date}.docx`
