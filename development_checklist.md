# Development Plan: Schedule of Assessments (SoA) Optimizer

This plan outlines a local-first, containerized development workflow. It focuses on creating a robust backend "Rules Engine" and an intuitive frontend for visualizing and comparing schedules. All modules will be independently testable using pytest.

---

### Phase 1: Project Foundation & Local Environment (Sprint 1)

**Objective:** Establish the project structure and a fully containerized local environment using Docker Compose.

- [ ] **Project Scaffolding**
    - [ ] Initialize Git repository: `soa-optimizer`.
    - [ ] Create the primary directory structure:
      ```
      soa-optimizer/
      ├── backend/         # Main FastAPI application
      ├── services/
      │   ├── mcp_ProtocolComplexityAnalyzer/
      │   └── mcp_ComplianceKnowledgeBase/
      ├── frontend/
      ├── docker-compose.yml
      └── README.md
      ```
- [ ] **Data Modeling**
    - [ ] Define the core Pydantic models in `backend/models.py` for:
        - `Assessment`: (e.g., name, duration, cost, is_invasive, equipment_needed)
        - `Visit`: (e.g., name, day, list of Assessments)
        - `Schedule`: (e.g., list of Visits)
        - `OptimizationResult`: (e.g., original_schedule, suggested_schedule, burden_scores, warnings)
- [ ] **Containerization Setup**
    - [ ] Create `Dockerfile` and `requirements.txt` for the `backend` and each mock `service`.
    - [ ] Write `docker-compose.yml` to define and network the `backend`, the two mock MCP `services`, and the `frontend`. Expose the backend API on port 8080.
- [ ] **Mock MCP Services**
    - [ ] Build simple FastAPI mock servers for `ProtocolComplexityAnalyzer` and `ComplianceKnowledgeBase`. They should accept a `Schedule` object and return mock data (e.g., complexity scores, compliance warnings).
    - [ ] Write a basic `pytest` for each mock service to ensure it starts and returns the expected mock data.

---

### Phase 2: Backend - The Optimization Engine (Sprints 2-3)

**Objective:** Develop the core logic of the application. This "Rules Engine" will analyze schedules and generate optimization suggestions.

- [ ] **Burden Calculation Module (`backend/burden_calculator.py`)**
    - [ ] Create a function to calculate a **Patient Burden Score** from a `Schedule` object (e.g., sum of visit durations, count of invasive procedures).
    - [ ] Create a function to calculate a **Site Burden Score** (e.g., sum of staff time, unique equipment requirements).
    - [ ] Write `pytest` unit tests for these functions with mocked `Schedule` data to verify scoring accuracy.
- [ ] **Rules Engine Development (`backend/rules_engine.py`)**
    - [ ] Implement the first rule: **Redundancy Detection**. Identify and flag assessments that are repeated within a short timeframe without clear justification.
    - [ ] Implement the second rule: **Visit Consolidation**. Identify visits that are close together in time with low patient burden, and suggest merging them.
    - [ ] Implement the third rule: **Logistical Feasibility**. Cross-reference with the `ComplianceKnowledgeBase` MCP to flag impossible schedules (e.g., a procedure scheduled on a weekend when a lab is closed).
    - [ ] Write extensive `pytest` unit tests for each rule, providing various `Schedule` objects to confirm the rule logic is sound.
- [ ] **Main API Endpoint (`backend/main.py`)**
    - [ ] Create the primary endpoint: `POST /optimize-schedule`.
    - [ ] This endpoint should:
        1. Accept a `Schedule` object in the request body.
        2. Call the `Burden Calculator` to get the baseline score.
        3. Pass the schedule through the `Rules Engine`.
        4. Call the mock MCPs for additional context.
        5. Assemble and return an `OptimizationResult` object.
    - [ ] Write `pytest` integration tests for this endpoint, mocking the `httpx` calls to the MCP services.

---

### Phase 3: Frontend - The User Interface (Sprints 3-4)

**Objective:** Design and build an intuitive interface for study designers to upload, visualize, and compare schedules.

- [ ] **Wireframing & UI Design**
    - [ ] Design a three-part UI:
        1. **Input:** A simple interface for uploading a CSV/JSON file or manually building a schedule.
        2. **Dashboard:** A view to display the analysis of the *current* schedule, showing burden scores and warnings.
        3. **Comparison View:** A side-by-side display of the original schedule and the *optimized* version, highlighting the changes and improvements.
- [ ] **Component Development**
    - [ ] Build a reusable `ScheduleTable` component that can visually render a `Schedule` object.
    - [ ] Build the `FileUpload` and manual entry components.
    - [ ] Build the `BurdenScoreCard` and `WarningsList` components for the dashboard.
- [ ] **State Management & API Connection**
    - [ ] Implement frontend state management to handle the original schedule, the analysis results, and the optimized schedule.
    - [ ] Connect the UI to the backend API. When a user submits a schedule, call `POST /optimize-schedule` and update the UI with the response.
    - [ ] Implement clear loading and error states for the user.

---

### Phase 4: Integration, Testing, & Deployment (Sprint 5)

**Objective:** Ensure all parts of the application work together seamlessly and prepare for deployment.

- [ ] **End-to-End Testing**
    - [ ] Run the entire application locally using `docker-compose up`.
    - [ ] Perform manual end-to-end tests: Upload a complex schedule, verify the optimization results on the frontend, and confirm the logic matches expectations.
- [ ] **Finalization & Documentation**
    - [ ] Refine the UI based on internal feedback.
    - [ ] Document the API endpoints and the data models.
- [ ] **"Stitching to Azure" - Deployment Plan**
    - [ ] Create an Azure Container Registry (ACR) to store Docker images.
    - [ ] Set up a CI/CD pipeline (e.g., GitHub Actions) to automatically build, test, and push images to ACR.
    - [ ] Provision Azure App Services for the backend, frontend, and mock services, configuring them to pull their respective images from ACR.
