# Architecture Diagrams - Supplier Selection App

## 1. System Architecture (4-Layer)

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[Main Window]
        PT[Project Tab]
        AT[AHP Tab]
        TT[TOPSIS Tab<br/>TRANSPOSED]
        RT[Results Tab]
        ST[Sensitivity Tab]
    end
    
    subgraph "Business Logic Layer"
        FAHP[Fuzzy AHP<br/>Algorithm]
        ITOPSIS[Interval TOPSIS<br/>7-Level Scale]
        SENS[Sensitivity<br/>Analysis]
    end
    
    subgraph "Data Layer"
        DB[(SQLite<br/>Database)]
        SCHEMA[Schema<br/>Manager]
        DBMGR[Database<br/>Manager]
    end
    
    subgraph "Utility Layer"
        EXCEL[Excel<br/>Handler]
        VALID[Validators]
        PMGR[Project<br/>Manager]
        SMGR[Scenario<br/>Manager]
    end
    
    UI --> PT
    UI --> AT
    UI --> TT
    UI --> RT
    UI --> ST
    
    PT --> DBMGR
    AT --> FAHP
    AT --> DBMGR
    TT --> ITOPSIS
    TT --> DBMGR
    RT --> DBMGR
    ST --> SENS
    ST --> DBMGR
    
    FAHP --> DBMGR
    ITOPSIS --> DBMGR
    SENS --> ITOPSIS
    
    DBMGR --> SCHEMA
    SCHEMA --> DB
    
    EXCEL --> DBMGR
    VALID --> DBMGR
    PMGR --> DBMGR
    SMGR --> DBMGR
    
    style ITOPSIS fill:#90EE90
    style TT fill:#90EE90
    style DB fill:#87CEEB
```

## 2. Data Flow

```mermaid
sequenceDiagram
    participant User
    participant GUI
    participant Algorithm
    participant Database
    
    User->>GUI: 1. Create Project
    GUI->>Database: Save project info
    
    User->>GUI: 2. Add Criteria & Alternatives
    GUI->>Database: Save criteria/alternatives
    
    User->>GUI: 3. AHP Comparisons
    GUI->>Algorithm: Fuzzy AHP Calculation
    Algorithm->>Database: Save weights
    
    User->>GUI: 4. TOPSIS Ratings (7 levels)
    GUI->>Database: Save interval ratings
    
    User->>GUI: 5. Calculate TOPSIS
    GUI->>Database: Load ratings & weights
    Database->>Algorithm: Return data
    Algorithm->>Algorithm: TOPSIS ranking
    Algorithm->>GUI: Return results
    GUI->>User: Display rankings
