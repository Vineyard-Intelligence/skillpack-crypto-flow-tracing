# skillpack-crypto-flow-tracing

The **Crypto fund-flow tracing** Skill Pack for Vineyard: a text investigation playbook that starts from an address, transaction or text and follows the funds hop by hop on the network the address really is on, to the exchanges and stablecoin issuers that can freeze them or name the account holder. It never draws an owner or a transfer the chain did not record.

The pack is built for hacking, scam and money-laundering cases: incident transaction analysis, per-asset value accounting, candidate clusters, laundering patterns, mixers and bridges, and address poisoning.

| Field | Value |
| --- | --- |
| Identifier | `run.vineyard.skillpacks.crypto_flow_tracing` |
| Version | `1.1.0` |
| Applies to | `cryptocurrency.crypto_address`, `cryptocurrency.crypto_transaction`, `cryptocurrency.crypto_token`, `financial.crypto_address`, `financial.crypto_transaction` |
| Requires | `run.vineyard.pluginpacks.chain_explorer` |

## When to use
- The analyst gives an address, a transaction hash, or a text that holds them, and asks where the funds went or came from.
- You need the victim funds and the attacker's receiving address in a hacking, scam, rug-pull or voice-phishing case.
- You are investigating a laundering structure: distribution, peel chain, mixer or bridge hops.
- You need an address's first funder, an issuer freeze check, or the sanctions status along a trace.
- You need the request table for the exchanges and issuers the funds reached.

Do not use it for one fact about one address, or for a domain, a person or an account. Hand those to "Infrastructure pivoting" or "Account & identity pivoting".

## What changed in 1.1.0
This release brings the English pack to the same content as the Korean edition: 10 sections become 17, with 15 starters, and the sections that touch plugin behaviour are corrected against the plugin packs' actual fields and coverage.

- **New sections:** `case-scoping` (case type, scope and freeze priority), `incident-transaction` (executor, receiver and victim roles in an incident), `value-accounting` (per-asset accounting, loss/net/proceeds, no local USD conversion), `laundering-patterns` (peel chain, distribution, consolidation, pass-through, chain hops), `clustering` (common input, common gas or asset funder, deposit-address patterns as candidates), `mixers` and `bridges-cross-chain` (split from the old `mixers-bridges`), and `address-poisoning` (look-alike addresses, dust, fake tokens).
- **Corrected against the plugin packs:** Chain Explorer's main EVM histories include internal transfers by default (not on BNB Smart Chain), while the keyed EVM history plugin includes them only with `include_internal: true`; two EVM history plugins can write the same `summary_<source>` key; `complete`, `history_complete` and `window_from` are different values; plugins do not draw zero-value transfers; BNB Smart Chain is limited to 30 days and Solana keyless history can miss SPL token-account receipts; the keyed EVM history pack's free and paid plans cover different chains; a first funder may be only a gas funder; `same address on` records the same string, not a transfer; an EIP-7702-delegated account is still shown as an EOA.
- **Service names:** the playbook describes plugin packs by capability, not by the third-party service a pack wraps. "Chain Explorer" remains named because it spans several services and points at no single one.
- **Size:** 17 sections and 15 starters; no section body exceeds the app's 8,000-character cap, and the document fits the 256 KB pack limit.

## Requirements
- The keyless `run.vineyard.pluginpacks.chain_explorer` pack and the Cryptocurrency type pack it writes. This pack declares Chain Explorer in `requires`; the skill is not offered when it cannot run in the project. Chain Explorer runs in the web app and the desktop app.
- Optional, where installed: keyed EVM history, address-detail and first-funder packs; Solana history, first-funder and wallet-identity packs; a Bitcoin-family history pack; and a sanctions list pack. The EVM history pack is desktop only and needs a key; its free plan reads Ethereum, OP Mainnet, Ethereum Classic and Arbitrum One, while Base and Polygon need a paid plan, and it does not cover BNB Smart Chain or Avalanche C-Chain. The Solana history and first-funder paths work on a free key and wallet identity needs a paid plan. The Bitcoin-family pack needs a key and covers BTC/BCH/LTC/BSV/DOGE/DASH/ZEC transparent addresses. Where a needed pack, key or plan is missing, the agent names the gap.
- Graph write access to stage seed addresses and transactions, and `challenge_claim` before a conclusion about who controls funds.
- Packs that are withheld pending terms are not required or described here.

## Structure
The `overview` is the top-level Markdown card. Load one section for the step you are on; each section body is a self-contained Markdown document with its own `#` title and `##` headings.

| Section | Use it for |
| --- | --- |
| `case-scoping` | Fix the case type, scope, reporting target and freeze priority before the first hop. |
| `starting-point` | Turn an address, a transaction, a text or a token history into seed nodes without guessing a network. |
| `identify-network` | Settle each seed's network before any hop, and know what each network can reach with and without a key. |
| `incident-transaction` | Separate executor, receiver and victim in an incident transaction, and record what actually moved per asset. |
| `hop-strategy` | Choose what to follow by asset, time and amount; know the window; raise the right limits; stop at hubs. |
| `value-accounting` | Reconcile amounts per asset and keep total loss, net loss and candidate attacker proceeds apart. |
| `laundering-patterns` | Classify observed structures: peel chain, distribution, consolidation, pass-through, chain hops. |
| `first-funder` | Who first funded an address, on which network, and whether it was gas or assets. |
| `clustering` | Candidate clusters of addresses that may share a controller, with heuristics and limits. |
| `service-identification` | Whether a busy or labelled address is an exchange, a service or a holder, and what a label is worth. |
| `mixers` | Where a mixer ends the recorded trace, what the withdrawal candidate set is, and the sanctions exposure. |
| `bridges-cross-chain` | Follow funds to another network and keep a direct source-destination link distinct from a candidate. |
| `address-poisoning` | Separate look-alike addresses, dust and fake tokens from real flows, and find the real receiver. |
| `issuer-freeze` | Whether USDT or USDC on the trace is frozen by its issuer, and what to request when it is not. |
| `sanctions-check` | Listings and exposure, with the list's date, and name candidates as candidates. |
| `evidence` | What goes on the canvas, what goes in the report, and how to cite amounts, times, sources and confidence. |
| `outputs` | The flow table, the exchange and issuer request table, the candidate cluster table, UTC and KST, and the five-part report. |

