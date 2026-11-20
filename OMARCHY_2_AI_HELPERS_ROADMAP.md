# Omarchy 2 AI Helpers Roadmap

## Overview
This roadmap outlines the planned AI helper integration for Omarchy 2, the next-generation Linux desktop distribution combining Arch Linux with Hyprland and a powerful shell ecosystem. The goal is to integrate AI assistance across all user touchpoints while maintaining the lightweight, customizable philosophy of Omarchy.

---

## Vision
**AI-assisted desktop experience** where the operating system understands context, anticipates user needs, and provides helpful suggestions without being intrusive. All processing respects user privacy, with optional on-device AI and cloud fallback.

---

## Phase 1: Foundation (Q1 2027)
### Core AI Infrastructure

| Feature | Description | Priority |
|---------|-------------|----------|
| `omarchy ai status` | Check AI assistant availability (local/cloud) | High |
| `omarchy ai config` | Configure AI settings (model, endpoint, keys) | High |
| `omarchy ai toggle` | Enable/disable AI helpers globally | High |
| AI command prefix | `ai:` prefix for all AI commands | Medium |

### Initial AI Capabilities

| Capability | Use Case | Implementation |
|------------|----------|----------------|
| `omarchy ai explain` | Explain command output or config errors | Read stderr, send to AI |
| `omarchy ai suggest` | Suggest next commands based on context | History analysis + AI |
| `omarchy ai fix` | Auto-fix common configuration issues | Pattern matching + AI |
| `omarchy ai search` | Web-augmented search from command line | Integration with Exa/Perplexity APIs |

### Documentation Updates

- [`docs/ai/overview.md`](docs/ai/overview.md) - High-level AI integration guide
- [`docs/ai/commands.md`](docs/ai/commands.md) - Reference for all `omarchy ai*` commands
- [`docs/ai/privacy.md`](docs/ai/privacy.md) - Data handling and privacy guarantees
- [`CHANGES.ai`](CHANGES.ai) - Migration guide for existing users

---

## Phase 2: Context Awareness (Q2 2027)
### Understanding User Context

| Feature | Description |
|---------|-------------|
| `omarchy ai context` | Show current context (active window, workspace, task) |
| History tracking | Last N commands, frequently used patterns |
| Workspace-aware suggestions | Different suggestions per Hyprland workspace |
| Time-aware hints | Time-of-day relevant commands (e.g., "good morning" setup) |

### AI-Powered Helpers

| Helper | Trigger | Action |
|--------|---------|--------|
| Morning setup | 8AM or `omarchy ai morning` | Configure displays, launch terminals, start services |
| Code assistance | Editing `.py`, `.qml`, `.lua` files | Auto-complete, error explanation, refactoring suggestions |
| System troubleshooting | Error logs, crash reports | Diagnose and suggest fixes |
| Plugin discovery | Browsing `~/.config/omarchy/plugins/` | AI recommends useful plugins |

### New Commands

- `omarchy ai morning` - Good morning sequence with AI
- `omarchy ai explain <command>` - Explain what a command does
- `omarchy ai fix <issue>` - Attempt automatic fix
- `omarchy ai suggest next` - Predict next command based on patterns

### Documentation

- [`docs/ai/context.md`](docs/ai/context.md) - Context awareness design
- [`docs/ai/history.md`](docs/ai/history.md) - Command history and learning
- [`docs/ai/plugins.md`](docs/ai/plugins.md) - AI-assisted plugin recommendations

---

## Phase 3: Modal AI Assistants (Q3 2027)
### Interactive AI Sessions

| Feature | Description |
|---------|-------------|
| `omarchy ai chat` | Open interactive AI chat in terminal |
| Session memory | Remembers context within AI session |
| Multi-model support | Switch between local/ cloud models |
| Quick prompts | `ai: "restart network"` as shortcut |

### Voice & Natural Language

| Feature | Implementation |
|---------|----------------|
| `omarchy ai speak` | Text-to-speech responses |
| Natural language commands | "Make my setup prettier", "slow down the bar" |
| Cross-language | Commands in user's preferred language |

### New UI Elements

- AI indicator in status bar
- Collapsible AI panel in Omarchy shell
- Quick prompt suggestions on bar right-click

### Documentation

