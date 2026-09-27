# Sample cash break (for testing `/recon` or `/recon-cash`)

> Fictional data. Paste this in to see the investigation run end-to-end.

**Account:** Operating Account #4471 — CAD
**As of:** 2026-07-03

| Source | Balance |
|---|---|
| Internal ledger (GL) | 128,450.00 |
| Bank statement | 126,900.00 |
| **Difference** | **1,550.00** |

Transaction detail (bank statement, July 3):

| Date | Description | Amount |
|---|---|---|
| 2026-07-03 | Incoming wire — client ABC | +45,000.00 |
| 2026-07-03 | Account maintenance fee | -50.00 |
| 2026-07-03 | Outgoing payment — vendor XYZ | -1,500.00 |

Internal ledger booked the +45,000 wire and the -1,500 vendor payment, but did
**not** book the -50 fee, and shows a second -1,500 vendor payment that the bank
does not show.

*(A good investigation should land on: unrecorded $50 bank fee + a $1,500
duplicate payment booked internally = $1,550 difference.)*
