# LLM Design Patterns

This document outlines powerful design patterns for building sophisticated LLM-based systems. These patterns include evaluation mechanisms (Judge/Jury), agentic behaviors (Tool Use, Planning), and quality improvement techniques (Reflection/Self-Correction).

---

## Table of Contents

1. [LLM as a Judge](#pattern-1-llm-as-a-judge) - Single-criterion evaluation
2. [LLM as a Jury](#pattern-2-llm-as-a-jury-multi-agent-evaluation) - Multi-agent evaluation
3. [Tool Use Pattern](#pattern-3-tool-use-pattern) - Dynamic tool selection and execution
4. [Plan-and-Execute Pattern](#pattern-4-plan-and-execute-pattern) - Multi-step task decomposition
5. [Reflection/Self-Correction Pattern](#pattern-5-reflectionself-correction-pattern) - Iterative quality improvement

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

---

## Pattern 3: Tool Use Pattern

The "Tool Use Pattern" enables LLMs to interact with external tools and APIs, extending their capabilities beyond text generation to real-world actions and data access.

### The Concept

An LLM agent can dynamically select and use tools from a predefined toolkit based on the user's request. The agent analyzes the task, chooses the appropriate tool, executes it, and incorporates the results into its response.

### How It Works

1. **Tool Registry:** Define a set of tools (functions) with clear descriptions, parameter schemas, and usage examples.
2. **Task Analysis:** The agent receives a user request and determines which tool(s) are needed.
3. **Tool Selection:** Using its reasoning capabilities, the LLM selects the most appropriate tool(s).
4. **Execution:** The agent calls the selected tool with appropriate parameters.
5. **Result Integration:** The tool's output is incorporated into the agent's final response.

### Strengths

- **Extended Capabilities:** LLMs can perform actions beyond text generation (calculations, web searches, API calls).
- **Dynamic Adaptation:** Agents can choose different tools based on the specific task requirements.
- **Composability:** Multiple tools can be chained together for complex workflows.

### Weaknesses

- **Tool Selection Errors:** The agent might choose the wrong tool or use incorrect parameters.
- **Dependency Management:** Requires maintaining and versioning external tools and APIs.
- **Error Handling:** Tool failures need to be gracefully handled and communicated.

---

## Pattern 4: Plan-and-Execute Pattern

The "Plan-and-Execute Pattern" breaks down complex tasks into smaller, manageable steps, then executes them sequentially or in parallel.

### The Concept

Instead of attempting to solve a complex problem in one shot, the agent first creates a detailed plan with discrete steps, then systematically executes each step, potentially adjusting the plan as it progresses.

### How It Works

1. **Task Decomposition:** The agent analyzes a complex task and breaks it into smaller sub-tasks.
2. **Plan Creation:** A structured plan is generated with clear steps, dependencies, and success criteria.
3. **Sequential Execution:** Each step is executed in order, with outputs feeding into subsequent steps.
4. **Progress Tracking:** The agent monitors completion and can adjust the plan if needed.
5. **Result Synthesis:** Final results from all steps are combined into a cohesive output.

### Strengths

- **Handles Complexity:** Complex tasks become manageable through decomposition.
- **Transparency:** The plan provides visibility into the agent's reasoning process.
- **Debuggability:** Failures can be traced to specific steps in the plan.
- **Adaptability:** Plans can be modified mid-execution based on intermediate results.

### Weaknesses

- **Planning Overhead:** Creating a detailed plan adds latency before execution begins.
- **Rigidity:** Pre-defined plans may not adapt well to unexpected situations.
- **Plan Quality:** The effectiveness depends heavily on the quality of the initial plan.

---

## Pattern 5: Reflection/Self-Correction Pattern

The "Reflection/Self-Correction Pattern" enables LLMs to iteratively improve their outputs through self-critique and refinement, mimicking human revision processes.

### The Concept

Instead of generating a response once and stopping, the agent generates an initial response, critically evaluates it against quality criteria, identifies weaknesses, and produces an improved version. This cycle repeats until quality thresholds are met or iteration limits are reached.

### How It Works

1. **Initial Generation:** The agent produces a first-draft response to the task.
2. **Self-Critique:** The agent evaluates its own response using structured criteria:
   - Scores the response on quality dimensions (accuracy, clarity, completeness, etc.)
   - Identifies specific weaknesses and areas for improvement
   - Suggests concrete refinements
3. **Refinement:** The agent generates an improved version addressing the critique.
4. **Iteration:** Steps 2-3 repeat until:
   - A quality threshold is met (e.g., score ≥ 0.8)
   - Maximum iterations are reached (e.g., 3 iterations)
5. **Final Output:** Returns the best version along with improvement history.

### Strengths

- **Quality Improvement:** Iterative refinement produces higher-quality outputs than single-pass generation.
- **Self-Awareness:** The agent develops awareness of its own weaknesses and blind spots.
- **Adaptability:** Can be tuned with different quality thresholds and iteration limits for various use cases.
- **Transparency:** The critique history provides insight into the improvement process.
- **No External Judge Needed:** Unlike the Jury pattern, this uses the same agent for both generation and evaluation.

### Weaknesses

- **Resource Intensive:** Multiple LLM calls per task increase latency and cost (typically 3-5x).
- **Diminishing Returns:** Later iterations may provide minimal improvement while consuming resources.
- **Critique Quality:** The effectiveness depends on the agent's ability to accurately self-evaluate.
- **Potential Loops:** Poor critique can lead to repeatedly making the same or similar mistakes.
- **Overconfidence:** The agent might be overly critical or lenient in self-evaluation.

### Use Cases

#### High-Quality Content Generation
- **Technical Documentation:** Iteratively refine API documentation for clarity and completeness.
- **Legal Writing:** Generate contract clauses that meet high standards of precision and coverage.
- **Academic Writing:** Improve research summaries for accuracy and scholarly tone.

#### Automated Debugging
- **Code Generation:** Generate code, identify bugs through self-review, and produce corrected versions.
- **SQL Query Optimization:** Refine database queries for correctness and performance.
- **Test Case Development:** Improve test coverage by identifying edge cases through reflection.

#### Creative Writing
- **Story Generation:** Refine narrative consistency, character development, and plot coherence.
- **Marketing Copy:** Iteratively improve persuasiveness, clarity, and brand alignment.

### Implementation Example

```python
class ReflectionAgent:
    def __init__(self, config_loader, max_iterations=3):
        self.max_iterations = max_iterations
        # ... initialization
    
    def run(self, task, context=None, quality_threshold=0.8):
        # Generate initial response
        response = self._generate_initial_response(task, context)
        
        # Iterative refinement loop
        for iteration in range(self.max_iterations):
            # Self-critique
            critique = self._critique_response(task, response, context)
            
            # Check if quality threshold is met
            if critique['quality_score'] >= quality_threshold:
                return self._build_result(response, iteration, critiques)
            
            # Refine based on critique
            response = self._refine_response(task, response, critique, context)
        
        return self._build_result(response, self.max_iterations, critiques)
```

### Comparison with Other Patterns

- **vs. Judge/Jury Pattern:** Reflection uses self-evaluation instead of external judges. Simpler architecture but potentially less objective.
- **vs. Tool Use Pattern:** Reflection focuses on quality improvement, while Tool Use extends capabilities. They can be combined (e.g., reflect on tool usage strategies).
- **vs. Plan-and-Execute:** Both involve iterative processes, but Reflection refines outputs while Planning decomposes tasks. Planning can use Reflection to improve individual steps.

---

## Choosing the Right Pattern

| Pattern | Best For | Complexity | Cost |
|---------|----------|------------|------|
| **Judge** | Single-criterion evaluation | Low | Low (1-2 LLM calls) |
| **Jury** | Holistic, multi-dimensional evaluation | High | High (3-6+ LLM calls) |
| **Tool Use** | Tasks requiring external data/actions | Medium | Medium (depends on tools) |
| **Plan-and-Execute** | Complex, multi-step tasks | Medium | Medium (scales with steps) |
| **Reflection** | High-quality content generation | Medium | High (3-5x generation) |

### Combining Patterns

These patterns can be composed for even more sophisticated systems:

- **Planning + Reflection:** Generate a plan, then refine each step through reflection.
- **Tool Use + Reflection:** Use tools to gather information, then reflect on how well the information answers the query.
- **Planning + Tool Use:** Create a plan that includes tool usage at specific steps.
- **Jury + Reflection:** Use reflection to improve outputs, then evaluate with a jury for final assessment.

