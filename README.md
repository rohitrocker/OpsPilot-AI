# OpsPilot-AI

**An AI-powered incident diagnosis and resolution copilot for
troubleshooting operational and infrastructure logs.**

OpsPilot-AI is a learning and development project that combines log
processing, machine learning, retrieval-augmented generation (RAG), and
agent-based workflows to help investigate incidents, surface relevant
runbooks, and suggest troubleshooting steps.

> **Project status:** In development. Available features depend on which
> modules have been implemented and configured in your local
> environment. Review the source code and configuration before relying
> on any generated diagnosis or recommendation.

## Contents

-   [Overview](#overview)
-   [Goals](#goals)
-   [Architecture](#architecture)
-   [Repository Structure](#repository-structure)
-   [Technology Stack](#technology-stack)
-   [How the Workflow Is Intended to
    Work](#how-the-workflow-is-intended-to-work)
-   [Getting Started](#getting-started)
-   [Configuration](#configuration)
-   [Running the Project](#running-the-project)
-   [Data](#data)
-   [Evaluation and Testing](#evaluation-and-testing)
-   [Security and Responsible Use](#security-and-responsible-use)
-   [Roadmap](#roadmap)
-   [Contributing](#contributing)
-   [License](#license)

## Overview

Operational incidents often require engineers to inspect noisy logs,
identify likely failure patterns, locate relevant documentation, and
decide what to investigate next. OpsPilot-AI is designed to bring these
steps into one workflow.

The project is organized around these capabilities:

-   **Log processing:** parse raw log files and convert log messages
    into structured records.
-   **Machine learning:** prepare features and train/evaluate a model
    for incident or anomaly-related classification.
-   **Knowledge retrieval:** index troubleshooting notes and runbooks so
    relevant guidance can be retrieved for an incident.
-   **Agent workflow:** coordinate investigation steps and supporting
    tools.
-   **API and interface:** expose backend functionality through an API
    and provide a Streamlit-based interface.

The exact behavior depends on the modules and integrations implemented
in the current version.

## Goals

1.  Turn raw operational logs into structured data that can be analyzed.
2.  Build a repeatable preprocessing, training, and evaluation pipeline.
3.  Retrieve relevant runbooks and troubleshooting knowledge.
4.  Combine model outputs and retrieved context to support incident
    investigation.
5.  Provide a maintainable foundation for an API, user interface, and
    tests.

## Architecture

``` text
Raw logs / incident input
          |
          v
   Log preprocessing
          |
          v
 Structured records and features
          |
          v
 ML classification / analysis
          |
          +--------------------------+
          |                          |
          v                          v
  Incident context            Knowledge base
                                     |
                              Runbooks / docs
                                     |
                                     v
                              Retrieval (RAG)
          |                          |
          +-------------+------------+
                        |
                        v
                Agent workflow/tools
                        |
                        v
             Diagnosis and recommendations
                        |
              +---------+---------+
              |                   |
              v                   v
          Backend API       Streamlit UI
```

This diagram describes the intended high-level workflow, not a guarantee
that every integration is already connected.

## Repository Structure

``` text
opspilot-ai/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── incidents.py
│   │   └── health.py
│   ├── schemas/
│   │   └── incident.py
│   ├── services/
│   │   ├── log_parser.py
│   │   ├── classifier.py
│   │   └── rag_service.py
│   └── agents/
│       ├── workflow.py
│       └── tools.py
├── ml/
│   ├── data/
│   ├── preprocess.py
│   ├── train.py
│   ├── evaluate.py
│   └── artifacts/
├── knowledge_base/
│   ├── runbooks/
│   └── ingestion.py
├── frontend/
│   └── streamlit_app.py
├── tests/
├── evaluation/
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Some files or folders may be added as development progresses. Update
this tree if your repository differs.

## Technology Stack

The project is designed around the following tools; check
`requirements.txt` and the implementation to confirm which are currently
in use.

-   **Python** --- core development language
-   **Pandas / NumPy** --- data preparation and feature processing,
    where used
-   **Scikit-learn** --- machine-learning pipeline, where configured
-   **FastAPI** --- backend API
-   **Streamlit** --- user interface
-   **RAG components** --- retrieve relevant knowledge from runbooks and
    documentation
-   **LLM / agent framework** --- coordinate reasoning and tool use,
    depending on configuration
-   **Docker** --- containerization support

## How the Workflow Is Intended to Work

1.  **Ingest logs:** provide a raw log file or incident input.
2.  **Parse and preprocess:** extract useful fields and normalize
    messages.
3.  **Create features:** transform structured log data into features
    appropriate for the ML pipeline.
4.  **Train and evaluate:** train the configured model and assess it
    with the evaluation scripts.
5.  **Retrieve knowledge:** search runbooks and troubleshooting material
    for relevant context.
6.  **Investigate:** use the agent workflow and available tools to
    combine incident evidence with retrieved information.
7.  **Present results:** return the available diagnosis or suggestions
    through the API or Streamlit interface.

Do not assume a step is active until its corresponding code and
configuration have been tested.

## Getting Started

### Prerequisites

-   Python compatible with the versions supported by your dependencies
-   Git
-   PowerShell on Windows, or a terminal on macOS/Linux
-   API credentials only if the selected LLM provider requires them

### 1. Clone the repository

Replace `YOUR_USERNAME` with your GitHub username:

``` bash
git clone https://github.com/YOUR_USERNAME/OpsPilot-AI.git
cd OpsPilot-AI
```

### 2. Create a virtual environment

**Windows PowerShell:**

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks environment activation, you can run the
environment's Python directly:

``` powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

**macOS/Linux:**

``` bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 3. Install dependencies

``` bash
python -m pip install -r requirements.txt
```

If installation fails, check the Python version and package versions
required by the error message. Keep `requirements.txt` synchronized with
the dependencies the project actually uses.

### 4. Configure environment variables

If the project uses API keys or other secrets, copy the example file and
fill in the required values:

**Windows PowerShell:**

``` powershell
Copy-Item .env.example .env
```

**macOS/Linux:**

``` bash
cp .env.example .env
```

Add only the variable names required by your code. For example, if your
chosen LLM provider requires a key, configure that provider's
environment variable. Do not put real credentials in `.env.example`,
source files, screenshots, or Git commits.

### 5. Prepare the data

Place permitted sample logs in the data directory expected by the
preprocessing script. Confirm the input path and output filenames in
`ml/preprocess.py` before running it.

If your current dataset is an HDFS-style log file, check that the parser
is designed for that format. Do not assume a log file automatically
provides labeled examples for supervised training.

## Running the Project

Run commands from the repository root. Confirm the paths and
command-line arguments in each script before execution.

### Machine-learning pipeline

``` powershell
python .\ml\preprocess.py
python .\ml\train.py
python .\ml\evaluate.py
```

Run each stage separately and verify its output before continuing. These
commands assume the corresponding scripts are implemented and runnable
in your checkout.

### Backend API

If `app/main.py` exposes a FastAPI application object named `app`, start
it with:

``` powershell
python -m uvicorn app.main:app --reload
```

Then open the API documentation at `http://127.0.0.1:8000/docs`.

If your application object or entry point has a different name, adjust
the command to match the code.

### Streamlit interface

If the Streamlit interface is implemented in
`frontend/streamlit_app.py`, run:

``` powershell
python -m streamlit run .\frontend\streamlit_app.py
```

### Docker

A `Dockerfile` is included in the project structure. Review it and
ensure required environment variables, data files, and model artifacts
are available before building or running the container.

## Data

The `ml/data/` directory is intended for input data and generated
intermediate files. Large datasets, confidential logs, credentials, and
personally identifiable information should not be committed to a public
repository.

For reproducible experiments:

-   Document the source and license of each dataset.
-   Keep a small, non-sensitive sample when it is useful for
    demonstrating the pipeline.
-   Record preprocessing assumptions and label definitions.
-   Separate raw data from generated features and model artifacts.
-   Avoid reporting model performance unless it has been measured on a
    clearly defined evaluation set.

## Evaluation and Testing

Use the `ml/evaluate.py` script and the `tests/` and `evaluation/`
directories for validation as they are implemented.

Recommended checks include:

-   Parser behavior on valid, malformed, and empty log input
-   Feature-generation consistency
-   Train/validation/test separation and prevention of data leakage
-   Appropriate classification metrics, such as precision, recall,
    F1-score, and a confusion matrix, when relevant
-   Retrieval relevance and whether recommendations are grounded in the
    retrieved runbook
-   API validation and error handling
-   Tests that confirm failures do not trigger unsafe automated actions

Record actual results in the repository only after running the
evaluation.

## Security and Responsible Use

-   Never commit `.env`, API keys, passwords, tokens, or private
    incident logs.
-   Keep `.env` and local virtual environments in `.gitignore`.
-   Sanitize logs before sending them to external LLM providers.
-   Treat model output as an aid to investigation, not proof of root
    cause.
-   Require human review and authorization before executing remediation
    steps in production.
-   Use least-privilege credentials and audit any tool that can change
    infrastructure.
-   Review third-party dataset and dependency licenses before
    redistribution.

## Roadmap

Potential next steps for the project:

-   [ ] Complete and validate log parsing and feature extraction
-   [ ] Establish a documented training and evaluation dataset
-   [ ] Add baseline metrics and reproducible evaluation
-   [ ] Complete runbook ingestion and retrieval evaluation
-   [ ] Connect the incident API to the ML and retrieval services
-   [ ] Add agent workflow tests and failure handling
-   [ ] Improve the Streamlit interface with incident details and
    evidence
-   [ ] Add Docker-based setup instructions and a deployment checklist
-   [ ] Document limitations, sample inputs, and example outputs

Mark items complete only after they are implemented and tested.

## Contributing

1.  Create a feature branch.
2.  Keep changes focused and document configuration changes.
3.  Add or update tests for behavior changes.
4.  Never include secrets or private log data in commits.
5.  Open a pull request with a summary and test results.

## License

No license is specified here. Add a `LICENSE` file before granting
others permission to reuse, modify, or distribute this project.
