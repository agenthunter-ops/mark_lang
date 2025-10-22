# Mark Lang Architecture & Process Flow Diagrams

## System Architecture

```mermaid
graph TB
    subgraph "Input Layer"
        A[Business Brief Text]
        B[Marketing Documents<br/>PPTX, DOCX, PDF, XLSX]
    end

    subgraph "Document Processing Layer"
        C[DocumentProcessor]
        D[TextTranslator<br/>Norwegian → English]
        E[BrandGuidelinesExtractor]
    end

    subgraph "Core Processing Layer"
        F[BriefIngestor]
        G[CreativeBriefExtractor]
        H[BrandCenterClient]
    end

    subgraph "Workflow Orchestration"
        I[CreativeCampaignWorkflow<br/>LangGraph StateGraph]
    end

    subgraph "Output Layer"
        J[Campaign Plan JSON]
        K[Brand Guidelines JSON]
        L[CLI Output]
    end

    subgraph "Storage"
        M[(Brand Guidelines<br/>JSON Files)]
        N[(Translated Documents<br/>Cache)]
    end

    A --> F
    B --> C
    C --> D
    D --> E
    E --> K
    K --> M
    
    F --> I
    G --> I
    H --> I
    M --> H
    
    I --> J
    I --> L
    D --> N

    style I fill:#e1f5ff
    style M fill:#fff4e6
    style N fill:#fff4e6
```

## Document Ingestion Workflow

```mermaid
flowchart TD
    Start([Start: User provides<br/>document directory])
    
    subgraph "Phase 1: Document Extraction"
        A1{File Type?}
        A2[Extract PPTX<br/>Slides & Shapes]
        A3[Extract DOCX<br/>Paragraphs & Tables]
        A4[Extract PDF<br/>Pages & Tables]
        A5[Extract XLSX<br/>Sheets & Rows]
        A6[Combine Text<br/>per Document]
    end
    
    subgraph "Phase 2: Translation"
        B1[Split into Chunks<br/>max 4500 chars]
        B2[Translate Norwegian<br/>to English]
        B3[Handle Translation<br/>Errors]
        B4[Reassemble<br/>Translated Text]
    end
    
    subgraph "Phase 3: Guidelines Extraction"
        C1[Keyword Matching<br/>Tone, Visual, Messaging]
        C2[Pattern Recognition<br/>Bullet Points, Lists]
        C3[Audience Identification]
        C4[Values & Themes<br/>Extraction]
        C5[Channel-Specific<br/>Guidelines]
        C6[Structured Output<br/>BrandGuidelinesExtracted]
    end
    
    subgraph "Phase 4: Output"
        D1[Generate JSON<br/>Brand Guidelines]
        D2[Save Translated<br/>Documents Optional]
        D3[Display Summary]
    end
    
    Start --> A1
    A1 -->|PPTX| A2
    A1 -->|DOCX| A3
    A1 -->|PDF| A4
    A1 -->|XLSX| A5
    A2 --> A6
    A3 --> A6
    A4 --> A6
    A5 --> A6
    
    A6 --> B1
    B1 --> B2
    B2 --> B3
    B3 --> B4
    
    B4 --> C1
    C1 --> C2
    C2 --> C3
    C3 --> C4
    C4 --> C5
    C5 --> C6
    
    C6 --> D1
    C6 --> D2
    C6 --> D3
    D3 --> End([End: Guidelines<br/>JSON Generated])
    
    style A6 fill:#e3f2fd
    style B4 fill:#f3e5f5
    style C6 fill:#e8f5e9
    style D1 fill:#fff9c4
```

## Campaign Workflow Process (LangGraph)