```

## 3. Database Schema

```mermaid
erDiagram
    PROJECT ||--o{ CRITERION : has
    PROJECT ||--o{ ALTERNATIVE : has
    PROJECT ||--o{ EXPERT : has
    PROJECT ||--o{ SCENARIO : has
    
    EXPERT ||--o{ AHP_COMPARISON : makes
    EXPERT ||--o{ TOPSIS_RATING : makes
    
    CRITERION ||--o{ AHP_COMPARISON : compared
    CRITERION ||--o{ TOPSIS_RATING : rated
    CRITERION ||--o{ CRITERION : "parent of"
    
    ALTERNATIVE ||--o{ TOPSIS_RATING : rated
    SCENARIO ||--o{ TOPSIS_RATING : contains
```

## 4. Module Dependencies

```mermaid
graph LR
    subgraph "High Level"
        GUI[GUI Layer]
    end
    
    subgraph "Mid Level"
        ALG[Algorithm Layer]
        UTIL[Utility Layer]
    end
    
    subgraph "Low Level"
        DB[Database Layer]
    end
    
    GUI --> ALG
    GUI --> UTIL
    GUI --> DB
    ALG --> DB
    UTIL --> DB
    
    style GUI fill:#FFE4B5
    style ALG fill:#98FB98
    style UTIL fill:#87CEEB
    style DB fill:#FFB6C1
```

## 5. User Workflow

```mermaid
flowchart TD
    Start([Start]) --> NewProject{New or<br/>Existing?}
    
    NewProject -->|New| CreateProj[Create Project]
    NewProject -->|Existing| OpenProj[Open Project]
    
    CreateProj --> AddCriteria[Add Criteria]
    OpenProj --> AddCriteria
    
    AddCriteria --> AddAlts[Add Alternatives]
    AddAlts --> AddExperts[Add Experts]
    AddExperts --> AHPInput[AHP Comparisons]
    
    AHPInput --> CalcWeights[Calculate Weights]
    CalcWeights --> CheckCR{CR ≤ 0.1?}
    
    CheckCR -->|No| AHPInput
    CheckCR -->|Yes| TOPSISInput[TOPSIS Ratings<br/>7-Level Scale]
    
    TOPSISInput --> CalcTOPSIS[Calculate Rankings]
    CalcTOPSIS --> ViewResults[View Results]
    ViewResults --> Export[Export Excel]
    Export --> End([End])
    
    style TOPSISInput fill:#90EE90
```

## 6. TOPSIS Algorithm

```mermaid
flowchart TD
    Start([Input: Ratings & Weights])
    --> Aggregate[Aggregate Expert Ratings]
    --> Normalize[Normalize Matrix]
    --> Weight[Apply Weights]
    --> PIS[Calculate PIS]
    --> NIS[Calculate NIS]
    --> DistPIS[Distance to PIS]
    --> DistNIS[Distance to NIS]
    --> CC[Closeness Coefficient]
    --> Rank[Rank Alternatives]
    --> End([Output: Rankings])
    
    style CC fill:#90EE90
```

## 7. Database ERD (Detailed with Fields)

```mermaid
erDiagram
    PROJECT ||--o{ CRITERION : has
    PROJECT ||--o{ ALTERNATIVE : has
    PROJECT ||--o{ EXPERT : has
    PROJECT ||--o{ SCENARIO : has
    
    EXPERT ||--o{ AHP_COMPARISON : makes
    EXPERT ||--o{ TOPSIS_RATING : makes
    
    CRITERION ||--o{ AHP_COMPARISON : compared
    CRITERION ||--o{ TOPSIS_RATING : rated
    CRITERION ||--o{ CRITERION : "parent of"
    
    ALTERNATIVE ||--o{ TOPSIS_RATING : rated
    SCENARIO ||--o{ TOPSIS_RATING : contains
    
    PROJECT {
        int id PK
        string name
        string description
        datetime created_at
    }
    
    CRITERION {
        int id PK
        int project_id FK
        int parent_id FK
        string name
        bool is_benefit
        float weight
    }
    
    ALTERNATIVE {
        int id PK
        int project_id FK
        string name
        string description
    }
    
    EXPERT {
        int id PK
        int project_id FK
        string name
        string title
        float expertise_weight
    }
    
    SCENARIO {
        int id PK
        int project_id FK
        string name
        string description
    }
    
    AHP_COMPARISON {
        int id PK
        int project_id FK
        int expert_id FK
        int criterion1_id FK
        int criterion2_id FK
        float fuzzy_l
        float fuzzy_m
        float fuzzy_u
    }
    
    TOPSIS_RATING {
        int id PK
        int project_id FK
        int scenario_id FK
        int expert_id FK
        int alternative_id FK
        int criterion_id FK
        float rating_lower
        float rating_upper
    }
```

## 8. Component Dependency (Detailed)

```mermaid
graph TD
    MainWindow[main_window.py]
    ProjectTab[project_tab.py]
    AHPTab[ahp_tab.py]
    TOPSISTab[topsis_tab.py]
    ResultsTab[results_tab.py]
    SensTab[sensitivity_tab.py]
    
    FuzzyAHP[fuzzy_ahp.py]
    IntervalTOPSIS[interval_topsis.py]
    SensAnalysis[sensitivity_analysis.py]
    
    DBManager[manager.py]
    Schema[schema.py]
    
    ExcelHandler[excel_handler.py]
    Validators[validators.py]
    ProjectMgr[project_manager.py]
    ScenarioMgr[scenario_manager.py]
    
    MainWindow --> ProjectTab
    MainWindow --> AHPTab
    MainWindow --> TOPSISTab
    MainWindow --> ResultsTab
    MainWindow --> SensTab
    
    ProjectTab --> DBManager
    ProjectTab --> Validators
    
    AHPTab --> FuzzyAHP
    AHPTab --> DBManager
    
    TOPSISTab --> IntervalTOPSIS
    TOPSISTab --> DBManager
    
    ResultsTab --> DBManager
    ResultsTab --> ExcelHandler
    
    SensTab --> SensAnalysis
    SensTab --> DBManager
    
    FuzzyAHP --> DBManager
    IntervalTOPSIS --> DBManager
    SensAnalysis --> IntervalTOPSIS
    SensAnalysis --> DBManager
    
    DBManager --> Schema
    
    ExcelHandler --> DBManager
    ProjectMgr --> DBManager
    ScenarioMgr --> DBManager
    
    style IntervalTOPSIS fill:#90EE90
    style TOPSISTab fill:#90EE90
    style DBManager fill:#87CEEB
    style MainWindow fill:#FFE4B5
```

## 9. Admin Workflow with File Exchange

```mermaid
flowchart TB
    Start([Admin]) --> Setup[1. Setup Project<br/>Criteria, Suppliers, Experts]
    Setup --> ExportDB[📤 2. Export Project File<br/>.db or Excel Template]
    
    ExportDB --> ShareFile[📧 Share with Experts<br/>Email/Cloud Storage]
    ShareFile --> Wait[⏳ Wait for Expert<br/>Evaluations]
    Wait --> ImportFile[📥 3. Import Expert Files<br/>AHP + TOPSIS Data]
    
    ImportFile --> CheckCR{Check CR<br/>≤ 0.1?}
    CheckCR -->|No| ShareFile
    CheckCR -->|Yes| TOPSIS[4. Run TOPSIS<br/>View Rankings]
    
    TOPSIS --> Analysis[5. Sensitivity<br/>Analysis]
    Analysis --> Scenarios{Create<br/>Scenarios?}
    Scenarios -->|Yes| NewScenario[Create Scenario<br/>Share with Experts]
    NewScenario --> Wait
    Scenarios -->|No| FinalExport[📤 6. Export Final<br/>Report Excel]
    FinalExport --> End([End])
    
    style Setup fill:#FFE4B5
    style ExportDB fill:#FFD700
    style ImportFile fill:#FFD700
    style TOPSIS fill:#90EE90
    style Analysis fill:#87CEEB
```

## 10. Expert Workflow with File Exchange

```mermaid
flowchart TB
    Start([Expert]) --> Receive[📥 1. Receive Project File<br/>from Admin]
    Receive --> Import[2. Import .db File<br/>or Open Excel]
    Import --> Review[Review Project<br/>Criteria & Suppliers]
    
    Review --> Role{Assigned<br/>Role?}
    
    Role -->|AHP Only| AHP[3a. AHP Comparisons<br/>Pairwise Matrix<br/>Fuzzy Scale]
    Role -->|TOPSIS Only| Rate
    Role -->|Both| AHP
    
    AHP --> SaveA[Save AHP Data<br/>to Local File]
    SaveA --> Both{Also do<br/>TOPSIS?}
    Both -->|Yes| Rate[3b. Rate Suppliers<br/>7-Level Scale<br/>VL-L-ML-M-MH-H-VH]
    Both -->|No| ExportA
    
    Rate --> SaveT[Save Ratings<br/>to Local File]
    SaveT --> CheckScenarios{Check for<br/>More Scenarios?}
    CheckScenarios -->|Yes| Rate
    CheckScenarios -->|No| ExportA[📤 4. Export Results<br/>.db or Excel]
    
    ExportA --> Send[📧 5. Send to Admin<br/>Email/Cloud]
    Send --> End([End])
    
    style Receive fill:#FFD700
    style Import fill:#FFE4B5
    style AHP fill:#87CEEB
    style Rate fill:#90EE90
    style ExportA fill:#FFD700
    style Send fill:#FFD700
```

---

## How to Use

1. **View in GitHub/GitLab**: Renders automatically
2. **Mermaid Live**: Copy code to https://mermaid.live/
3. **Export**: PNG, SVG, or PDF
