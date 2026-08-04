# Prompting with Customer Context: Glossaries, Examples, Taboos

**Phase 5 · Lesson 05 · ~1h**

## PROBLEM

The pilot's classification accuracy is stuck at 78%. The champion is patient but the VP is not. You look at the misclassifications: the model keeps labeling internal-transfer tickets as "customer complaints" because the ticket text says "unhappy" a lot; it can't tell a "Series B customer" from a "Series C customer" because it doesn't know those are internal tier codes at this company; and worst, it once cheerfully described a competitor product by name in a customer-facing response — a fireable offense, per the customer's own policy. The base model is perfectly capable; nobody told it any of this. The prompt is 60 words of "You are a helpful assistant that classifies tickets" and nothing else. The customer's context — their vocabulary, their edge cases, their forbidden topics — has to be *in* the prompt or the model may as well be answering for a different company.

## INTUITION

A production prompt for a customer engagement has four layers, each doing a distinct job:

**Role and scope.** One sentence naming the assistant's job and its boundary. "You are the internal support-triage assistant for Acme Corp. You classify inbound tickets into one of the following categories:..." Boundary language is what stops the model from freelancing into adjacent tasks.

**Glossary.** The customer's jargon defined inline. "In Acme's vocabulary: 'Series B' refers to enterprise-tier customers on the legacy contract; 'Series C' refers to new-tier customers on the FY2024 contract. These are NOT company funding rounds." Two lines fix a whole class of errors that would have taken a month of fine-tuning otherwise.

**Few-shot examples.** Three to five worked examples showing the shape you want — including at least one edge case and one refusal. Examples teach in a way that instructions can't. But every example is a claim you now maintain: when the customer's process changes, the examples must too.

**Taboos and refusal path.** Explicit list of things the assistant must never do or say. "Never mention competitor names. If a request cannot be answered from the retrieved context, respond with 'I don't have that information' — do not guess." The refusal path is the taboo's escape hatch; without it, a well-drilled model will still improvise when cornered.

The prompt is a customer artifact. It gets versioned, reviewed by the SME, changelog'd. It is not a place for clever wording; it is a place for exhaustive, boring specificity.

## BUILD IT

A prompt template you can lift directly:

```python
PROMPT_TEMPLATE = """You are {ROLE} for {CUSTOMER}.

TASK: {TASK_DESCRIPTION}

GLOSSARY (customer-specific terminology):
{GLOSSARY_LINES}

RULES:
- Answer ONLY from the provided sources. If the sources do not contain
  the answer, respond exactly: "I don't have that information."
- {TABOO_LINES}
- Cite the source IDs of every fact you use, in the format [doc#chunk].

EXAMPLES:
{FEW_SHOT_EXAMPLES}

SOURCES:
{RETRIEVED_CONTEXT}

QUESTION: {USER_QUERY}

ANSWER:"""
```

The pieces come from separate files, versioned separately:

- `glossary.yaml` — SME owns, ~30-100 entries typical.
- `taboos.yaml` — legal/comms owns, ~5-15 entries.
- `examples.yaml` — you own, curated from actual customer traffic.

The assembly logic — the template above — you own too, but treat it as a stable contract. Every prompt change is a deploy; every deploy is an eval run (Lesson 06).

Glossary entry format:

```yaml
- term: "Series B"
  definition: "Enterprise-tier customer on the legacy contract"
  never_confuse_with: "Company funding round Series B"
```

The `never_confuse_with` field is not decoration; it becomes a negative constraint in the assembled prompt and catches the exact class of errors that "just add the glossary" misses.

## FIELD NOTES

- The customer will hand you the glossary "next week." They will not. Extract it yourself from their internal wiki, the top 100 acronyms in their tickets, and 20 minutes with a support lead. Show them a draft; they will happily fix it. A blank slate paralyzes SMEs; a straw-man activates them.
- Few-shot examples leak signal. If your examples all follow "category A -> polite response, category B -> polite response," the model will infer "always be polite." That's fine until category C is "escalate immediately" and it comes back polite. Diverse examples, including refusals and escalations, are non-negotiable.
- Taboos need audit. "Never mention competitor names" is easy to specify and hard to verify; write a post-generation check that greps for the taboo list and re-prompts on hit. The check is your evidence when legal asks.
- Prompt length is a cost lever the CFO will find. Every token in every request costs money and latency. Move stable content (glossary, examples) into a prefix that can be cached — the hosted APIs increasingly support prompt caching, and it's a 40-70% cost win on repetitive workloads.
- The customer will ask to "improve the prompt" mid-pilot. Refuse without an eval. Prompt edits without measurement have a coin-flip chance of regressing accuracy on cases you weren't looking at. Show them the eval harness (Lesson 06); make prompt edits a PR-style workflow.

## INTERVIEW ANGLE

Prompt-engineering questions in FDE loops probe whether you treat prompts as software (versioned, tested, reviewed) or as text (edited in the console, deployed on vibes).

Sample questions:

1. "How do you incorporate customer-specific vocabulary into a general-purpose LLM?" (They want: inline glossary in the prompt, not fine-tuning as the first move. Bonus: negative constraints for common confusables, prompt caching for the stable prefix.)
2. "Your prompt has grown to 3,000 tokens and every request is slow. What do you do?" (Split into cacheable prefix + volatile suffix, audit which glossary/example entries are actually earning their token cost via ablation on the eval, consider retrieval for glossary entries when the glossary is huge.)
3. "The customer says 'the model keeps mentioning our competitor.' Walk through your fix." (Add explicit taboo, add post-generation regex check, re-prompt on violation, add a test to the eval set. Never rely solely on prompt instruction for a policy-grade constraint.)

## DRILL

Take a classifier or Q&A prompt you have used. Rewrite it in the four-layer structure: role/scope, glossary, few-shot examples, taboos/refusal. Extract the glossary and examples into separate YAML files. Now write three "taboo" test queries — inputs designed to trick the model into breaking a rule — and add them to your eval set. If any pass through, add a post-generation check. Save the file structure; you will reuse it on every customer engagement.