```mermaid
stateDiagram-v2
    [*] --> Ingest: Brief Text + Title + Brand ID
    
    state "Ingest Node" as Ingest {
        [*] --> ValidateInput
        ValidateInput --> CreateBusinessBrief
        CreateBusinessBrief --> [*]
    }
    
    state "Extract Node" as Extract {
        [*] --> ParseBrief
        ParseBrief --> ExtractGoals
        ExtractGoals --> ExtractAudience
        ExtractAudience --> ExtractMessaging
        ExtractMessaging --> ExtractTimeframe
        ExtractTimeframe --> DetectGaps
        DetectGaps --> [*]
    }
    
    state "Fetch Guidelines Node" as Guidelines {
        [*] --> FetchFromBrandCenter
        FetchFromBrandCenter --> LoadToneOfVoice
        LoadToneOfVoice --> LoadVisualStyle
        LoadVisualStyle --> LoadCompliance
        LoadCompliance --> [*]
    }
    
    state "Campaign Node" as Campaign {
        [*] --> BuildEmailChannel
        BuildEmailChannel --> BuildSocialChannel
        BuildSocialChannel --> BuildWebChannel
        BuildWebChannel --> ApplyBrandGuidelines
        ApplyBrandGuidelines --> [*]
    }
    
    state "Finalize Node" as Finalize {
        [*] --> ValidateOutput
        ValidateOutput --> [*]
    }
    
    Ingest --> Extract: State with BusinessBrief
    Extract --> Guidelines: State with CreativeBrief + Gaps
    Guidelines --> Campaign: State with BrandGuidelines
    Campaign --> Finalize: State with CampaignPlan
    Finalize --> [*]: Complete WorkflowStateData
    
    note right of Extract
        Uses CreativeBriefExtractor
        to parse and structure
        brief content
    end note
    
    note right of Guidelines
        Fetches from JSON files
        or BrandCenterClient API
    end note
    
    note right of Campaign
        Generates multi-channel
        campaign plan with
        brand-aligned messaging
    end note
```

## Component Interaction Diagram

```mermaid
graph LR
    subgraph "CLI Layer"
        CLI[cli.py<br/>Command Line Interface]
    end
    
    subgraph "Workflow Layer"
        WF[CreativeCampaignWorkflow]
        IG[ingest_brand_documents.py]
    end
    
    subgraph "Processing Components"
        BI[BriefIngestor]
        CBE[CreativeBriefExtractor]
        BCC[BrandCenterClient]
        DP[DocumentProcessor]
        TT[TextTranslator]
        BGE[BrandGuidelinesExtractor]
    end
    
    subgraph "Data Models"
        BB[BusinessBrief]
        CB[CreativeBrief]
        BG[BrandGuidelines]
        WS[WorkflowStateData]
        BGX[BrandGuidelinesExtracted]
    end
    
    subgraph "External Services"
        GT[Google Translate API]
        FS[File System]
    end
    
    CLI -->|Brief Text| WF
    CLI -->|Documents Path| IG
    
    WF --> BI
    WF --> CBE
    WF --> BCC
    
    IG --> DP
    IG --> TT
    IG --> BGE
    
    BI --> BB
    CBE --> CB
    BCC --> BG
    WF --> WS
    BGE --> BGX
    
    DP --> FS
    TT --> GT
    BCC --> FS
    BGE --> FS
    
    style CLI fill:#42a5f5
    style WF fill:#66bb6a
    style IG fill:#ab47bc
    style GT fill:#ffa726
    style FS fill:#ef5350
```

## Data Flow: Brief to Campaign Plan

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as CLI
    participant WF as CreativeCampaignWorkflow
    participant BI as BriefIngestor
    participant CBE as CreativeBriefExtractor
    participant BC as BrandCenterClient
    participant LG as LangGraph
    
    U->>CLI: Run with brief.txt + brand ID
    CLI->>WF: Instantiate workflow
    WF->>LG: Build StateGraph
    
    Note over LG: Node 1: Ingest
    LG->>BI: from_text(brief_text, title)
    BI-->>LG: BusinessBrief
    
    Note over LG: Node 2: Extract
    LG->>CBE: extract(BusinessBrief)
    CBE-->>LG: CreativeBrief
    LG->>CBE: detect_gaps(CreativeBrief)
    CBE-->>LG: gaps dict
    
    Note over LG: Node 3: Fetch Guidelines
    LG->>BC: fetch_guidelines(brand_id)
    BC->>BC: Load from JSON
    BC-->>LG: BrandGuidelines
    
    Note over LG: Node 4: Campaign
    LG->>LG: _build_plan(CreativeBrief, BrandGuidelines)
    LG->>LG: Generate multi-channel plan
    
    Note over LG: Node 5: Finalize
    LG-->>WF: WorkflowStateData
    WF-->>CLI: Complete state
    CLI->>CLI: _display(state)
    CLI-->>U: Print campaign plan + brief summary