- [`docs/ai/chat.md`](docs/ai/chat.md) - Interactive chat guide
- [`docs/ai/voice.md`](docs/ai/voice.md) - Voice/NLU features
- [`docs/ai/models.md`](docs/ai/models.md) - Model management and switching

---

## Phase 4: Automation & Agents (Q4 2027)
### AI Agents for Routine Tasks

| Agent | Task | Safety |
|-------|------|--------|
| `backup-agent` | Automated config backups before changes | Requires confirmation |
| `update-agent` | Check for updates, apply safe ones | User approval for breaking changes |
| `setup-agent` | New user onboarding, config generation | Template-based, no random changes |
| `monitor-agent` | Monitor system health, alert on issues | Predictive, not intrusive |

### Workflow Automation

| Workflow | Trigger | AI Role |
|----------|---------|---------|
| Daily reset | `omarchy ai daily` | Clean up, archive logs, reset states |
| Project setup | `omarchy ai project <name>` | Scaffold new project structure |
| System migration | Moving to new hardware | Transfer configs, adapt settings |

### Safety Features

- **Confirmation prompts** for all AI-initiated changes
- **Undo history** for AI actions
- **Model oversight** - user can review before execution
- **Opt-out per-command** - disable specific AI capabilities

### Documentation

- [`docs/ai/agents.md`](docs/ai/agents.md) - AI agents guide
- [`docs/ai/safety.md`](docs/ai/safety.md) - Safety and control mechanisms
- [`docs/ai/workflows.md`](docs/ai/workflows.md) - Pre-defined workflows

---

## Phase 5: Ecosystem & Extensibility (Q1 2028)
### Developer API

| Feature | Description |
|---------|-------------|
| `omarchy ai tool` | Register custom AI tools/extensions |
| Plugin AI hooks | `omarchy hook ai <event>` |
| Model marketplace | Browse and install AI models |
| API keys management | Secure storage and rotation |

### Community Contributions

- `omarchy ai community` - Browse shared prompts and tools
- Shared prompt library
- Custom tool submissions
- Model configuration templates

### Extensibility Points

- AI command plugins
- Custom model integrations
- Workflow generators
- Notification handlers

### Documentation

- [`docs/ai/developer.md`](docs/ai/developer.md) - Building AI tools for Omarchy
- [`docs/ai/marketplace.md`](docs/ai/marketplace.md) - Community marketplace guide
- [`APIreference.md`](APIreference.md) - Complete API reference

---

## Privacy & Security Framework

### Data Handling Principles

| Principle | Implementation |
|-----------|----------------|
| On-device first | All possible processing runs locally |
| Cloud optional | User chooses cloud models; local fallback always available |
| Minimal data collection | Only essential context sent to AI |
| Transparent logging | Clear audit trail of what data was sent |
| Easy deletion | `omarchy ai purge` - remove all AI data |

### User Controls

| Control | Command |
|---------|---------|
| Disable AI entirely | `omarchy ai toggle off` |
| Per-command consent | Prompt before each AI usage |
| Data retention policy | Configure how long context is kept |
| Export/import | Backup and restore AI preferences |

### Documentation

- [`docs/ai/privacy.md`](docs/ai/privacy.md) (expanded)
- [`docs/ai/security.md`](docs/ai/security.md) - Security model details
- [`COMPLIANCE.md`](COMPLIANCE.md) - GDPR/privacy compliance

---

## Technical Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   Omarchy 2 Desktop                     │
│  ┌─────────────┐  ┌──────────────────────────────┐       │
│  │  Hyprland   │  │  Omarchy Shell (Quickshell)    │       │
│  └──────▲───────┘  └───────▲──────────────────────┘       │
│          │                  │                          │
│  ┌──────▼───────┐  ┌──────────▼─────────────────────┐       │
│  │  AI Core     │  │  AI Helpers (omarchy ai*)          │       │
│  └──────▲───────┘  └───────▲─────────────────────┘       │
│          │                  │                          │
│  ┌──────▼───────┐  ┌──────────▼─────────────────────┐       │
│  │  Local LLM   │  │  Cloud API Gateway               │       │
│  └──────▲───────┘  └───────▲──────────────────────┘       │
│          │                  │                          │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                 Context Store                        │ │
│  │  - Command history                                 │ │ │
│  │  - Active workspace                                │ │ │
│  │  - User preferences                                │ │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### AI Core Components

