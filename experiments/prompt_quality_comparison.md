# Prompt Quality Experiment: Does Skill Scaffolding Beat a Great Raw Prompt?

**Research question (Keyaan's hypothesis):** a well-built "skill" — one of this library's
YAML prompts, with its full `system_prompt` + `user_prompt_template` scaffolding — can make
a WEAK raw user prompt outperform a GOOD, or even an AMAZING, raw prompt that has no
scaffolding at all.

**Status:** research artifact only. Not wired into `cli.py` or the Streamlit app. Nothing
here changes production code.

## Method

Three library prompts were chosen from three different categories so the finding isn't an
artifact of one prompt's design:

| Prompt | Category |
|---|---|
| `variance_commentary` | variance |
| `vat_rec` | month_end |
| `board_pack_narrative` | reporting |

For each prompt, one realistic underlying scenario was invented (new numbers, not the
YAML's own `example_input`, so this reads as an independent test rather than the library
marking its own homework). For that scenario, three tiers of a **raw, no-skill** user
request were written — WEAK (vague, minimal detail), GOOD (clear ask, key figures, some
structure requested), AMAZING (an expert management accountant's prompt: precise ask, full
context, structure and tone specified).

For each tier, two outputs were produced against the same underlying facts:

- **RAW** — what a plain LLM call produces for that tier's raw prompt alone, with no system
  prompt and no access to the library's rules.
- **SKILL** — what the LLM produces when the same scenario is run through the actual
  `variance_commentary` / `vat_rec` / `board_pack_narrative` skill (real `system_prompt` +
  `user_prompt_template`, rendered via `lib/renderer.py`), fed with **that tier's own level
  of input completeness** — i.e. a "weak" user of the skill fills in only the required
  numeric fields and skips optional context/notes fields; a "good" user fills in partial
  context; an "amazing" user fills in everything the schema allows.

That second axis matters: the experiment isn't just "scaffolding vs. no scaffolding" with
perfect data in both cases — it's testing whether scaffolding survives *realistic laziness*
on the input side too, which is the more honest test of the hypothesis.

There is no live LLM API key in this environment (by design — no budget for live spend
during this unattended run). All 18 outputs below were generated directly by me, acting as
the model, reasoning the same way the library's target model class would when given each
exact prompt. They are clearly labelled RAW or SKILL throughout. `vat_rec` outputs below all
use `output_type: manager_review` (rather than `all`) purely to keep the three tiers
comparable in length — `file_note`/`client_note` follow the same pattern.

---

## 1. `variance_commentary` — Bramwell FM Services Ltd, November 2025

**Underlying facts** (same across all six outputs):

| Line | Actual | Budget | Variance | % | F/A |
|---|---|---|---|---|---|
| Revenue | £612,000 | £590,000 | +£22,000 | +3.7% | F |
| Subcontractor costs | £248,000 | £221,000 | +£27,000 | +12.2% | A |
| Staff costs | £142,000 | £145,000 | −£3,000 | −2.1% | F (immaterial) |
| EBITDA | £94,000 | £103,000 | −£9,000 | −8.7% | A |

Materiality: £7,000 absolute OR 4% — whichever is breached first. Known (but not
necessarily disclosed) drivers: two new site contracts (Riverside Retail Park, Colton
Business Park) mobilised a month early, boosting revenue; emergency HVAC call-outs at two
sites during the November cold snap plus an unnotified day-rate increase from the largest
subcontractor, driving the cost overspend.

### Tier: WEAK

**Raw prompt (no skill):**
> Here's this month's actuals vs budget for Bramwell FM. Can you explain what happened?
> Revenue 612k vs 590k budget, subcontractor costs 248k vs 221k budget, staff costs 142k vs
> 145k budget, EBITDA 94k vs 103k budget.

**RAW output:**
> Thanks for sharing these figures. Here's a quick breakdown of what's happening:
>
> - **Revenue** came in at £612k against a budget of £590k, which is an overperformance of
>   £22k, or about 3.7% above target. That's a positive result.
> - **Subcontractor costs** were £248k versus a £221k budget, an overspend of £27k
>   (roughly 12%). It's worth noting this is a fairly significant overrun and would be worth
>   digging into further to understand the cause — it could be due to higher activity
>   levels, rate increases, or one-off works.
> - **Staff costs** were slightly under budget at £142k vs £145k, a small favourable
>   variance of about 2%.
> - **EBITDA** was £94k against a budget of £103k, a shortfall of £9k (around 8.7%), which
>   seems to be mainly driven by the subcontractor overspend outweighing the revenue
>   upside.
>
> Overall, it looks like the extra revenue wasn't enough to offset higher subcontractor
> spend, resulting in a slight EBITDA miss. If you can share what drove the subcontractor
> increase, I can give you a more precise explanation of the underlying cause. Let me know
> if you'd like this written up more formally for a board pack!

**SKILL output** (inputs: all four numbers + thresholds + tone="executive"; `analyst_notes`
left blank, `reporting_entity` left blank — a weak/lazy use of the skill):

> ## Headline
> **EBITDA of £94,000 fell £9,000 short of budget (A), a 8.7% miss**, as a subcontractor
> cost overrun outweighed a favourable revenue variance.
>
> ## Material Variances
> **EBITDA — £94,000 actual vs £103,000 budget: £9,000 adverse (A) (8.7%)**
> EBITDA missed budget by £9,000. The two variances below only partially explain this gap;
> the balance falls in overhead lines not itemised in this dataset.
>
> **Subcontractor Costs — £248,000 actual vs £221,000 budget: £27,000 adverse (A) (12.2%)**
> Subcontractor costs exceeded budget by £27,000. No driver has been provided for this
> variance.
>
> **Revenue — £612,000 actual vs £590,000 budget: £22,000 favourable (F) (3.7%)**
> Revenue exceeded budget by £22,000. No driver has been provided for this variance.
>
> ## Net Position
> The material variances above produced a combined adverse impact of £5,000 on the lines
> shown (£27,000 adverse subcontractor cost, partially offset by £22,000 favourable
> revenue); the residual £4,000 of the total £9,000 EBITDA shortfall sits in unlisted
> overhead lines and cannot be attributed from the data provided.
>
> ## Screened Out
> One item — staff costs — was within the materiality thresholds of £7,000 absolute / 4%.

### Tier: GOOD

**Raw prompt (no skill):**
> Write a short variance commentary for our November 2025 management accounts (Bramwell FM
> Services Ltd) that I can drop into the board pack. Please only flag variances that are
> meaningfully large — say over about £7k or 4%. Here's the actual vs budget: Revenue £612k
> vs £590k budget; Subcontractor costs £248k vs £221k budget; Staff costs £142k vs £145k
> budget; EBITDA £94k vs £103k budget. Structure it with a headline, the variances that
> matter, and the net EBITDA impact. Executive tone please.

**RAW output:**
> **Headline**
> Bramwell FM Services delivered EBITDA of £94k in November 2025, £9k behind budget, as a
> subcontractor cost overrun more than offset a favourable revenue performance.
>
> **Material Variances**
> - *Revenue:* £612k actual vs £590k budget — £22k favourable (3.7%). Revenue trended ahead
>   of plan for the month.
> - *Subcontractor costs:* £248k actual vs £221k budget — £27k adverse (12.2%). This is the
>   largest variance in the pack and the primary driver of the EBITDA miss.
>
> Staff costs (£142k vs £145k budget, −2.1%) were broadly in line with budget and are not
> flagged given the £7k/4% threshold.
>
> **Net EBITDA Impact**
> The combination of favourable revenue and adverse subcontractor costs nets to a £5k
> adverse position before other overheads, consistent with the overall £9k EBITDA shortfall
> versus budget.
>
> Let me know if you'd like me to add commentary on likely drivers for the subcontractor
> overspend once you have more detail.

**SKILL output** (inputs as WEAK tier, plus `reporting_entity` filled in and one partial
analyst note: `["Subcontractor overspend linked to reactive maintenance call-outs during
the November cold snap."]`):

> ## Headline
> **EBITDA of £94,000 fell £9,000 short of budget (A), a 8.7% miss**, as reactive
> subcontractor call-outs outweighed a favourable revenue variance at Bramwell FM Services
> Ltd.
>
> ## Material Variances
> **EBITDA — £94,000 actual vs £103,000 budget: £9,000 adverse (A) (8.7%)**
> EBITDA missed budget by £9,000. The variances below explain £5,000 of this gap; the
> remaining £4,000 sits in overhead lines not itemised in this dataset.
>
> **Subcontractor Costs — £248,000 actual vs £221,000 budget: £27,000 adverse (A) (12.2%)**
> Subcontractor costs exceeded budget by £27,000, driven by reactive maintenance call-outs
> during the November cold snap.
>
> **Revenue — £612,000 actual vs £590,000 budget: £22,000 favourable (F) (3.7%)**
> Revenue exceeded budget by £22,000. No driver has been provided for this variance.
>
> ## Net Position
> The subcontractor overspend of £27,000 (A) and revenue outperformance of £22,000 (F) net
> to a £5,000 adverse impact on EBITDA, with a further £4,000 of adverse variance sitting in
> unlisted overhead lines.
>
> ## Screened Out
> One item — staff costs — was within the materiality thresholds of £7,000 absolute / 4%.

### Tier: AMAZING

**Raw prompt (no skill):**
> I need a board-ready variance commentary for Bramwell FM Services Ltd's November 2025
> management accounts. Apply a materiality screen of £7,000 absolute OR 4% (either
> threshold breaches = material). For cost lines, actual > budget is adverse; for revenue
> and profit lines, actual > budget is favourable — label every variance (F) or (A). Data:
> Revenue £612,000 actual vs £590,000 budget; Subcontractor costs £248,000 actual vs
> £221,000 budget; Staff costs £142,000 actual vs £145,000 budget; EBITDA £94,000 actual vs
> £103,000 budget. Drivers: revenue outperformance is from two new site contracts (Riverside
> Retail Park, Colton Business Park) mobilised a month early; subcontractor overspend is
> from emergency HVAC call-outs at two sites during the November cold snap plus an
> unnotified day-rate increase from our largest subcontractor from 1 November. Structure as:
> Headline (1 sentence), Material Variances (name/actual/budget/£ var/% var/F-A label/1–2
> sentence driver, largest first), Net Position (1–3 sentences), Screened Out (1 sentence,
> confirm count only). Third person, no filler phrases, no bullet points, GBP with comma
> separators.

**RAW output:**
> **Headline**
> Bramwell FM Services Ltd reported EBITDA of £94,000 against a budget of £103,000 for
> November 2025, an £9,000 adverse variance (8.7%), as a subcontractor cost overrun
> outweighed early contract mobilisation gains on revenue.
>
> **Material Variances**
> Subcontractor costs were £248,000 against a budget of £221,000, a variance of £27,000
> adverse (A) (12.2%). The overspend reflects emergency HVAC call-outs at two sites during
> the November cold snap and an unnotified day-rate increase from the largest subcontractor
> effective 1 November.
>
> Revenue was £612,000 against a budget of £590,000, a variance of £22,000 favourable (F)
> (3.7%). The outperformance is attributable to early mobilisation of two new site
> contracts, Riverside Retail Park and Colton Business Park, both of which were budgeted to
> commence in December.
>
> **Net Position**
> The subcontractor overspend of £27,000 (A) and the revenue outperformance of £22,000 (F)
> combine to a net adverse impact of £5,000 on EBITDA; the residual £4,000 of the total
> £9,000 EBITDA shortfall falls within overhead lines not itemised in this dataset.
>
> **Screened Out**
> One line item, staff costs, was within the materiality thresholds and has been screened
> out.

**SKILL output** (inputs: all fields filled including `reporting_entity` and both full
analyst notes):

> ## Headline
> **EBITDA of £94,000 fell £9,000 short of budget (A), a 8.7% miss**, as a subcontractor
> cost overrun tied to reactive site works and a supplier rate increase outweighed
> early-mobilised contract revenue at Bramwell FM Services Ltd.
>
> ## Material Variances
> **Subcontractor Costs — £248,000 actual vs £221,000 budget: £27,000 adverse (A) (12.2%)**
> Subcontractor costs exceeded budget by £27,000, driven by emergency HVAC repairs at two
> sites following the November cold snap and a day-rate increase from the largest
> subcontractor effective 1 November that was not notified to finance in advance.
>
> **Revenue — £612,000 actual vs £590,000 budget: £22,000 favourable (F) (3.7%)**
> Revenue exceeded budget by £22,000, driven by early mobilisation of the Riverside Retail
> Park and Colton Business Park contracts, both budgeted to commence in December.
>
> ## Net Position
> The £27,000 adverse subcontractor variance (A) and £22,000 favourable revenue variance (F)
> net to a £5,000 adverse impact on EBITDA; the remaining £4,000 of the total £9,000 EBITDA
> shortfall sits in overhead lines not itemised in this dataset.
>
> ## Screened Out
> One item — staff costs — was within the materiality thresholds of £7,000 absolute / 4%.

---

## 2. `vat_rec` — Northfield Interiors Ltd, quarter to 31 May 2026

**Underlying facts:** Box 1 £18,240.60, Box 4 £6,510.20, Box 5 £11,730.40, Box 6 £91,203,
Box 7 £32,551. VAT control diff £340 (fail, in-band), output VAT proof diff −£0.30 (pass),
Box 6 vs TB diff £2,100 (informational), AP vs BS diff £0 (pass), AR vs BS diff £280 (fail,
in-band). Opening VAT balance £3,400, HMRC payments in quarter £15,200, zero-rated sales
£0, filing deadline 7 Jul 2026. Known explanations: the £340 control diff is a supplier
credit note processed in-period but posted to the nominal ledger one day after cut-off
(timing only); the £280 AR diff is a customer overpayment sitting in suspense, agreed with
credit control, due to clear in June.

### Tier: WEAK

**Raw prompt (no skill):**
> Can you check these VAT numbers and tell me if they're ok? Box1 18240.60, Box4 6510.20,
> Box5 11730.40, Box6 91203, control diff 340, AR diff 280.

**RAW output:**
> Thanks for sharing these. Here's a quick sense-check:
>
> - Box 5 should equal Box 1 minus Box 4: 18,240.60 − 6,510.20 = 11,730.40 ✓ — this matches
>   what you've given, so that part looks consistent.
> - Box 6 (net sales) of £91,203 with Box 1 (output VAT) of £18,240.60 implies an effective
>   VAT rate of about 20%, which is in line with the UK standard rate, so that looks
>   broadly reasonable.
> - The VAT control diff of £340 and the AR diff of £280 are both relatively small compared
>   to your VAT liability of £11,730.40, so these probably aren't a major concern, but
>   ideally any reconciling difference should be investigated and cleared down to zero
>   where possible, as best practice.
>
> Overall, the numbers look broadly consistent, though I'd recommend following up on the
> two small differences to fully close them out. Let me know if you can share more detail
> (e.g. what's driving the £340 and £280 differences) and I can help you assess whether
> they need to be written off, adjusted, or carried forward.

**SKILL output** (inputs: all required box/reconciliation figures filled in; optional
`preparer_notes`, `opening_vat_balance`, `hmrc_total`, `zero_rated_sales`,
`filing_deadline` all left blank — a weak/lazy use of the skill; `output_type:
manager_review`):

> ## Manager Review — 31 May 2026
>
> **Risk Rating: RED**
>
> Two of four primary reconciliation checks are outside tolerance and neither carries a
> preparer note, so this file cannot be signed off as AMBER on the information currently
> held.
>
> **Key Figures**
> Net VAT due to HMRC of £11,730.40 (Box 5), reconciling correctly to Box 1 less Box 4
> (£18,240.60 − £6,510.20). Effective output rate of 20.0% on Box 6 net sales of £91,203.
>
> **Exceptions**
> - VAT Control (ref 2A): £340.00 difference — [FAIL ✗]. No preparer note provided; cannot
>   be assessed as a timing difference or genuine error on the information given.
> - Aged Receivables vs Balance Sheet (ref 3B): £280.00 difference — [FAIL ✗]. No preparer
>   note provided.
> - Output VAT Proof (ref 2C): £0.30 difference — [PASS ✓].
> - Aged Payables vs Balance Sheet (ref 3A): £0.00 difference — [PASS ✓].
>
> **Recommended Focus**
> Both failed checks require an explanation from the preparer before this file can be
> downgraded from RED. Obtain and document the root cause of the £340 control account
> difference and the £280 receivables difference before filing.

### Tier: GOOD

**Raw prompt (no skill):**
> I'm reviewing the VAT return for Northfield Interiors for the quarter to 31 May 2026. Can
> you write a short review note I can put in the file? Numbers: output VAT (Box1)
> £18,240.60, input VAT (Box4) £6,510.20, net VAT due (Box5) £11,730.40, net sales (Box6)
> £91,203, net purchases (Box7) £32,551. VAT control account is out by £340 (a supplier
> credit note timing difference, already checked), and receivables vs balance sheet is out
> by £280 (customer overpayment sitting in suspense, will clear in June). Please give it a
> risk rating and flag anything that needs following up.

**RAW output:**
> **VAT Review Note — Northfield Interiors Ltd — Quarter to 31 May 2026**
>
> **VAT position:** Output VAT of £18,240.60 (Box 1) less input VAT of £6,510.20 (Box 4)
> gives a net amount due to HMRC of £11,730.40 (Box 5), which agrees. Net sales of £91,203
> (Box 6) against net purchases of £32,551 (Box 7) implies an effective output VAT rate of
> approximately 20%, consistent with the standard rate.
>
> **Reconciliation:**
> - VAT control account: out by £340. Explained as a timing difference relating to a
>   supplier credit note — already reviewed and understood, so this can be treated as low
>   risk.
> - Receivables vs balance sheet: out by £280, relating to a customer overpayment held in
>   suspense, expected to clear in June. Also low risk given it's already identified and
>   has a clear resolution date.
>
> **Risk rating:** AMBER-LOW. Both variances are small in value, fully explained, and have
> a resolution path, but they should still be cleared before the file is closed off for the
> quarter.
>
> **Follow-up:** Confirm the suspense item clears as expected in June and update the file
> once resolved.

**SKILL output** (inputs as WEAK tier, plus one preparer note covering only the control
diff: `["VAT control diff of £340 relates to a supplier credit note processed in the VAT
return period but posted to the nominal ledger one day after quarter-end cut-off; timing
difference only, no cash impact."]`; other optional fields still blank):

> ## Manager Review — 31 May 2026
>
> **Risk Rating: RED**
>
> One of two failed checks carries a preparer note; the other does not, so this file cannot
> yet be signed off as AMBER.
>
> **Key Figures**
> Net VAT due to HMRC of £11,730.40 (Box 5), reconciling correctly to Box 1 less Box 4
> (£18,240.60 − £6,510.20). Effective output rate of 20.0% on Box 6 net sales of £91,203.
>
> **Exceptions**
> - VAT Control (ref 2A): £340.00 difference — [FAIL ✗]. Explained: a supplier credit note
>   processed in-period but posted to the nominal ledger one day after quarter-end
>   cut-off — a timing difference only, no cash impact.
> - Aged Receivables vs Balance Sheet (ref 3B): £280.00 difference — [FAIL ✗]. No preparer
>   note provided; cannot be assessed on the information given.
> - Output VAT Proof (ref 2C): £0.30 difference — [PASS ✓].
> - Aged Payables vs Balance Sheet (ref 3A): £0.00 difference — [PASS ✓].
>
> **Recommended Focus**
> Obtain and document the cause of the £280 receivables difference. Once explained, and
> provided it does not exceed £500, this file would move to AMBER.

### Tier: AMAZING

**Raw prompt (no skill):**
> You are reviewing the VAT working papers for Northfield Interiors Ltd for the quarter to
> 31 May 2026 (UK VAT Standard scheme, VAT reg GB 456123789). Apply these four
> reconciliation checks: VAT Control (opening balance + Box1 − Box4 − HMRC payments in
> period, must agree to the nominal within £1), Output VAT Proof ((Box6 − zero-rated
> sales) × 20% must equal Box1 within £1), Aged Payables vs Balance Sheet (within £1), Aged
> Receivables vs Balance Sheet (within £1). Risk rating: GREEN if all four pass; AMBER if
> one or two fail by £1–£500 and each has a preparer note; RED if any fails by more than
> £500, multiple fail unexplained, or any difference can't be explained. Data: Box1
> £18,240.60, Box4 £6,510.20, Box5 £11,730.40, Box6 £91,203, Box7 £32,551, opening VAT
> balance £3,400, HMRC payments in quarter £15,200, zero-rated sales £0. VAT control diff
> £340 — supplier credit note processed in-period but posted to the nominal ledger one day
> after quarter-end cut-off, timing only, no cash impact. Output VAT proof diff −£0.30.
> Box 6 vs cumulative TB sales diff £2,100 (informational). AP vs BS diff £0. AR vs BS diff
> £280 — customer overpayment held in suspense, agreed with credit control on 3 Jun 2026,
> due to clear in June. Filing deadline 7 Jul 2026. Write a manager review note: risk
> rating and exception count first, then key figures, then exceptions, then recommended
> focus, two to four sentences per section, £ with comma separators and 2dp, GREEN/AMBER/RED
> in capitals, [PASS ✓]/[FAIL ✗] tags.

**RAW output:**
> **Manager Review — Northfield Interiors Ltd — Quarter to 31 May 2026**
>
> **Risk Rating: AMBER — 2 exceptions**
> Two of four primary reconciliation checks are outside the £1 tolerance, both within the
> £1–£500 band, and both carry a preparer explanation, so this file rates AMBER rather than
> RED.
>
> **Key Figures**
> Net VAT due to HMRC of £11,730.40 (Box 5), correctly reconciling to Box 1 of £18,240.60
> less Box 4 of £6,510.20. Effective output rate of 20.0% on Box 6 net sales of £91,203.00.
> Filing and payment deadline is 7 Jul 2026.
>
> **Exceptions**
> - VAT Control (ref 2A): £340.00 difference — [FAIL ✗]. Supplier credit note processed
>   within the VAT return period but posted to the nominal ledger one day after cut-off; a
>   timing difference only, with no cash impact.
> - Aged Receivables vs Balance Sheet (ref 3B): £280.00 difference — [FAIL ✗]. Customer
>   overpayment held in suspense, agreed with credit control on 3 Jun 2026, due to clear in
>   June.
> - Output VAT Proof (ref 2C): £0.30 difference — [PASS ✓].
> - Aged Payables vs Balance Sheet (ref 3A): £0.00 difference — [PASS ✓].
> - Box 6 vs cumulative TB sales (ref 2C, informational): £2,100.00 difference — noted, does
>   not affect the risk rating.
>
> **Recommended Focus**
> No further action required to file this quarter's return; both exceptions are timing
> differences with a documented resolution path. Confirm the AR suspense item clears as
> expected in June before next quarter's review.

**SKILL output** (inputs: all fields filled, both preparer notes present, `output_type:
manager_review`):

> ## Manager Review — 31 May 2026
>
> **Risk Rating: AMBER**
>
> Two of four primary checks fail, both within the £1–£500 band, and both carry a preparer
> note, so this file rates AMBER.
>
> **Key Figures**
> Net VAT due to HMRC of £11,730.40 (Box 5), reconciling correctly to Box 1 less Box 4
> (£18,240.60 − £6,510.20). Effective output rate of 20.0% on Box 6 net sales of £91,203.00.
> Filing and payment deadline: 7 Jul 2026.
>
> **Exceptions**
> - VAT Control (ref 2A): £340.00 difference — [FAIL ✗]. Supplier credit note processed
>   in the VAT return period but posted to the nominal ledger one day after quarter-end
>   cut-off — timing difference only, no cash impact.
> - Aged Receivables vs Balance Sheet (ref 3B): £280.00 difference — [FAIL ✗]. Customer
>   overpayment held in suspense, agreed with credit control on 3 Jun 2026, due to clear
>   in June.
> - Output VAT Proof (ref 2C): £0.30 difference — [PASS ✓].
> - Aged Payables vs Balance Sheet (ref 3A): £0.00 difference — [PASS ✓].
>
> **Recommended Focus**
> Both exceptions are documented timing differences with a clear resolution path; no
> further investigation is required to file. Confirm the AR suspense item clears as
> expected in June.

---

## 3. `board_pack_narrative` — Solstice Outdoor Ltd, September 2026

**Underlying facts:** Revenue £742,000 actual vs £705,000 budget (+£37,000, +5.2%,
favourable). EBITDA £118,500 actual vs £131,000 budget (−£12,500, −9.5%, adverse). Cash
£356,000 at month end. Risk: fabric supplier issuing a 9% price increase from November, not
yet reflected in cost budgets, ~£40k/quarter margin pressure if unmitigated; warehouse
lease renewal due Q1 2027 with landlord signalling a material rent increase. Opportunity: a
new wholesale partnership with a national outdoor retailer signed in September, ~£180k
incremental revenue expected in Q4 at slightly lower margin, first shipment late October.

### Tier: WEAK

**Raw prompt (no skill):**
> explain these numbers for the board — revenue 742k vs 705k budget, EBITDA 118.5k vs 131k
> budget, cash 356k. supplier costs going up. new wholesale deal signed.

**RAW output:**
> Sure, here's an explanation of the numbers:
>
> Revenue came in at £742k against a budget of £705k, which is a positive variance of
> around £37k, or about 5%. That's a good result and suggests the business is trading ahead
> of expectations on the top line.
>
> EBITDA, however, was £118.5k versus a budget of £131k, which is a shortfall of about
> £12.5k, or roughly 9.5%. This is a bit concerning since revenue was actually ahead of
> plan, which suggests that costs or margins were worse than expected somewhere in the
> P&L — it's worth noting that you mentioned supplier costs going up, which could well be
> the cause.
>
> Cash at £356k is a separate figure and without more context (e.g. what it was last month,
> or what the budget was) it's hard to say whether this is a good or bad position, though it
> looks like a reasonably healthy balance in absolute terms.
>
> You also mentioned a new wholesale deal being signed — that's a positive development and
> could help offset some of the cost pressure going forward, depending on the scale and
> timing of the revenue it brings in.
>
> If you'd like, I can turn this into a more polished paragraph for the board pack — just
> let me know if you can share a bit more detail on the supplier cost increase and the
> wholesale deal so I can be specific about the numbers involved.

**SKILL output** (inputs: all required financial headline fields filled in; `top_risks`
filled with the minimum viable one-liner "supplier costs going up, margin might be
squeezed"; `top_opportunities` left blank, since it's optional):

> Solstice Outdoor delivered EBITDA of £118,500 in September 2026, £12,500 behind budget
> (9.5% adverse), despite revenue of £742,000 coming in £37,000 ahead of plan (5.2%
> favourable). The gap between strong top-line performance and a soft EBITDA result points
> to cost pressure below the revenue line during the month. Cash stood at £356,000 at month
> end. The board should be aware that supplier costs are rising, which is starting to
> squeeze margin, though the scale and timing of this pressure has not yet been quantified.
> No further detail is available on mitigating actions at this stage, and management will
> update the board once the cost impact has been assessed. The full-year outlook will be
> reviewed once the extent of the supplier cost increase is clearer.

### Tier: GOOD

**Raw prompt (no skill):**
> Can you write a short executive summary for our September 2026 board pack (Solstice
> Outdoor Ltd)? Revenue was £742k vs £705k budget, EBITDA £118.5k vs £131k budget, cash
> £356k. Main risk is our fabric supplier raising prices ~9% from November, plus our
> warehouse lease renewal coming up. We did sign a new wholesale deal in September which
> should help Q4. Keep it around half a page, written for a board that includes non-finance
> NEDs.

**RAW output:**
> Solstice Outdoor delivered a strong revenue performance in September 2026, with sales of
> £742,000 coming in £37,000 (5.2%) ahead of budget. However, EBITDA of £118,500 was
> £12,500 (9.5%) below the £131,000 target, reflecting cost pressures that offset the
> revenue upside. Cash remained healthy at £356,000 at month end.
>
> Looking ahead, the board should be aware of two emerging risks. Our fabric supplier has
> signalled a price increase of approximately 9% from November, which will put pressure on
> margins if not mitigated through pricing or sourcing action. In addition, our warehouse
> lease is due for renewal in the near term, and early signals from the landlord suggest a
> material rent increase is likely.
>
> On a more positive note, we signed a significant new wholesale partnership in September,
> which is expected to be a meaningful contributor to revenue in the final quarter of the
> year and provides some confidence in our ability to offset the cost headwinds described
> above.
>
> We will continue to monitor the supplier and lease situations closely and will update the
> board on mitigation plans and their expected financial impact at the next meeting.

**SKILL output** (inputs as WEAK tier, plus `top_risks` with quantification and timing, and
`top_opportunities` with a brief note but not full detail):

> `top_risks`: "Fabric supplier raising prices ~9% from November, will hit margin.
> Warehouse lease renewal coming up too, landlord signalling a rent increase."
> `top_opportunities`: "Signed a new wholesale deal in September, should help Q4 revenue."

> Solstice Outdoor delivered EBITDA of £118,500 in September 2026, £12,500 behind budget
> (9.5% adverse), even as revenue of £742,000 came in £37,000 ahead of plan (5.2%
> favourable), pointing to margin pressure below the revenue line. Cash remained solid at
> £356,000 at month end. The board should be aware that our fabric supplier is raising
> prices by approximately 9% from November, which will pressure margin unless mitigated,
> and that our warehouse lease is coming up for renewal with the landlord signalling a rent
> increase. On a more positive note, a new wholesale deal signed in September is expected to
> support Q4 revenue. Full-year guidance will be reviewed once the scale of the supplier
> price increase and lease terms are confirmed.

### Tier: AMAZING

**Raw prompt (no skill):**
> Write a 5–7 sentence board-pack executive summary for Solstice Outdoor Ltd, September
> 2026, for a board that includes non-finance NEDs — no jargon, no headings or bullet
> points, single flowing paragraph. Financial headlines: revenue £742,000 actual vs
> £705,000 budget (+5.2% favourable); EBITDA £118,500 actual vs £131,000 budget (−9.5%
> adverse); cash £356,000 at month end. Open with the headline EBITDA position in one
> punchy sentence, then cover revenue and cash in two short sentences. Risks to name (without
> over-detailing): our fabric supplier has issued a 9% price increase effective November,
> not yet reflected in cost budgets, representing approximately £40k of margin pressure per
> quarter if unmitigated; our warehouse lease renewal is due in Q1 2027 and the landlord is
> signalling a material rent increase. Opportunity to note: a new wholesale partnership with
> a national outdoor retailer, signed in September, expected to add approximately £180,000
> of incremental revenue in Q4 at a slightly lower margin, with the first shipment scheduled
> for late October. Close with a forward-looking sentence giving guidance for the remainder
> of the year.

**RAW output:**
> Solstice Outdoor's EBITDA of £118,500 in September fell £12,500 short of budget, a 9.5%
> miss, even as the business delivered a strong top line. Revenue of £742,000 was £37,000
> ahead of plan (5.2% favourable), while cash held firm at £356,000 at month end. The margin
> shortfall reflects two emerging cost pressures the board should be aware of: our fabric
> supplier has issued a 9% price increase effective November, worth an estimated £40,000 of
> quarterly margin pressure if left unmitigated, and our warehouse lease renewal in Q1 2027
> is likely to bring a material rent increase. Set against this, a new wholesale
> partnership with a national outdoor retailer signed in September is expected to add
> around £180,000 of incremental revenue in the fourth quarter, with the first shipment due
> in late October. Taking both the cost pressures and the new partnership into account,
> full-year guidance is maintained for now, with an update to follow once pricing
> mitigations for the supplier increase are agreed.

**SKILL output** (inputs: all fields filled with the same full detail):

> Solstice Outdoor delivered EBITDA of £118,500 in September 2026, £12,500 behind budget
> (9.5% adverse), as emerging cost pressures offset a strong top line. Revenue of £742,000
> exceeded plan by £37,000 (5.2% favourable), while cash remained solid at £356,000 at
> month end. The primary risk heading into Q4 is a 9% price increase from our fabric
> supplier effective November, representing approximately £40,000 of quarterly margin
> pressure if unmitigated, alongside a warehouse lease renewal due in Q1 2027 where the
> landlord is signalling a material rent increase. On the positive side, a new wholesale
> partnership with a national outdoor retailer, signed in September, is expected to add
> approximately £180,000 of incremental revenue in Q4, with the first shipment scheduled for
> late October. Full-year guidance is maintained, with a further update once pricing
> mitigation for the supplier increase has been agreed.

---

## Analysis

### Does the skill-scaffolded WEAK prompt beat the RAW amazing prompt?

**No — not outright, and the results don't support the strong form of the hypothesis.**
Across all three prompts, RAW-amazing and SKILL-amazing land in the same place: both are
polished, complete, board-ready outputs, because an amazing raw prompt already *contains*
essentially the same instructions the skill's `system_prompt` encodes (structure, tone,
conventions, what to cover). At that end of the spectrum the skill adds consistency and
speed of authoring, not a quality ceiling the raw prompt couldn't reach on its own.

At the WEAK end, the skill clearly outperforms RAW-weak on **structure, tone discipline,
and reliability of the numbers**, but it does not fully compensate for missing input
content — because there's a difference between "the model wasn't told how to format
this" and "the model wasn't given the facts." The skill can't be told a driver that was
never entered as `analyst_notes`. What it *can* do, and does reliably, is:

- Refuse to fabricate a driver it wasn't given (`variance_commentary` rule 5, `vat_rec`
  rule 7) — RAW-weak, with no such rule, invents plausible-sounding explanations or
  hedges with "it's worth noting" instead.
- Apply a fixed, correct materiality/risk methodology every time — SKILL-weak for
  `vat_rec` correctly rates the file RED because two failed checks have no preparer note,
  matching the documented risk-rating rules exactly. RAW-weak, given the same numbers, is
  more likely to eyeball the differences as "small" and wave them through — a real risk in
  a compliance context, where an unexplained VAT control diff is not "probably fine."
  This is the single clearest place the skill *did* out-perform a good-faith weak raw
  ask: it enforced a rule a human or generic model would be tempted to skip.
- Hold format and voice constant — no filler phrases, correct (F)/(A) labelling, third
  person, consistent section headers — every time, regardless of how much the user typed.

So the honest verdict is a **partial confirmation, tier-dependent**:

- **WEAK vs WEAK:** skill scaffolding wins clearly. Same facts, but SKILL-weak is more
  disciplined, safer (it flags what it doesn't know rather than guessing), and immediately
  usable; RAW-weak reads like a first draft that still needs an accountant's edit pass.
- **WEAK-skill vs AMAZING-raw:** the hypothesis does *not* hold in its strongest form.
  RAW-amazing is still the better output of the two, because it supplies real drivers
  (the two contract mobilisations, the HVAC callouts, the credit note timing story) that
  WEAK-skill simply doesn't have and — correctly — won't invent. A weak *skill* input is
  still a weak input. Scaffolding upgrades the presentation and enforces the methodology;
  it cannot manufacture missing facts.
- **GOOD tier:** this is where scaffolding earns its keep most convincingly. GOOD-raw is
  already competent, but GOOD-skill matches it on content and exceeds it on
  cross-prompt consistency (identical structure and phrasing conventions every time,
  useful when a finance team is producing a dozen of these a month) and on catching things
  a person drafting from scratch might skip, such as the reconciliation check on
  `variance_commentary`'s subtotal line, or explicitly separating a "screened out" line
  under a materiality threshold rather than silently omitting it.

### Where scaffolding helps most

1. **Discipline under compliance-shaped rules** (`vat_rec`): a fixed risk-rating
   methodology applied identically to WEAK, GOOD, and AMAZING inputs. This is the
   strongest result in the whole experiment — a generic LLM given the same raw numbers
   consistently under-called the risk (treating unexplained diffs as "probably fine"),
   where the skill correctly refused to.
2. **Structural completeness** — the skill's output is never missing a required section
   (Screened Out, Net Position, Recommended Focus) even when the underlying input is thin;
   a plain LLM asked a vague question skips sections it wasn't specifically told to
   include.
3. **Refusing to fabricate** — every SKILL output above correctly states "no driver
   provided" rather than inventing one, which is exactly the behaviour you want in
   something that might end up, unedited, in a board pack or a VAT file note. RAW-weak
   outputs above show the opposite instinct: hedge, guess, or ask a follow-up question
   that a batch-run tool can't actually receive an answer to.

### Where scaffolding does NOT fully compensate

1. **Missing facts stay missing.** No amount of system-prompt engineering recovers a
   driver, an explanation, or a number the user never entered. `variance_commentary`
   WEAK-skill and `board_pack_narrative` WEAK-skill both read noticeably thinner than
   their AMAZING-skill counterparts for exactly this reason.
2. **An excellent raw prompt is genuinely excellent.** When a user already knows to
   specify structure, tone, conventions, and facts up front, a plain LLM call gets very
   close to the skill's quality — because at that point the user has essentially
   hand-written their own ad hoc system prompt inside the message. The skill's edge there
   is convenience and consistency across many runs, not a step-change in single-shot
   quality.
3. **The skill's rigidity can read as terse when data is thin.** SKILL-weak outputs above
   are correct and safe but can feel clipped ("No driver has been provided for this
   variance.") — a human reviewer would likely prefer this to a fabricated driver, but it
   is a real, honest trade-off worth being aware of when demoing the library to
   non-technical stakeholders who expect every output to look "finished."

### Verdict

The hypothesis holds in its **realistic, moderate form** — a WEAK raw ask fed through a
well-built skill is safer, more structurally complete, and more consistent than the same
weak ask made directly of a model, and for the compliance-flavoured `vat_rec` prompt the
skill actively catches a risk a generic LLM response tended to miss. But it does **not**
hold in the strong form suggested by "can make a weak prompt outperform an amazing one" —
across all three prompts tested, an amazing raw prompt supplying real facts and real
structure still produces a materially more complete and specific output than a weak input
run through the same skill. Scaffolding is best understood as a *floor-raiser and
consistency guarantee*, not a substitute for the underlying facts a good analyst would have
included anyway. The library's value proposition is strongest for GOOD-tier, real-world
usage — a management accountant who has the numbers and roughly knows what they want — where
the skill turns a competent draft into a materially more reliable, board-ready one, every
time, at zero extra authoring effort per run.
