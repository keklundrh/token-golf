# Root Documentation Policy

**Policy**: Keep root directory clean - only essential user-facing docs

---

## ✅ Allowed in Root Directory

These files serve immediate user needs and are appropriately in root:

### User-Facing Documentation
- **README.md** - Project overview, first thing users see
- **QUICKSTART.md** - Quick setup guide for new users
- **CONTRIBUTING.md** - Contribution guidelines
- **LICENSE** - Project license (when added)

### AI Assistant Context
- **CLAUDE.md** - Comprehensive context for AI assistants

### Project Management
- **PROJECT_STATUS.md** - Current development state

---

## ❌ Not Allowed in Root Directory

These belong in organized subdirectories:

### Phase Documentation → `docs/phases/`
- ❌ PHASE_X.Y_COMPLETE.md
- ❌ PHASE_X.Y_CONSISTENCY_CHECK.md
- ❌ PHASE_X.Y_FIXES.md
- ❌ PHASE_X.Y_COMPREHENSIVE_VERIFICATION.md
- ❌ Any phase-specific documentation

### Architecture Decisions → `docs/ADRs/`
- ❌ NNN-decision-name.md

### Development Guides → `docs/`
- ❌ ARCHITECTURE.md
- ❌ DEVELOPMENT_PHASES.md
- ❌ CHALLENGE_FORMAT.md
- ❌ MVP_SCOPE.md
- ❌ DOCUMENTATION_REORGANIZATION.md

---

## Current Root Structure (Correct)

```
token-golf/
├── README.md                 ✅ User overview
├── QUICKSTART.md             ✅ Getting started
├── CONTRIBUTING.md           ✅ How to contribute
├── CLAUDE.md                 ✅ AI context
├── PROJECT_STATUS.md         ✅ Current state
├── .gitignore               ✅ Git config
├── .env.example             ✅ Config template
├── docker-compose.yml       ✅ Container setup
├── Dockerfile               ✅ Container build
├── requirements.txt         ✅ Dependencies
├── alembic.ini              ✅ DB migrations config
├── app/                     ✅ Application code
├── docs/                    ✅ Documentation
├── challenges/              ✅ Challenge definitions
├── static/                  ✅ Frontend assets (future)
└── tests/                   ✅ Test suite (future)
```

---

## Why This Policy?

### Benefits
1. **Clean Root**: Easy to navigate, not cluttered
2. **Clear Purpose**: Each file in root has obvious value to users
3. **Organized Details**: Internal docs in logical subdirectories
4. **Scalable**: Won't get messy as project grows
5. **Professional**: Standard open-source project structure

### Anti-Pattern
```
token-golf/
├── README.md
├── PHASE_0_COMPLETE.md        ❌ Should be in docs/phases/
├── PHASE_1.2_COMPLETE.md      ❌ Should be in docs/phases/
├── CONSISTENCY_CHECK.md       ❌ Should be in docs/phases/
├── VERIFICATION_REPORT.md     ❌ Should be in docs/phases/
├── ARCHITECTURE.md            ❌ Should be in docs/
└── ...cluttered root
```

---

## Enforcement

### Before Committing
1. Check `git status`
2. If new `.md` file in root, ask:
   - Is this user-facing? (README, QUICKSTART, CONTRIBUTING)
   - Is this AI context? (CLAUDE.md)
   - Is this project status? (PROJECT_STATUS.md)
3. If NO to all → move to appropriate `docs/` subdirectory

### When Creating Documentation
1. **Phase docs** → `docs/phases/PHASE_X.Y_TYPE.md`
2. **Architecture decisions** → `docs/ADRs/NNN-title.md`
3. **Development guides** → `docs/GUIDE_NAME.md`
4. **User guides** → Root or `docs/` depending on audience

---

## Migration Record

### 2026-09-21: Documentation Reorganization
- ✅ Moved 7 PHASE_*.md files from root/docs to `docs/phases/`
- ✅ Moved COMPREHENSIVE_CONSISTENCY_VERIFICATION.md to `docs/phases/PHASE_2.1_COMPREHENSIVE_VERIFICATION.md`
- ✅ Created this policy to prevent future violations

**Before**: 1 phase doc in root, 6 in docs/, mixed with other docs  
**After**: 0 in root, 8 organized in `docs/phases/`

---

## Related Policies

- **File Naming**: See `docs/phases/README.md`
- **Documentation Organization**: See `docs/ADRs/008-documentation-organization.md`
- **Development Process**: See `CONTRIBUTING.md`

---

**Policy Owner**: Token Golf Team  
**Last Updated**: 2026-09-21  
**Status**: Active