1. **Context Engine** - Gathers current state (window, workspace, command history)
2. **Intent Classifier** - Determines user intent from command or query
3. **Model Router** - Selects optimal model (local > cloud based on privacy/latency)
4. **Response Formatter** - Converts AI output to actionable commands or natural language
5. **Safety Filter** - Reviews AI suggestions before execution

### Supported Models

| Category | Options |
|----------|---------|
| **Local** | - `llama3` via Ollama \
| | - `mistral` via Ollama \
| | - `phi3` (small, fast) \
| | - Custom quantized models |
| **Cloud** | - OpenAI GPT-4/4o \
| | - Anthropic Claude \
| | - Google Gemini \
| | - Ollama remote |
| **Embedded** | - Tiny LLM for simple queries \
| | - Rule-based fallback |

### Integration Points

- **Shell hooks** - Before/after command execution
- **Plugin system** - Extend AI capabilities via plugins
- **Config files** - AI settings in `~/.config/omarchy/ai/`
- **Shell variables** - `$AI_ENABLED`, `$AI_MODEL`, `$AI_CONTEXT`

---

## Migration Guide

### From Omarchy 1 to 2

| Step | Action |
|------|--------|
| 1. Backup | `omarchy backup create --include-ai` |
| 2. Install | Fresh install or `omarchy update --major` |
| 3. Configure | `omarchy ai config --setup` |
| 4. Migrate prompts | `omarchy ai community migrate` |
| 5. Verify | `omarchy ai status --check` |

### Breaking Changes

| Change | Impact | Mitigation |
|--------|--------|------------|
| AI command prefix change | Old `ai:` commands may need update | Alias old commands |
| Context store format | Existing history needs migration | Automatic migration script |
| Model defaults | Change from cloud to local first | Config update guide |

### Documentation

- [`MIGRATION.md`](MIGRATION.md) - Step-by-step migration
- [`UPGRADE.md`](UPGRADE.md) - What's new and changed

---

## Success Metrics

### User Adoption

- 40% of daily users enable AI helpers within first month
- `omarchy ai` usage grows organically through word-of-mouth
- Positive feedback rate > 80% on AI suggestions

### Technical Performance

- < 2s latency for local LLM queries
- < 5s latency for cloud queries (with network variance)
- < 5% failure rate for AI-assisted commands
- Optional mode maintains 100% functionality without AI

### Privacy Compliance

- Zero data retention when cloud disabled
- Clear opt-in/opt-out flows
- All data handling documented and transparent
- Compatible with GDPR, privacy expectations

---

## Call to Action

### Immediate Next Steps

1. **Approve Phase 1 scope** - Foundation AI infrastructure
2. **Select local LLM** - Choose model for on-device processing
3. **Design privacy model** - User data handling preferences
4. **Set up development environment** - AI tooling, model weights, APIs

### Decision Points (This Quarter)

| Decision | Options | Deadline |
|----------|---------|----------|
| Local LLM choice | Llama3 8B, Mistral 7B, Phi3 3.8B | Week 2 |
| Cloud provider | OpenAI, Anthropic, None (local-only) | Week 3 |
| Opt-in vs opt-out | Users must opt-in to AI | Week 2 |
| Data retention policy | 24h, 7d, 30d, indefinite | Week 3 |

### Quarterly Milestones

- **Q1 2027**: Phase 1 foundation released (`omarchy ai` basic commands)
- **Q2 2027**: Phase 2 context awareness beta
- **Q3 2027**: Phase 3 interactive assistants alpha
- **Q4 2027**: Phase 4 automation agents preview
- **Q1 2028**: Phase 5 ecosystem and extensibility

---

## Related Documentation

See also:
- [`docs/omarchy/overview.md`](docs/omarchy/overview.md) - Omarchy 2 overview
- [`docs/hyprland/roadmap.md`](docs/hyprland/roadmap.md) - Hyprland integration
- [`docs/shell/roadmap.md`](docs/shell/roadmap.md) - Shell evolution
- [`CHANGELOG.md`](CHANGELOG.md) - All changes by version
- [`CONTRIBUTING.md`](CONTRIBUTING.md) - How to contribute AI features

---

*Roadmap version 1.0 - Generated for Omarchy 2 AI Helpers planning*
*Last updated: November 2026*