Shared ChatGPT conversation "Explain probability calibration", 2026-09-24 06:06 UTC to 2026-09-29 04:52 UTC, model `gpt-5-6-thinking`.
Source: https://chatgpt.com/share/6abfef2c-e9fc-83e9-92a4-6affb200159d
Transcribed 2026-10-02: every user and assistant message verbatim, with the tool steps shown between them in italics.

Q: what are "well calibrated probabilities"... and what is the claim Jev is making about the calibration of its probabilities?

---

A:

I’ll separate two things: what “well calibrated” means mathematically, and the specific empirical claim Jev makes about its own probability outputs.

*[thinking: Explaining calibration; Explained calibration]*
*[thinking: Searched 30 websites]*
*[Worked for 38s]*

A **well-calibrated probability** is a probability whose numerical value actually corresponds to how often the event occurs.

If a model makes 1,000 predictions and, for 100 of them, says:

> **P(event) = 0.80**

then among those ~100 cases, the event should actually happen about **80 times**.

That is calibration.

So an ideal reliability curve looks like:

| Model says | Event actually occurs |
|---:|---:|
| 10% | ~10% |
| 30% | ~30% |
| 50% | ~50% |
| 70% | ~70% |
| 90% | ~90% |

Formally, in the binary case:

\[
P(Y=1\mid \hat p=p) = p
\]

This is importantly **different from accuracy**.

A model can be extremely accurate but badly calibrated. Imagine a model that's right 90% of the time but says `0.999` on almost every prediction. It's accurate, but overconfident.

Conversely, suppose 60% of emails really are spam, and a totally dumb model always says:

\[
P(\text{spam})=0.60
\]

That model can actually be **perfectly calibrated** while having rather poor discriminatory power. Calibration tells you whether the *numbers mean what they say*, not whether the model is good at separating cases.

### What Jev is claiming

This is actually one of Jev's central claims.

TypeSafe says Jev is trained using **RLCD — Reinforcement Learning for Calibrated Decisions**. Their launch post says Jev is optimized for:

> “Calibrated decisions: answers with epistemically honest probabilities on System One tasks.”

and says:

> “All answers are accompanied with calibrated probabilities and confidence scores.”  ([TypeSafe AI](https://typesafe.ai/blog/introducing-system-one-models-and-jev))

Their own explanation of calibration gives essentially the definition above: outcomes assigned `0.2` should occur about 20% of the time, outcomes assigned `0.8` about 80%, etc. They explicitly note that this is a property of **groups of predictions**, not a guarantee about an individual prediction.  ([Learn Jev](https://learnjev.com/concepts/calibration?utm_source=chatgpt.com))

So if Jev gives you:

```text
BUY:   0.72
HOLD:  0.20
SELL:  0.08
```

the intended interpretation is **not merely**:

> "BUY got the largest model score."

It is intended to mean something much stronger:

> "Cases to which Jev assigns ~72% probability to BUY should actually have BUY as the correct outcome about 72% of the time."

That's a **very valuable property** for the RL/bandit ideas we were discussing. If `0.72` is genuinely a probability rather than an arbitrary model score, you can do expected-value calculations directly:

\[
EV(a)=\sum_s P(s\mid x,a)R(s,a)
\]

rather than first having to learn what something like a neural-network score of `0.72` actually means.

### There is a catch — and it's a pretty important one

Calibration is fundamentally **distribution-dependent**.

Suppose Jev is perfectly calibrated on its training/evaluation population. That does **not** imply it will remain calibrated on:

- your particular stocks,
- Kalshi questions,
- today's market regime,
- your unusual prompt/schema,
- events 3–12 months in the future,
- rare-event predictions.

For example, a classifier might produce `0.70` for "spam" on two companies' emails. If 70%-score emails really are spam 70% of the time at company A but 45% at company B, the exact same model is calibrated on one distribution and miscalibrated on the other.

This is why a recent critique points out that a universal claim of calibration for arbitrary user distributions cannot really hold without qualification.  ([Alex Molas](https://www.alexmolas.com/2026/09/23/jev-cant-be-calibrated.html?utm_source=chatgpt.com))

And the evidence for Jev so far is **mixed**, rather than establishing universal calibration. One independent API audit summarizes results ranging from very good calibration on one test (MMLU probe, ECE ≈ `0.031`) to substantial overconfidence on another (phishing, ECE ≈ `0.154`).  ([GitHub](https://github.com/jujumilk3/jev-calibration-audit?utm_source=chatgpt.com)) Another larger recent study found calibration degraded substantially on an unseen synthetic rule task even though it looked good on several public benchmarks.  ([JevDirectory.org](https://www.jevdirectory.org/resources/jev-ood-calibration?utm_source=chatgpt.com))

More importantly, TypeSafe's launch materials do **not currently publish a standard calibration benchmark with reliability diagrams/ECE/Brier scores establishing the broad claim**. Their published evaluations focus more on workflow intelligence, speed, cost and type safety.  ([TypeSafe AI](https://typesafe.ai/blog/introducing-system-one-models-and-jev))

### The distinction I'd keep in your head

There are really three levels:

**1. Raw model score**

`0.82` means only "the model prefers this pretty strongly."

**2. Monotonic confidence**

`0.82` predictions are more accurate than `0.62` predictions.

**3. Calibrated probability**

`0.82` means that, over comparable cases, the event actually happens **~82% of the time**.

Jev is explicitly claiming **#3**, not merely #1 or #2. TypeSafe even calls these probabilities “epistemically honest.”  ([TypeSafe AI](https://typesafe.ai/blog/introducing-system-one-models-and-jev))

And that's why the Jev idea is interesting. If the claim holds **on your distribution**, its outputs become much more useful for decision theory, contextual bandits, betting, position sizing, abstention, routing, and exploration/exploitation than ordinary LLM confidence scores.

For the stock/Kalshi project we were discussing, though, I would **measure Jev's calibration ourselves**. The nice thing is that Jev is so cheap that we could run tens or hundreds of thousands of historical decisions, make a reliability diagram, calculate Brier score/ECE, and determine whether a Jev `0.70` actually means 70% **on financial/event data**. That experiment could materially change how useful Jev is for the RL ideas we were considering.

Sources: [TypeSafe AI](https://typesafe.ai/blog/introducing-system-one-models-and-jev), [Learn Jev](https://learnjev.com/concepts/calibration?utm_source=chatgpt.com), [Alex Molas](https://www.alexmolas.com/2026/09/23/jev-cant-be-calibrated.html?utm_source=chatgpt.com), [GitHub](https://github.com/jujumilk3/jev-calibration-audit?utm_source=chatgpt.com), [JevDirectory.org](https://www.jevdirectory.org/resources/jev-ood-calibration?utm_source=chatgpt.com)

---

Q: could you learn a "calibration mapping" from jev probabilities to custom probabilities in a particular domain?

---

A:

*[Worked for a few seconds]*

Yes. That is a very standard idea, and it is probably the first thing I would try with Jev in a specialized domain.

You can learn a function

\[
p_{\text{custom}} = f(p_{\text{Jev}})
\]

from historical predictions and observed outcomes.

For example, suppose Jev says `0.80` on 2,000 historical stock predictions, but only 65% of those predictions were actually correct. Your learned calibration mapping might turn:

\[
0.80 \rightarrow 0.65
\]

Likewise:

\[
0.60 \rightarrow 0.54
\]

\[
0.90 \rightarrow 0.76
\]

Then downstream decision-making uses your calibrated probability rather than Jev's raw one.

There are several common ways to learn \(f\):

- **Platt scaling / logistic calibration:** learn \(p'=\sigma(a\,\text{logit}(p)+b)\). Very simple and data-efficient.
- **Isotonic regression:** learn an arbitrary monotonic mapping. Good when you have lots of examples and don't want to assume a sigmoid-shaped correction.
- **Beta calibration:** often especially appropriate for probabilities because it can correct asymmetric under/overconfidence.
- **Temperature scaling:** common for neural classifiers, though usually more natural when you have logits rather than just probabilities.
- **Multiclass calibration:** if Jev gives BUY/HOLD/SELL probabilities, use methods such as vector scaling or Dirichlet calibration rather than independently recalibrating each number.

The more interesting version for your use case is to make the calibration **conditional**:

\[
p_{\text{custom}} =
f(p_{\text{Jev}}, x)
\]

where \(x\) includes things like:

\[
x =
\{\text{asset type, horizon, volatility, regime, event category, liquidity, Jev task type, etc.}\}
\]

So you might discover:

> Jev's 80% means ~78% for large-cap earnings predictions, ~61% for biotech, ~73% at a 1-day horizon, and ~55% at a 30-day horizon.

Then you're learning a **domain-specific calibration layer**, rather than one global correction curve.

For the stock/Kalshi system, I think this is particularly promising because you could make it hierarchical:

\[
P(Y|J,x)
\]

with something like

```text
Jev probability
      ↓
global calibration
      ↓
domain calibration
      ↓
regime/category calibration
      ↓
final probability
```

You'd want enough regularization that small buckets don't wildly overfit.

There is also an even better formulation if you're collecting data continuously: make the calibrator **online/adaptive**. Markets change, so a fixed mapping learned on 2024–2025 data might stop being right in 2026. You could continuously update:

\[
f_t(p)
\]

with recent outcomes, possibly with recency weighting.

One subtle point: calibration cannot fix lack of information. If Jev assigns almost every case a probability between 0.55 and 0.65, calibration can make those probabilities more truthful, but it cannot magically create discrimination between easy and hard cases. You want both:

\[
\textbf{discrimination} + \textbf{calibration}
\]

A very nice diagnostic would therefore be to measure both **AUC/ranking performance** and **Brier score/log loss/calibration error**.

For your Jev experimentation, I'd probably start with three baselines:

1. Raw Jev probability.
2. One-dimensional beta or isotonic calibration of Jev probability.
3. Contextual calibrator using Jev probability + a small number of domain features.

Then test all three strictly out-of-sample.

If #3 materially beats #2, that's especially interesting, because you've effectively turned Jev into a cheap **prior probability generator**, while your own learned layer adapts that prior to the peculiarities of stocks or Kalshi.

---

Q: # Selected text:

## Selection 1
prior probability generator

## My request:
what do you mean exactly?  I mean, its generating "Jev's prior probabilities" by definition... but is there something more interesting about these priors?

---

A:

*[Worked for 6s]*

Yes — there is a more interesting interpretation, but I used “prior” a little loosely.

I did **not** mean “prior” merely as “whatever probability Jev spits out first.” The potentially useful idea is that Jev's probability can serve as a **general-purpose semantic baseline**, and your domain-specific model only has to learn how that baseline should be corrected.

For example, instead of learning from scratch

\[
P(Y=1\mid x)
\]

you can model

\[
\operatorname{logit} P(Y=1\mid x)
=
\operatorname{logit} p_{\text{Jev}}
+
g(x)
\]

where \(g(x)\) is your learned domain-specific correction.

That is interesting because Jev may already have compressed a lot of complicated information into one number:

- textual evidence,
- relationships among concepts,
- common-sense reasoning,
- background knowledge,
- uncertainty from ambiguous evidence,
- interactions that would be hard to hand-engineer.

Your model then doesn't need to relearn all of that. It learns things like:

> “Jev is systematically too optimistic on biotech catalyst questions.”

or

> “When Jev says 70% on short-horizon earnings questions during high-volatility regimes, the real number is closer to 58%.”

### There is a Bayesian-looking interpretation

Writing it in odds form makes this especially clear:

\[
\frac{p_{\text{custom}}}{1-p_{\text{custom}}}
=
\frac{p_{\text{Jev}}}{1-p_{\text{Jev}}}
\times
e^{g(x)}
\]

This looks like:

\[
\text{posterior odds}
=
\text{prior odds}
\times
\text{likelihood ratio}
\]

So you could conceptually treat Jev's output as an **amortized learned prior**, while your specialized model supplies an empirical likelihood correction based on your particular domain.

That's stronger than ordinary calibration.

A simple calibration map does:

\[
p_{\text{custom}}=f(p_{\text{Jev}})
\]

It says, essentially:

> “When Jev says 80%, historically it means 67% here.”

The richer version does:

\[
p_{\text{custom}}=f(p_{\text{Jev}},x)
\]

and says:

> “What should Jev's 80% mean **in this particular situation**?”

### Why Jev might be especially useful for this

Suppose you're predicting Kalshi outcomes.

You could build a conventional ML model from structured variables:

```text
market price
volume
time remaining
category
historical volatility
polling data
...
```

But there are potentially thousands of unstructured considerations. Jev could consume something like:

> “Given this market question, these news stories, the current polling information, and these arguments, what is the probability the event occurs?”

and collapse that enormous semantic state into:

\[
p_\text{Jev}=0.73
\]

Your cheap statistical learner can then take:

\[
[0.73,\ \text{market price},\ \text{category},\ \text{time-to-resolution}, ...]
\]

and learn the actual outcome probability.

In that sense, Jev becomes almost like a **learned feature extractor whose feature happens to have the semantics of a probability**.

That is quite useful.

### And there's an even more interesting possibility

You don't necessarily have to give your downstream model only **one** Jev probability.

You could ask Jev several carefully chosen probabilistic questions:

\[
\begin{aligned}
P(\text{event occurs}) &= .71\\
P(\text{evidence is misleading}) &= .18\\
P(\text{current trend persists}) &= .64\\
P(\text{important unknown information exists}) &= .37\\
P(\text{market consensus is wrong}) &= .29
\end{aligned}
\]

Now Jev is generating a small **probabilistic latent representation** of the situation.

Then a learned model maps:

\[
(p_1,p_2,\ldots,p_k,x)
\rightarrow P(Y)
\]

That strikes me as potentially much more powerful than merely “recalibrating Jev.”

You'd be using Jev as a very cheap **semantic probability-feature generator**, then letting conventional ML learn which Jev judgments are useful, how much to trust them, and under what conditions.

One important caveat: I wouldn't call \(p_{\text{Jev}}\) a *formal Bayesian prior*. Jev hasn't necessarily generated that number according to a Bayesian generative model. “Learned/amortized prior” is an analogy describing how you can **use** the number downstream.

But that analogy leads directly to a potentially good architecture:

\[
\boxed{
\text{raw world data}
\rightarrow
\text{Jev probabilistic features}
\rightarrow
\text{small adaptive ML model}
\rightarrow
\text{domain-calibrated }P(Y)
}
\]

For the stock/Kalshi RL ideas, I think **that formulation is considerably more interesting than simple post-hoc calibration**.

---

If you want, I can:

- Explain how Jev probabilities serve as semantic baselines
- Describe Bayesian interpretation of domain calibration
- Expand on using multiple Jev probabilities as latent features