```

## Data Flow: Documents to Brand Guidelines

```mermaid
sequenceDiagram
    participant U as User
    participant IG as IngestWorkflow
    participant DP as DocumentProcessor
    participant TT as TextTranslator
    participant BGE as BrandGuidelinesExtractor
    participant FS as File System
    
    U->>IG: Run with documents directory
    IG->>FS: List directory files
    FS-->>IG: File paths list
    
    loop For each document
        IG->>DP: process_file(file_path)
        alt PPTX
            DP->>DP: _process_pptx()
        else DOCX
            DP->>DP: _process_docx()
        else PDF
            DP->>DP: _process_pdf()
        else XLSX
            DP->>DP: _process_excel()
        end
        DP-->>IG: Document dict with full_text
    end
    
    loop For each document
        IG->>TT: translate_document(doc)
        TT->>TT: Split into chunks (4500 char max)
        loop For each chunk
            TT->>TT: GoogleTranslator.translate()
        end
        TT-->>IG: Translated document dict
    end
    
    IG->>BGE: extract_from_documents(translated_docs)
    BGE->>BGE: _extract_tone()
    BGE->>BGE: _extract_visual_style()
    BGE->>BGE: _extract_audiences()
    BGE->>BGE: _extract_values()
    BGE->>BGE: _extract_campaign_themes()
    BGE->>BGE: _extract_compliance()
    BGE-->>IG: BrandGuidelinesExtracted
    
    IG->>FS: Save JSON guidelines
    IG->>FS: Save translated docs (optional)
    FS-->>U: Success message
```

## Class Hierarchy

```mermaid
classDiagram
    class DocumentProcessor {
        +process_file(file_path) dict
        +process_directory(dir_path) list
        -_process_pptx(file_path) dict
        -_process_docx(file_path) dict
        -_process_pdf(file_path) dict
        -_process_excel(file_path) dict
    }
    
    class TextTranslator {
        -source_lang: str
        -target_lang: str
        -translator: GoogleTranslator
        -max_chunk_size: int
        +translate(text) str
        +translate_document(document) dict
        +translate_documents(documents) list
        -_translate_chunks(text) str
        -_translate_long_paragraph(paragraph) str
    }
    
    class BrandGuidelinesExtractor {
        -keywords: dict
        +extract_from_documents(documents) BrandGuidelinesExtracted
        +to_json(guidelines, output_path) None
        -_extract_tone(text) str
        -_extract_visual_style(text) str
        -_extract_audiences(text) list
        -_extract_values(text) list
        -_extract_compliance(text) str
        -_extract_campaign_themes(text) list
        -_extract_content_guidelines(text) list
        -_extract_channel_guidelines(text) dict
    }
    
    class BrandGuidelinesExtracted {
        +brand_name: str
        +tone_of_voice: str
        +visual_style: str
        +messaging_principles: list
        +target_audiences: list
        +brand_values: list
        +compliance_notes: str
        +campaign_themes: list
        +content_guidelines: list
        +channel_specific: dict
    }
    
    class BriefIngestor {
        +from_text(text, title) BusinessBrief
    }
    
    class CreativeBriefExtractor {
        +extract(brief) CreativeBrief
        +detect_gaps(brief) dict
    }
    
    class BrandCenterClient {
        <<interface>>
        +fetch_guidelines(brand_id) BrandGuidelines
    }
    
    class LocalBrandCenterClient {
        -guidelines: dict
        +fetch_guidelines(brand_id) BrandGuidelines
    }
    
    class CreativeCampaignWorkflow {
        -brand_client: BrandCenterClient
        -brief_extractor: CreativeBriefExtractor
        -brief_ingestor: BriefIngestor
        +build() CompiledStateGraph
        +run(brief_text, title, brand_id) WorkflowStateData
        -_ingest(state) dict
        -_extract(state) dict
        -_guidelines(state) dict
        -_campaign(state) dict
        -_finalize(state) dict
        -_build_plan(creative_brief, guidelines) dict
    }
    
    class BrandDocumentIngestionWorkflow {
        -doc_processor: DocumentProcessor
        -translator: TextTranslator
        -guidelines_extractor: BrandGuidelinesExtractor
        +process_files(file_paths) dict
        +process_directory(directory_path) dict
        +save_guidelines(guidelines, output_path) None
        +save_translated_documents(documents, output_dir) None
    }
    
    class CLI {
        -parser: ArgumentParser
        +run(argv) WorkflowStateData
        -_load_guidelines(path) dict
        -_display(state) None
    }
    
    BrandGuidelinesExtractor --> BrandGuidelinesExtracted : creates
    BrandDocumentIngestionWorkflow --> DocumentProcessor : uses
    BrandDocumentIngestionWorkflow --> TextTranslator : uses
    BrandDocumentIngestionWorkflow --> BrandGuidelinesExtractor : uses
    CreativeCampaignWorkflow --> BriefIngestor : uses
    CreativeCampaignWorkflow --> CreativeBriefExtractor : uses
    CreativeCampaignWorkflow --> BrandCenterClient : uses
    LocalBrandCenterClient ..|> BrandCenterClient : implements
    CLI --> CreativeCampaignWorkflow : orchestrates
