# Carteras Colectivas — Claude Desktop Extension

> Colombian mutual funds (FICs) — performance, risk, fees, and market segmentation across 650+ fund offerings (ofertas de inversión) with 17+ years of history.

This repository contains the source for the **Carteras Colectivas** Claude Desktop Extension (`.mcpb` bundle). The extension provides AI-assisted analysis of Colombian Fondos de Inversión Colectiva (FICs) directly inside Claude Desktop.

The MCP server itself is hosted at `https://agents.carterascolectivas.co/mcp`. This bundle ships a thin client bridge (~9 kB Python) that forwards requests over HTTPS using your API key.

---

## Install

1. Download the latest `carteras-colectivas-mcp.mcpb` from the [Releases page](https://github.com/carterascolectivas/carteras-colectivas-mcp/releases) (or from the Anthropic Desktop Extensions Directory once approved).
2. Double-click the file — Claude Desktop will prompt to install.
3. When prompted for "API Key", paste your Carteras Colectivas key (provided with your subscription).
4. Enable the extension in **Settings → Extensions**.

### Get an API key

Contact **info@carterascolectivas.co** or visit [www.carterascolectivas.co](https://www.carterascolectivas.co) to subscribe and receive a key.

### Requirements

- Claude Desktop (macOS, Windows, or Linux)
- An active Carteras Colectivas API key
- `uv` runtime (auto-installed by Claude Desktop on first launch — no manual setup)

---

## What's included

The 28 tools in this extension are all **read-only**. They fall into five groups:

- **Data discovery** — `query_database` (SELECT-only SQL), `get_schema_info`, `get_table_info`, `health_check`, `check_data_freshness`
- **Fund lookup** — `search_funds`, `list_all_funds`, `filter_funds`, `list_categories`
- **Fund analysis** — `analyze_fund_performance`, `get_fund_overview`, `get_risk_metrics`, `analyze_fees`, `get_fund_attribution`, `generate_investment_chart`
- **Comparison & ranking** — `compare_funds`, `compare_to_benchmark`, `get_fund_percentiles`, `get_fund_correlations`, `get_alpha_ranking`, `compare_category_funds`, `find_similar_funds`, `get_diversification_matrix`
- **Market segmentation** — `get_market_segments`, `get_segment_funds`, `get_segment_distribution`, `match_investor_profile`, `compare_segment_performance`

---

## Example prompts

- *"List all Renta Variable funds with more than 100 billion COP under management."*
- *"What's the 3-year Sharpe ratio of the top fund in the equity category by AUM?"*
- *"Compare the fees of these three funds over a 5-year horizon with a 10M COP investment."*
- *"Which funds in the Persona Natural segment have the highest 1-year return?"*

Claude will pick the right tool(s) and present the result.

---

## Data source

Data is sourced from regulatory filings and monthly publications by fund administrators under [Superintendencia Financiera de Colombia](https://www.superfinanciera.gov.co/) oversight. Coverage includes 650+ fund offerings (participaciones) across all four investor segments (PN, PJ, Institucional, Especiales), with 17+ years of continuous history.

---

## Privacy

See the [Privacy Policy](https://www.carterascolectivas.co/legal#privacy-policy). The extension:

- Only transmits your API key and the tool arguments Claude generates from your prompts.
- Does **not** collect personal information beyond what is needed to fulfill subscription operations.
- Does **not** send your conversations or unrelated context to Carteras Colectivas.

---

## Repository contents

This is the public source mirror for the `.mcpb` bundle. It contains only the files that ship to end users:

| File | Purpose |
|---|---|
| `CarterasColectivasMCP_bridge.py` | Thin HTTPS client that runs in Claude Desktop and forwards MCP calls to the hosted server |
| `manifest.json` | MCPB v0.4 manifest (display name, description, tool list, user-config schema) |
| `pyproject.toml` | Python dependencies (`mcp`, `requests`) resolved by `uv` at install time |
| `icon.png` | Catalog icon (512×512) |
| `LICENSE` | Proprietary |
| `README.md` | This file |

The hosted server (Aurora MySQL, AWS Lambda, query validator, business logic) is maintained in a separate private repository and is not part of this distribution.

---

## Support

- Email: **info@carterascolectivas.co**
- Homepage: [www.carterascolectivas.co](https://www.carterascolectivas.co)
- Documentation: [agents.carterascolectivas.co](https://agents.carterascolectivas.co)
- Issues: please email rather than file a GitHub issue — the public repo is a source mirror, not a support channel.

---

## License

Proprietary © Carteras Colectivas Profesional. All rights reserved.
