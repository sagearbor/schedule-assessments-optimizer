# Schedule of Assessments (SoA) Optimizer

**An intelligent tool designed to streamline clinical trial protocols by analyzing and optimizing the Schedule of Assessments for patient and site burden.**

---

### 1. The Problem 😩

Designing a Schedule of Assessments is a balancing act. While comprehensive data collection is crucial for trial success, overly complex or burdensome schedules can be detrimental. They often lead to:

* **Patient Burnout:** Excessive visits or lengthy procedures increase patient burden, resulting in higher dropout rates.
* **Site Strain:** Complicated schedules create logistical challenges for site staff, increasing the risk of protocol deviations and errors.
* **Redundant Procedures:** Unnecessary or overlapping assessments bloat the protocol, adding cost and complexity without contributing meaningful data.

Currently, identifying these issues relies on manual review, which is time-consuming and often subjective.

### 2. The Solution: Data-Driven Streamlining ✨

The **SoA Optimizer** provides a data-driven, objective way to analyze a proposed Schedule of Assessments *before* the protocol is finalized. By leveraging specialized MCPs, the tool automatically flags logistical challenges, identifies redundancies, and calculates a "burden score" for both patients and sites.

It doesn't just find problems; it suggests **actionable alternatives**. The optimizer proposes streamlined schedules that reduce burden while ensuring the integrity of the trial's endpoints is maintained.

### 3. Key Features

* **Protocol Upload:** Ingests SoA tables directly from protocol documents or structured data files (e.g., CSV, JSON).
* **Burden Scoring:** Calculates and visualizes distinct burden scores for patients (e.g., total visit time, number of invasive procedures) and sites (e.g., specialized equipment needs, staff time).
* **Optimization Engine:** A rules-based engine that suggests concrete improvements, such as combining visits, eliminating redundant tests, or flagging logistically impossible schedules.
* **Comparison View:** Allows designers to compare their original SoA side-by-side with the optimized version, complete with a summary of improvements.

### 4. MCPs Integrated

This solution is powered by the synergy between two core MCP tools:

1.  `ProtocolComplexityAnalyzer`
2.  `ComplianceKnowledgeBase`

### 5. Local Development & Setup

This project uses a local-first, containerized workflow with Docker.

1.  **Clone the repository:**
    ```bash
    git clone [repository_url]
    cd soa-optimizer
    ```

2.  **Build and run all services:**
    ```bash
    docker-compose up --build -d
    ```

3.  **Access the application:**
    * **Frontend UI:** [http://localhost:3000](http://localhost:3000)
    * **Backend API:** [http://localhost:8080](http://localhost:8080)
