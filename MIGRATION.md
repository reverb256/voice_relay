# Migration Guide - Omarchy 2 AI Helpers

## From Omarchy 1 to Omarchy 2

### Step 1: Backup Existing AI Data
```bash
# Create backup including AI data
omarchy backup create --include-ai

# Or manual backup of AI configuration
cp ~/.config/omarchy/ai/ ~/.config/omarchy/ai-backup-$(date +%Y%m%d).bak
```

### Step 2: Fresh Install or Update
```bash
# Fresh install (recommended for AI features)
#   Download Omarchy 2 ISO or follow install guide

# Or major update
omarchy update --major
```

### Step 3: Configure AI Settings
```bash
# Quick setup with default local model
omarchy ai --setup

# Or interactive configuration
omarchy ai --config
```

### Step 4: Migrate Prompts and Preferences
```bash
# Migrate from Omarchy 1 community prompts
omarchy ai community migrate

# Or manual migration
cp ~/.omarchy1/ai-prompts.md ~/.config/omarchy/ai/prompts.md
```

### Step 5: Verify Installation
```bash
# Check AI status
omarchy ai --status --check

# Verify local model is working
omarchy ai --model phi3 --test

# Confirm all settings are as expected
omarchy ai config --review
```

## Breaking Changes & Mitigations

### AI Command Prefix Change
- **Impact**: Old `ai:` commands may need update
- **Mitigation**: Alias old commands automatically
  ```bash
  # Old commands still work via alias
  ai:status  # Works -> omarchy ai --status
  ai:config  # Works -> omarchy ai --config
  ```

### Context Store Format Change
- **Impact**: Existing history needs migration
- **Mitigation**: Automatic migration script runs on first launch
  ```bash
  # Migration runs automatically
  omarchy ai --status
  # Prompt appears if migration needed
  ```

### Model Defaults Change
- **Impact**: Change from cloud to local first
- **Mitigation**: Config update guide
  ```bash
  # Update to local-first settings
  omarchy ai --model phi3
  omarchy ai --toggle local
  ```

## Post-Migration Checklist

### Verify AI Functionality
- [ ] `omarchy ai --status` shows expected configuration
- [ ] Local model responds to queries
- [ ] Cloud API (if configured) works
- [ ] AI helpers can be toggled on/off

### Check Privacy Settings
- [ ] Data retention policy configured
- [ ] Opt-in/opt-out preferences set
- [ ] Export created for safety

### Confirm Roadmap Progress
- [ ] Phase 1 foundation verified (Issue #1)
- [ ] Issue tracker updated for next phases
- [ ] Documentation reviewed and updated

## Known Issues & Workarounds

### Local Model Not Found
```bash
# Install Phi-3 model
omarchy ai --setup

# Or install manually via Ollama
ollama pull phi3
```

### Cloud API Key Not Accepted
```bash
# Re-enter API key
omarchy ai --config

# Verify key format (OpenAI/Anthropic/Gemini)
```

### Context Not Recognized
```bash
# Refresh context store
omarchy ai --status --refresh

# Check hyprland workspace integration
```

## Upgrade Path Q1 2027

### Phase 1 Release (Current)
- Basic `omarchy ai` commands
- Local LLM support
- Configurable models
- Enable/disable toggles

### Phase 2 (Q2 2027) - After Upgrade
- Context awareness features
- Workspace-aware suggestions
- Time-aware hints
- Command history tracking

### Phase 3 (Q3 2027) - After Upgrade
- Interactive chat sessions
- Session memory
- Multi-model switching
- Quick prompts

### Phase 4 (Q4 2027) - After Upgrade
- AI agents for routines
- Workflow automation
- Daily reset, project setup
- Safety features

### Phase 5 (Q1 2028) - After Upgrade
- Developer API
- Model marketplace
- Community contributions
- Extensibility points

## Migration Timeline

| Quarter | Milestone |
|---------|-----------|
| Q1 2027 | Phase 1 foundation released |
| Q2 2027 | Phase 2 context awareness beta |
| Q3 2027 | Phase 3 interactive assistants alpha |
| Q4 2027 | Phase 4 automation agents preview |
| Q1 2028 | Phase 5 ecosystem and extensibility |

## Need Help?

- [GitHub Issues](https://github.com/reverb256/voice_relay/issues) - Report migration problems
- [Discussions](https://github.com/reverb256/voice_relay/discussions) - Ask migration questions
- [Documentation](docs/ai/) - Read detailed guides for each phase