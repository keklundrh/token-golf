# Token Golf Challenges

This directory contains challenge definitions for Token Golf.

## Structure

Each challenge is in its own directory:
```
challenges/
├── hole-001/
│   ├── challenge.yaml      # Challenge definition
│   └── assets/             # Context files, test data
├── hole-002/
│   └── ...
└── README.md               # This file
```

## Creating Challenges

See [CHALLENGE_FORMAT.md](../docs/CHALLENGE_FORMAT.md) for the complete specification.

## Current Challenges

### Placeholder Challenges (To Be Completed)

1. **hole-001** - Easy coding challenge (placeholder)
2. **hole-002** - Medium extraction challenge (placeholder)
3. **hole-003** - Medium coding challenge (placeholder)
4. **hole-004** - Hard question answering challenge (placeholder)
5. **hole-005** - Easy classification challenge (placeholder)

All placeholders need:
- Complete task descriptions
- Validation criteria
- Test data
- Token estimates
- Context files (if applicable)

## Validation

Run the challenge validation script before committing:
```bash
python scripts/validate_challenges.py
```

## Challenge Guidelines

- **Clear Requirements**: No ambiguity in what "correct" means
- **Fair Validation**: Deterministic, reproducible results
- **Token Efficiency Focus**: Challenge should teach optimization
- **Appropriate Difficulty**: Match estimated tokens to difficulty level
- **Test Thoroughly**: Solve your own challenge before submitting
