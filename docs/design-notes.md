# Design notes

Short notes on why ReconKit is built the way it is.

## Why one engine + presets, not one rigid tool

Reconciliation looks standard from the outside but isn't: the matching key, the
tolerance, the break categories, and the escalation rules differ by firm, by
file, and by person. A tool that hard-codes one method would be wrong for almost
everyone and — worse — would look wrong to the experienced ops people who'd
actually judge it.

So ReconKit separates the **thinking** from the **specifics**:

- The **engine** (`framework/investigation-template.md`) is the part that never
  changes: restate the break → classify it → gather evidence → work the
  root-cause checklist → write the finding.
- The **presets** (`/recon-cash`, `/recon-positions`, `/recon-statement`) are thin
  wrappers that tune *which break types to look for* and *what words to use*.
- The **adaptive mode** (`/recon`) takes the person's own method as input and
  works with any file, for everything the presets don't cover.

Add a new recon type and you write one small preset, not a new tool.

## Why it reasons only over pasted data

It deliberately connects to no bank, custodian, or internal system. That keeps it
safe to use (nothing leaves the conversation), portable (works with any file you
can paste), and honest (it can only conclude from what it's actually shown). When
the data is too thin, the right answer is "here's what's missing," not a
confident guess.

## Why the offline tools are bundled

Not everyone wants to paste data into an AI, and not every task needs one. The
formula-only Excel checklist and the dependency-free VBA generator cover the
"zero cost, zero internet, zero AI" cases — log a break by hand, or generate a
macro to compare two sheets — so the kit is useful even with the AI turned off.

## Why "never invent a transaction" is a hard rule

A reconciliation finding is only worth anything if it's true. Inventing a
plausible-looking cause to fill a gap is worse than saying "I can't tell yet" —
it sends someone chasing the wrong fix. So the engine narrows to the smallest set
of transactions that explains the difference and asks for what it needs, rather
than manufacturing detail.
