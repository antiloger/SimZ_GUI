# SimZ Conceptual Diagrams

This document provides visual representations of the key concepts in SimZ to complement the conceptual overview.

## 1. Core Components of SimZ Architecture

```mermaid
graph TD
    subgraph "SimZ Architecture"
        A[Project Manager] --> B[File Manager]
        A --> C[DB Manager]
        A --> D[Simulation Builder]
        D --> E[Component System]
        D --> F[GenType System]
        D --> G[Workflow Graph]
        E --> H[Component Registry]
        E --> I[Component Execution]
        F --> J[Entity Definitions]
        F --> K[Container System]
        G --> L[Edge Connections]
        G --> M[Execution Paths]
    end
    
    style A fill:#f9d5e5,stroke:#333,stroke-width:2px
    style D fill:#eeeeee,stroke:#333,stroke-width:2px
    style E fill:#d5e8d4,stroke:#333,stroke-width:2px
    style F fill:#dae8fc,stroke:#333,stroke-width:2px
    style G fill:#fff2cc,stroke:#333,stroke-width:2px
```

## 2. Discrete Event Simulation Timeline

```mermaid
gantt
    title SimZ Discrete Event Timeline
    dateFormat  s
    axisFormat %S
    
    section Events
    Customer Arrival      :a1, 0, 1s
    Order Placement       :a2, after a1, 2s
    Food Preparation Start:a3, after a2, 1s
    Food Preparation End  :a4, after a3, 5s
    Food Delivery         :a5, after a4, 1s
    Customer Departure    :a6, after a5, 3s
    
    section Simulation Clock
    Clock Jumps           :crit, 0, 13s
```

## 3. Component Interaction Model

```mermaid
graph LR
    subgraph "Component Interaction"
        A[Generator] -->|Creates Entities| B[Entity Container]
        B -->|Flows To| C[Resource 1]
        C -->|Processes| D[Updated Entity]
        D -->|Flows To| E[Resource 2]
        E -->|Processes| F[Final Entity]
        F -->|Exits System| G[Output]
    end
    
    style A fill:#f9d5e5,stroke:#333,stroke-width:2px
    style B fill:#dae8fc,stroke:#333,stroke-width:2px
    style C fill:#d5e8d4,stroke:#333,stroke-width:2px
    style D fill:#dae8fc,stroke:#333,stroke-width:2px
    style E fill:#d5e8d4,stroke:#333,stroke-width:2px
    style F fill:#dae8fc,stroke:#333,stroke-width:2px
    style G fill:#fff2cc,stroke:#333,stroke-width:2px
```

## 4. Workflow Example: Coffee Shop Simulation

```mermaid
graph TD
    subgraph "Coffee Shop Simulation"
        A[Customer Generator] -->|Customer| B[Order Queue]
        B -->|Customer Order| C[Barista Resource]
        C -->|Prepared Order| D[Pickup Counter]
        D -->|Completed Order| E[Customer Exit]
        
        F[Supply Generator] -->|Supplies| G[Inventory]
        G -->|Ingredients| C
    end
    
    style A fill:#f9d5e5,stroke:#333,stroke-width:2px
    style B fill:#fff2cc,stroke:#333,stroke-width:2px
    style C fill:#d5e8d4,stroke:#333,stroke-width:2px
    style D fill:#fff2cc,stroke:#333,stroke-width:2px
    style E fill:#eeeeee,stroke:#333,stroke-width:2px
    style F fill:#f9d5e5,stroke:#333,stroke-width:2px
    style G fill:#dae8fc,stroke:#333,stroke-width:2px
```

## 5. Entity Structure and Flow

```mermaid
classDiagram
    class GenContainer {
        +containerId: string
        +Data: Dictionary
        +targetComp: string
        +targetHandler: string
        +Flag: string
        +priority: int
    }
    
    class GenType {
        +typeName: string
        +attributes: Dictionary
        +updateValue(key, value)
        +getValue(key)
    }
    
    class Workflow {
        +components: List
        +edges: List
        +findNextComponent(source, handler)
        +getExecutionPath()
    }
    
    GenContainer "1" --> "1..*" GenType: contains
    Workflow "1" --> "0..*" GenContainer: routes
```

## 6. Mental Model for Simulation Design

```mermaid
graph TD
    subgraph "Simulation Design Process"
        A[Identify Entities] --> B[Define Attributes]
        B --> C[Map Process Flow]
        C --> D[Identify Resources & Constraints]
        D --> E[Define Component Behaviors]
        E --> F[Connect Components]
        F --> G[Run Simulation]
        G --> H[Analyze Results]
        H --> I[Refine Model]
        I -->|Iterate| C
    end
    
    style A fill:#f9d5e5,stroke:#333,stroke-width:2px
    style B fill:#dae8fc,stroke:#333,stroke-width:2px
    style C fill:#d5e8d4,stroke:#333,stroke-width:2px
    style D fill:#fff2cc,stroke:#333,stroke-width:2px
    style E fill:#eeeeee,stroke:#333,stroke-width:2px
    style F fill:#f9d5e5,stroke:#333,stroke-width:2px
    style G fill:#dae8fc,stroke:#333,stroke-width:2px
    style H fill:#d5e8d4,stroke:#333,stroke-width:2px
    style I fill:#fff2cc,stroke:#333,stroke-width:2px
```

## 7. Component State and Execution

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Receiving: Entity Arrives
    Receiving --> Processing: Begin Processing
    Processing --> Sending: Processing Complete
    Sending --> Idle: Entity Sent to Next Component
    
    Idle --> Generating: Generator Creates Entity
    Generating --> Sending: Entity Created
    
    Processing --> Queued: Resource Busy
    Queued --> Processing: Resource Available
```

## 8. Project Structure Visualization

```mermaid
graph TD
    subgraph "Project Structure"
        A[Project] --> B[config.json]
        A --> C[Run Directory]
        A --> D[Save Directory]
        
        C --> E[Run ID Folders]
        E --> F[CSV Logs]
        E --> G[Simulation Data]
        
        D --> H[dataState.json]
        D --> I[genState.json]
        D --> J[edge.json]
    end
    
    style A fill:#f9d5e5,stroke:#333,stroke-width:2px
    style B fill:#dae8fc,stroke:#333,stroke-width:2px
    style C fill:#d5e8d4,stroke:#333,stroke-width:2px
    style D fill:#fff2cc,stroke:#333,stroke-width:2px
    style E fill:#eeeeee,stroke:#333,stroke-width:2px
    style F fill:#f9d5e5,stroke:#333,stroke-width:2px
    style G fill:#dae8fc,stroke:#333,stroke-width:2px
    style H fill:#d5e8d4,stroke:#333,stroke-width:2px
    style I fill:#fff2cc,stroke:#333,stroke-width:2px
    style J fill:#eeeeee,stroke:#333,stroke-width:2px
```

## Notes on Using These Diagrams

These diagrams are created using Mermaid, a markdown-based diagramming tool. They can be rendered in many markdown viewers that support Mermaid syntax, including GitHub, GitLab, and various markdown editors.

The diagrams provide visual representations of:

1. The overall SimZ architecture
2. How discrete events work in a timeline
3. How components interact with entities
4. A practical workflow example (coffee shop)
5. The structure of entities and their flow
6. The mental model for designing simulations
7. Component states and execution flow
8. The physical project structure

These visuals complement the conceptual overview by providing a way to see the relationships between different elements of the SimZ system.
