# Reconciliation Break — Investigation Template

Paste your discrepancy data (CSV, table, or description) below the line, then
work through this structure. This template is generic — it makes no
assumptions about which platform, custodian, or internal system the data came
from.

---

## 1. Restate the break in one sentence
- What two sources disagree, on what value, as of what date?
  _e.g. "Internal ledger shows a $30,000 cash balance for account X on
  settlement date; custodian statement shows $28,450 for the same account/date."_

## 2. Classify the break type
Pick the closest fit — this changes what you look for next:
- **Timing difference** — both sides are "right", one just hasn't posted yet
  (trade date vs. settlement date, cut-off time mismatch)
- **Price/FX difference** — same trade, different valuation or exchange rate
  applied
- **Quantity/position difference** — share count, notional, or units don't
  match
- **Missing entry** — one side has a transaction the other doesn't
- **Duplicate entry** — one side recorded something twice
- **Fee/tax/withholding difference** — a charge or withholding amount applied
  inconsistently
- **Static data error** — wrong account, wrong currency, wrong settlement
  instructions on file

## 3. Gather the minimum evidence set
For most breaks you need, at minimum:
- Trade/transaction ID or reference number on both sides
- Trade date and settlement date
- Amount, currency, and quantity on both sides
- Counterparty / custodian / broker identifiers
- Any prior day's balance to establish when the difference first appeared

## 4. Root-cause checklist (work top to bottom, stop when one fits)
1. Does the difference exactly match a known fee, FX rate, or withholding
   percentage? → likely a fee/tax/FX difference, not a real break.
2. Does the difference appear only as of one specific date and self-correct
   the next day? → likely a timing difference.
3. Is there a transaction on one side with no matching reference on the
   other, for the same amount? → likely a missing or duplicate entry.
4. Does the account/currency/settlement instruction differ between the two
   sources for the same trade? → likely a static data error.
5. If none of the above fit exactly, isolate the smallest set of transactions
   that sum to the discrepancy amount — this narrows "which trade(s)" before
   asking "why."

## 5. Draft the write-up
Once you've identified the likely cause, produce:
- **One-line summary** — cause + amount + accounts affected
- **Evidence** — the specific transaction IDs/dates that support the
  conclusion
- **Recommended resolution** — booking correction, timing adjustment,
  escalation to counterparty, or write-off (with approval)
- **Prevention note** (optional) — if this is a recurring pattern, what
  process or control would catch it earlier next time

---

## Paste your data here:

