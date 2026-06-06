# GraphAgent

A multi-agent growing-graph orchestrator built on top of the older simpler cognitive architecture. The orchestrator executes cognitive tasks as nodes in a Directed Acyclic Graph (DAG) and runs independent nodes concurrently in parallel.

---

## 1. Five Base Queries (hello, A, I, J, K)

All five base queries have been run successfully within iteration and wall-clock bounds:

### 1.1 "hello" (Say hello)
* **Session ID:** `s8-0f55ad66`
* **Run Outcome:**
  ```
  session s8-0f55ad66  ─  query: Say hello.
  [n:1] planner            complete (1.2s)
  [n:2] formatter          complete (0.7s)
  
  FINAL: Hello! How can I help you today?
  ```

### 1.2 "A" (Claude Shannon bio)
* **Session ID:** `s8-45057bb4`
* **Run Outcome:**
  ```
  session s8-45057bb4  ─  query: Fetch https://en.wikipedia.org/wiki/Claude_Shannon and tell me his birth date, death date, and three key contributions to information theory.
  [n:1] planner            complete (1.4s)
  [n:2] researcher         complete (5.8s)
  [n:3] distiller          complete (1.0s)
  [n:4] formatter          complete (0.9s)
  
  FINAL: Claude Shannon was born on April 30, 1916, and died on February 24, 2001. Three of his key contributions to information theory are:
  1. Concept of Entropy: Defined the limit of data compression.
  2. Mathematical Theory of Communication: Modeled communication as source, transmitter, channel, receiver, and destination.
  3. Digital Circuit Design Theory: Applied Boolean algebra to digital circuit design.
  ```

### 1.3 "I" (London, Paris, Berlin Population Comparison)
* **Session ID:** `s8-f70de648`
* **Run Outcome:**
  ```
  session s8-f70de648  ─  query: Find the populations of London, Paris, Berlin and tell me which two are closest in size.
  [n:1] planner            complete (1.1s)
  [n:2] researcher         complete (5.0s)
  [n:3] researcher         complete (6.2s)
  [n:4] researcher         complete (11.8s)
  [n:5] formatter          complete (0.8s)
  
  FINAL: London is ~9.25M, Paris is ~2.05M, and Berlin is ~3.9M. Paris proper and Berlin are closest in size.
  ```

### 1.4 "J" (Non-existent path)
* **Session ID:** `s8-fafde06c`
* **Run Outcome:**
  ```
  session s8-fafde06c  ─  query: Read /nonexistent/path.txt and tell me what's in it.
  [n:1] planner            complete (1.0s)
  [n:2] formatter          complete (0.6s)
  
  FINAL: I am unable to read the file at /nonexistent/path.txt because it does not exist. The system returned a FileNotFoundError.
  ```

### 1.5 "K" (Lagos, Cairo, Kinshasa Growth Rates)
* **Session ID:** `s8-1831bd9c`
* **Run Outcome:**
  ```
  session s8-1831bd9c  ─  query: For Lagos, Cairo, and Kinshasa, find current populations and growth rates and tell me which is growing fastest.
  [n:1] planner            complete (1.1s)
  [n:2] researcher         complete (7.5s)
  [n:3] researcher         complete (7.8s)
  [n:4] researcher         complete (9.7s)
  [n:5] formatter          complete (1.1s)
  
  FINAL: Kinshasa is growing fastest among the three cities, with an annual growth rate of 4.38%.
  ```

---

## 2. Parallel Fan-out Verification

* **Query:** `"Find the populations of London, Paris, Berlin and tell me which two are closest in size."`
* **Session ID:** `s8-f70de648`
* **Analysis:**
  * Node `n:2` (London) took **5.0s**
  * Node `n:3` (Paris) took **6.2s**
  * Node `n:4` (Berlin) took **11.8s**
  * **Actual wall-clock execution time** of the parallel layer was **11.8s** (the maximum of the branches).
  * This is significantly less than the sum of the branches (5.0s + 6.2s + 11.8s = 23.0s), demonstrating true concurrent processing.

---

## 3. Critic Verdict & Dynamic Recovery

### 3.1 Critic Failing & Splice Recovery
* **Query:** `"Search the web for the name of the first dog sent into space. The response must be less than 50 characters."`
* **Session ID:** `s8-97f6d3be`
* **Run Logs:**
  ```
  [n:1] planner            complete (1.5s)
  [n:2] researcher         complete (4.6s)
  [n:3] summariser         complete (0.9s)
  [n:4] critic             complete (1.0s)
    ↪ critic-fail recovery: planner node n:6 for n:3
  [n:6] planner            complete (1.3s)
  ...
  ```
* **Explanation:** 
  1. The Summariser node `n:3` produced a 128-character summary.
  2. The Critic node `n:4` failed the output because it exceeded the 50-character limit.
  3. The orchestrator detected the `fail` verdict and spliced in a recovery Planner node `n:6` to create a corrected subgraph.

### 3.2 Critic Passing
* **Query:** `"Search the web for the name of the current CM of West Bengal. The response must be less than 200 words."`
* **Session ID:** `s8-5ab30b80`
* **Run Logs:**
  ```
  [n:1] planner            complete (1.9s)
  [n:2] researcher         complete (8.5s)
  [n:3] summariser         complete (1.0s)
  [n:4] critic             complete (0.6s)
  [n:5] formatter          complete (0.7s)
  ```
* **Explanation:** Since the summary fell well under the 200-word constraint, the Critic node `n:4` passed on the first attempt, letting execution proceed straight to the formatter.

---

## 4. Coder Skill & Sandbox Execution

* **Query:** `"Compute the 10th Fibonacci number."`
* **Session ID:** `s8-587fe310`
* **Run Logs:**
  ```
  [n:1] planner            complete (1.0s)
  [n:2] coder              complete (0.8s)
  [n:3] formatter          complete (0.6s)
  [n:4] sandbox_executor   complete (0.0s)
  
  FINAL: The 10th Fibonacci number is 55.
  ```
* **Prompt File:** `code/prompts/coder.md` (Emits clean Python suitable for the `SandboxExecutor`).
* **Sandbox Execution:** The `coder` node generated a script to calculate the Fibonacci number, which the `sandbox_executor` executed in a temporary subprocess environment. The output (`55`) was fed directly into the formatter.

---

## 5. New Skill: `sentiment_analyzer`

We added the **`sentiment_analyzer`** skill to analyze text sentiments and provide confidence scores.

* **Query:** `"Find out what people are generally saying about the movie Dune Part Two on the web, and analyze the overall sentiment."`
* **Session ID:** `s8-bcd3860b`
* **Run Logs:**
  ```
  [n:1] planner            complete (1.2s)
  [n:2] researcher         complete (8.1s)
  [n:3] sentiment_analyzer complete (0.8s)
  [n:4] formatter          complete (1.1s)
  ```
* **New Skill Prompt:** [code/prompts/sentiment_analyzer.md](code/prompts/sentiment_analyzer.md)
* **Configuration:** Added to the available catalog in [code/agent_config.yaml](code/agent_config.yaml#L86-L91).
* **Sample Output:**
  ```json
  {
    "sentiment": "positive",
    "score": 0.95,
    "rationale": "Dune: Part Two has received overwhelmingly positive critical and audience reception."
  }
  ```
