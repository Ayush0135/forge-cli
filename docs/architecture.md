---
noteId: "67c327d08f7311f1b68823b51e8a11c5"
tags: []

---

# Forge CLI Architecture

The architecture is highly modular, designed to support multiple AI providers, comprehensive tooling, and intelligent context injection.

```mermaid
graph TD
    subgraph Interfaces
        CLI[Interactive CLI]
    end

    subgraph Core
        Session[Session Manager]
        ContextEngine[Context Engine]
        Memory[SQLite Memory]
        Agent[Autonomous Agent]
    end

    subgraph Providers
        Factory[Provider Factory]
        Gemini[Gemini API]
        OpenAI[OpenAI / OpenRouter]
        Ollama[Ollama API]
    end

    subgraph Tools
        ToolManager[Tool Manager]
        Shell[Shell Execution]
        Search[Code/File Search]
        Git[Git Integration]
        FS[Safe File Editing]
    end

    CLI --> Session
    Session --> ContextEngine
    Session --> Memory
    Session --> Agent
    
    Agent --> Factory
    Factory --> Gemini
    Factory --> OpenAI
    Factory --> Ollama
    
    Agent <--> ToolManager
    ToolManager --> Shell
    ToolManager --> Search
    ToolManager --> Git
    ToolManager --> FS
```

## Flow Overview
1. **User Input:** Received via the interactive Typer/Rich CLI.
2. **Session Setup:** The `Session` retrieves history from `Memory` and builds a system prompt using the `ContextEngine` (which scans the project tree, git status, and README).
3. **Agent Loop:** The `Agent` queries the `ProviderFactory` and evaluates tool calls.
4. **Tool Execution:** When a model calls a tool, the `Agent` passes the request to the `ToolManager`, which validates and executes tools safely without crashing the agent.
5. **Observation:** Tool outputs are fed back to the model for continuous iteration.