## What the agent draws and what it writes

Transfers are the chain's record, and only plugins put them on the canvas: `sent to`, `input to`, `output to`, first funders, deployers, freezes, labels, sanctions listings, and the attribution edges a wallet-identity plugin writes. The agent does not draw a link between two addresses already in the project, does not relabel a plugin's edge, and does not turn a label, a deposit pattern or a matching amount into an attribution or a transfer. It also states in the report that plugins do not collect zero-value transfers.

A plugin-written `attributed to` edge is still a vendor claim, not verified ownership: cite `label_kind`, `as_of` and the label's source, and run `challenge_claim` before writing that someone controls an address.

Those inferences still matter: they decide which exchange gets a request. So they go in the report as sentences, each with its basis, a confidence, the alternative that survives and the check that would settle it. Clusters stay a candidate table, never a canvas edge. Amounts stay decimal strings, and the pack does not convert them to USD without a stated price source. The grade the app shows on a link is derived from what produced it; the pack never sets one.

## Source and translation
- The English edition and the Korean edition (`skillpack-crypto-flow-tracing-ko`, `run.vineyard.skillpacks.crypto_flow_tracing_ko`) carry the same 17 sections, 15 starters and the same method. Keep them in step when either changes.
- Section headings are English, and the Korean edition translates only the body. Section ids, edge labels, field names, plugin names and tool names stay as written in both, so graphs and loaders read the same strings.
- The playbook names plugin packs by capability, not by the third-party service a pack wraps. The one exception is "Chain Explorer", which spans several services and points at no single one.
- The document carries two texts: `summary` (the card line) and `description` (the pack page). `scripts/validate.py` checks both caps.
- Packs withheld pending terms are not listed or assumed. If one is released later, add it conditionally to `service-identification`, `clustering` and `value-accounting`.

## Reference material
The 1.1.0 revision read the public skills and repositories below and took only methods that can be verified with Vineyard plugins. This list is where the analysis started; these are not the services the plugin packs wrap, and no product API instructions from them are reproduced.

- [minaminao/ctf-blockchain](https://github.com/minaminao/ctf-blockchain): mostly exploit challenges, rejected. Kept only `src/Scan2024CTF/` for finding a fund wallet from token history, confirming a bridge receipt, splitting drainer fees and the ransomware broker-to-master structure, `FuzzyIdentity` for address grinding (address-poisoning warning), and `Ethernaut Force` for `selfdestruct` forced transfers (value accounting).
- [slowmist/misttrack-skills](https://github.com/slowmist/misttrack-skills): its API, x402 payment and scripts were rejected because no such plugin is installed. Kept the gas-funder versus asset-funder split, describing risk as hop distance times amount share, "a failed check is not clean", and multisig assessment criteria.
- [etherscan/skills](https://github.com/etherscan/skills): kept "only what this run read is a fact", roles from evidence only, execution-evidence rules (logs are not state, approval is not a transfer, reverted effects do not persist, internal transactions are not a call tree, proxy versus implementation), lossless amount arithmetic, and the USD and gap rules. Its API and CLI instructions were rejected.
- [Viprasol-Tech/onchain-forensics](https://github.com/Viprasol-Tech/onchain-forensics): adopted the six-stage checklist, MIH, change-address, deposit-address and common-gas-funder heuristics, peel chain, obfuscation chains, bridge receipt matching, and confidence and reproducibility logs. Its examples are fabricated and the mixer statistics it cites come from a withdrawn preprint, so the numbers and the legal self-certification were rejected.
- [allium-labs/skills](https://github.com/allium-labs/skills): adopted investigation scoping and the data contract, "a listing is not coverage", stock versus flow, asymmetric bridge legs and double counting, native versus bridged assets, pass-through versus inventory, and the USD and reproducibility rules. Its SQL and MCP instructions were rejected.
- [Vo1ganin/crypto-claude-skills](https://github.com/Vo1ganin/crypto-claude-skills): adopted label relation grades (confirmed/candidate/weak), the evidentiary standing of vendor labels, "fee data alone does not prove intent", Solana token accounts, decimals and time precision, and rug-pull lifecycle signals. Its vendor API instructions were rejected.

## Testing and installation
Listed in the [registry](https://github.com/Vineyard-Intelligence/registry) at the pinned commit. To test the document without the registry:

- Import the JSON through **Run ▸ Skill packs ▸ Import skill pack…**. Import renames the `run.vineyard` identifier into a `local.project.skillpacks.*` copy and fills in the current author, so open it by the renamed id or by display name.
- Run `python3 scripts/validate.py`. It checks the document against the app's loader caps, and checks that the README's version, identifier, applies-to and requires rows and its section list match the document. Pass another pack repo path to validate that repo the same way.
- Open the pack in the app's Skill Pack editor and save it once, to confirm the loader cuts or drops nothing.

## Layout

| Path | Purpose |
| --- | --- |
| `skillpacks/crypto-flow.skill.json` | The Skill Pack document (overview, sections, starters) |
| `scripts/validate.py` | Format, length, starter-variable and README-consistency checks |
| `.github/workflows/validate.yml` | Runs the validation on pull requests |

## License

MIT
