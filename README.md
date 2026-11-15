# skillpack-crypto-flow-tracing

The **Crypto fund-flow tracing** Skill Pack for Vineyard: a text investigation playbook that follows crypto funds from one address or transaction, hop by hop on the network the address is really on, to the exchanges and stablecoin issuers that can freeze them or name the account holder, without drawing an owner the chain never recorded.

| Field | Value |
| --- | --- |
| Identifier | `run.vineyard.skillpacks.crypto_flow_tracing` |
| Version | `1.0.0` |
| Applies to | `cryptocurrency.crypto_address`, `cryptocurrency.crypto_transaction`, `financial.crypto_address` |
| Requires | `run.vineyard.pluginpacks.chain_explorer` |

## When to use
- The analyst has an address, a transaction hash, or a text that holds them, and asks where the funds went or came from.
- You need an address's first funder, an issuer freeze check, or a sanctions check along a trace.
- You need the request table for the exchanges and issuers the funds reached.

Do not use it for one fact about one address, or for a domain, a person or an account. Hand those to "Infrastructure pivoting" or "Account & identity pivoting".

## Requirements
- The `run.vineyard.pluginpacks.chain_explorer` plugin pack (keyless) and the Cryptocurrency type pack it writes. This pack declares Chain Explorer in `requires`; the skill is not offered when it cannot run in the project. Chain Explorer runs in the web app and the desktop app.
- Optional, where installed: keyed packs for depth (Blockscout PRO, Helius, Blockchair), Helius's Solana Wallet Identity for attribution on Solana, and the Sanctions pack for OFAC screening. Where a network or check needs one that is not installed, the agent names the gap.
- Graph write access to stage seed addresses and transactions.
- `challenge_claim` before a conclusion about who controls funds.

## Structure
The `overview` is the top-level Markdown card. Load one section for the step you are on; each section body is a self-contained Markdown document with its own `#` title and `##` headings.

| Section | Use it for |
| --- | --- |
| `starting-point` | Turn an address, a transaction or a text into seed nodes without guessing a network. |
| `identify-network` | Settle each seed's network before any hop, and know what each network can reach with and without a key. |
| `hop-strategy` | Choose what to follow by asset, time and amount; know the window; stop at hubs. |
| `first-funder` | Who first funded an address, by network. |
| `issuer-freeze` | Whether USDT or USDC on the trace is frozen by its issuer. |
| `service-identification` | Exchange, service or holder, and why an inference stays out of the graph. |
| `mixers-bridges` | Where recorded tracing ends, and what would continue it. |
| `sanctions-check` | Listings and exposure, with the list's date. |
| `evidence` | What goes on the canvas and what goes in the report. |
| `outputs` | The flow table, the exchange and issuer request table, UTC and KST, the five-part report. |

## What the agent draws and what it writes

Transfers are the chain's record, and only plugins put them on the canvas: `sent to`, `input to`, `output to`, first funders, deployers, freezes, labels, sanctions listings. The agent does not draw a link between two addresses already in the project, and does not turn a label, a deposit pattern or a matching amount into an attribution.

Those inferences still matter: they decide which exchange gets a request. So they go in the report as sentences, each with its basis, a confidence, the alternative that survives and the check that would settle it. The grade the app shows on a link is derived from what produced it; the pack never sets one.

## Layout

| Path | Purpose |
| --- | --- |
| `skillpacks/crypto-flow.skill.json` | The Skill Pack document (overview + sections + starters) |
| `.github/workflows/validate.yml` | CI validation |

## Listing / installing

Listed in the [registry](https://github.com/Vineyard-Intelligence/registry); browsable at [docs.vineyard.run](https://docs.vineyard.run/). The registry entry pins an immutable commit of this repo, and the document is served from it via jsDelivr.

## License

MIT
