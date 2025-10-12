# LLM Design Patterns: The Judge and The Jury

This document outlines two powerful design patterns for evaluating the output of Large Language Models (LLMs) by using other LLMs as evaluators. These patterns move beyond simple numeric scores to provide nuanced, qualitative, and more trustworthy assessments.

---

## Pattern 1: LLM as a Judge

The "LLM as a Judge" pattern is the foundational concept where a single LLM is tasked with evaluating a specific aspect of another LLM's output. It acts as a specialist expert focused on a single criterion.

### The Concept

Think of this pattern as a specialist court judge, like a tax court judge who only rules on financial matters. The Judge LLM is given a clear, one-dimensional task: assess the generated text against a single, well-defined metric (e.g., factual accuracy, clarity, relevance).

### How It Works

1.  **Define a Criterion:** A single, specific evaluation goal is established. For example, "Is the answer factually consistent with the provided context?"
2.  **Craft a Persona:** A detailed system prompt is created to give the Judge LLM a specific persona and a clear rubric to follow.
    -   *Example Persona:* "You are Judge Factus, a meticulous and unforgiving fact-checker. Your sole purpose is to determine if the provided answer is factually consistent with the given context. You are logical, precise, and must justify your final score with a clear, evidence-based explanation. Do not comment on style or relevance, only on facts."
3.  **Provide the Case:** The Judge LLM is given the system prompt, the text to be evaluated (e.g., the question, context, and answer), and any ground truth data.
4.  **Request a Structured Verdict:** The model is prompted to return a structured output, such as a JSON object containing a numeric score and a written justification for its decision.

### Strengths

-   **Simplicity:** Relatively straightforward to implement for targeted evaluations.
-   **Nuance:** Provides qualitative feedback (the "verdict") that is more insightful than a simple score.
-   **Focus:** By concentrating on a single aspect, the evaluation can be more detailed and accurate for that specific dimension.

### Weaknesses

-   **Lack of Holistic View:** An answer can be factually correct but stylistically terrible. A single Judge focused on facts will miss this.
-   **Potential for Bias:** The evaluation is subject to the inherent biases and limitations of the single LLM acting as the Judge.
-   **No Conflict Resolution:** It cannot resolve trade-offs. What if an answer is highly relevant but only partially faithful? The Judge pattern can't weigh these competing qualities.

---

## Pattern 2: LLM as a Jury (Multi-Agent Evaluation)

The "LLM as a Jury" pattern is a sophisticated evolution of the Judge pattern. It creates a collaborative, multi-agent system that mimics a real-world jury, where multiple experts deliberate to reach a comprehensive and balanced final decision.

### The Concept

Instead of one specialist judge, you assemble a panel of diverse expert judges. Each judge evaluates the same piece of text from their unique perspective. A "Chief Justice" or "Jury Foreman" then synthesizes these individual verdicts into a single, holistic ruling.

### How It Works

1.  **Assemble the Jury:** A panel of specialized **Judge Agents** is created. Each has a unique persona and responsibility, defined by its system prompt.
    -   `FactualJudgeAgent`: Checks for factual accuracy and groundedness.
    -   `ClarityJudgeAgent`: Assesses readability, style, and conciseness.
    -   `RelevanceJudgeAgent`: Determines if the answer directly addresses the user's query.
    -   `SafetyJudgeAgent`: Scans for bias, toxicity, or other ethical red flags.

2.  **Delegate the Case:** A primary agent, the **Chief Justice Agent**, receives the evaluation case and dispatches it to all Judge Agents, who run their assessments in parallel.

3.  **Collect the Verdicts:** The Chief Justice gathers the structured outputs (scores and written verdicts) from each Judge Agent.

4.  **Synthesize and Rule:** This is the crucial step. The Chief Justice Agent, armed with its own system prompt ("You are the Chief Justice..."), performs a final reasoning step:
    -   It reviews all the individual, expert verdicts.
    -   It identifies agreements and conflicts (e.g., "Judge Factus confirms the answer is true, but Judge Stylus notes it is poorly written.").
    -   It generates a final, comprehensive report that summarizes the findings, provides a holistic score (e.g., a weighted average), and delivers a final, synthesized opinion.

### Strengths

-   **Holistic and Balanced:** Provides a 360-degree view of the output's quality, covering multiple dimensions simultaneously.
-   **Reduces Bias:** The diversity of the jury panel mitigates the inherent biases of any single model.
-   **Conflict Resolution:** The Chief Justice can be designed to weigh different aspects and resolve trade-offs, leading to a more nuanced final judgment.
-   **Extensible:** It's easy to add new Judge Agents to the panel to evaluate for new criteria (e.g., a `CreativityJudge`) without changing the core architecture.

### Weaknesses

-   **Complexity:** More complex to design and orchestrate than the single Judge pattern.
-   **Resource Intensive:** Requires multiple LLM calls for a single evaluation, increasing latency and cost.
-   **Synthesis Quality:** The quality of the final ruling is highly dependent on the reasoning capability of the Chief Justice Agent.