```

## Technology Stack

```mermaid
graph TB
    subgraph "Python 3.11+"
        subgraph "Core Dependencies"
            A[pydantic 2.6+<br/>Data Validation]
            B[langgraph 0.0.50<br/>State Machine]
            C[langchain 0.1+<br/>LLM Framework]
        end
        
        subgraph "Document Processing"
            D[python-pptx<br/>PowerPoint]
            E[python-docx<br/>Word Documents]
            F[pdfplumber<br/>PDF Extraction]
            G[openpyxl<br/>Excel Files]
        end
        
        subgraph "Translation"
            H[deep-translator<br/>Google Translate API]
        end
        
        subgraph "HTTP & Utilities"
            I[requests<br/>HTTP Client]
            J[pathlib<br/>File Operations]
        end
        
        subgraph "Testing"
            K[pytest<br/>Unit Testing]
        end
    end
    
    style A fill:#4caf50
    style B fill:#2196f3
    style C fill:#2196f3
    style H fill:#ff9800
```

---

## Execution Flow Example

### Example 1: Processing a Business Brief

```
User Input: examples/brief.txt + --brand dnb
    ↓
CLI.run()
    ↓
CreativeCampaignWorkflow.run()
    ↓
StateGraph Execution:
    1. Ingest Node → BusinessBrief(title="brief", goals=..., audience=...)
    2. Extract Node → CreativeBrief(goals="Expand into Nordic SMB", ...)
    3. Fetch Guidelines Node → BrandGuidelines(tone="Professional and trustworthy", ...)
    4. Campaign Node → campaign_plan = { channels: [email, social, web], ... }
    5. Finalize Node → WorkflowStateData(complete)
    ↓
CLI._display() → Print JSON output
```

### Example 2: Ingesting Brand Documents

```
User Input: documents directory path
    ↓
BrandDocumentIngestionWorkflow.process_directory()
    ↓
Phase 1: Extract
    For each file → DocumentProcessor.process_file()
        → {file_name, file_type, full_text, ...}
    ↓
Phase 2: Translate
    For each document → TextTranslator.translate_document()
        → Split into chunks → Google Translate API
        → Reassemble translated text
    ↓
Phase 3: Extract Guidelines
    BrandGuidelinesExtractor.extract_from_documents()
        → Keyword matching (tone, visual, messaging, ...)
        → Pattern recognition (bullets, lists, ...)
        → BrandGuidelinesExtracted(tone_of_voice=..., visual_style=..., ...)
    ↓
Phase 4: Output
    Save to examples/dnb_brand_guidelines.json
    Save translated docs to examples/translated/
```
