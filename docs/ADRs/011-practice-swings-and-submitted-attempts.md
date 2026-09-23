# ADR 011: Practice Swings and Submitted Attempts

**Date:** 2026-09-23  
**Status:** Accepted  
**Deciders:** Product Owner, Development Team  
**Supersedes:** Original "all tokens count" scoring mechanics

## Context

The original Token Golf scoring system followed strict golf rules: **every stroke counts**. All attempts (successful and failed) accumulated tokens, encouraging users to get it right the first time.

However, this created several issues:
1. **Fear of experimentation** - Users afraid to try different approaches
2. **Punished learning** - Early failures penalized final score
3. **Unclear goal** - Was it "get it right first try" or "find the optimal solution"?
4. **Poor educational value** - Discouraged iteration and refinement

The game's actual goal is to **teach token optimization** - finding the most efficient prompt. The current system taught "guess right quickly" instead.

## Decision

We will implement a **Practice Swings** system with two distinct actions:

### 1. Practice Swing
- **User Action:** "Practice Swing" button
- **Behavior:** Submit prompt to LLM, get response and validation, see token count
- **Storage:** Saved to database as `attempt_type='practice'`
- **Scoring:** Does **not** count toward leaderboard
- **Limit:** Unlimited practice swings

### 2. Submit & Record Score
- **User Action:** "Submit & Record Score" button
- **Behavior:** Save attempt as `attempt_type='submitted'`
- **Validation:** Only successful attempts can be submitted
- **Scoring:** Counts toward leaderboard
- **Calculation:** Best (lowest tokens) submitted attempt per hole wins
- **Retry:** Can submit multiple times to improve score

### Game Flow
```
1. User writes prompt
2. Click "Practice Swing" → See result
3. If incorrect: Try again (unlimited)
4. If correct: "Submit & Record Score" button enabled
5. Click Submit → Score recorded
6. Can retry hole to improve submitted score
7. Next hole unlocked after first successful submission
```

## Terminology

We chose **"Practice Swing"** over alternatives to maintain golf theme consistency:

| Action | Button Label | Database Value |
|--------|-------------|----------------|
| Try solution without recording | "Practice Swing" | `attempt_type='practice'` |
| Record score for leaderboard | "Submit & Record Score" | `attempt_type='submitted'` |

Rejected alternatives:
- ❌ "Try Solution" / "Submit" - breaks golf theme
- ❌ "Test" / "Commit" - too technical, not thematic
- ❌ "Swing" / "Count This One" - unclear

## Consequences

### Positive
✅ **Encourages experimentation** - Practice swings are free  
✅ **Better learning** - Iterate without penalty  
✅ **Clear optimization goal** - Find the best solution, not the first  
✅ **Lower barrier to entry** - Beginners can practice  
✅ **Analytics-friendly** - Can study optimization patterns  
✅ **Retry-after-success** - Natural improvement path

### Negative
⚠️ **Loses pure golf scoring** - No longer "every stroke counts"  
⚠️ **Database growth** - Storing all practice attempts  
⚠️ **More complex UI** - Two buttons instead of one  
⚠️ **Migration needed** - Existing attempts must be backfilled

### Technical Impact

**Database:**
- Add `attempt_type` VARCHAR(20) to `attempts` table
- Index on `attempt_type` for query performance
- Backfill: Mark existing correct attempts as 'submitted'

**API:**
- Add `action: "practice" | "submit"` parameter to submit endpoint
- Validate: only successful attempts can have `action="submit"`
- Return: `practice_count` and `submitted_count` in response

**Scoring:**
- Filter all leaderboard queries: `WHERE attempt_type='submitted'`
- Per-hole score: MIN(total_tokens) WHERE `attempt_type='submitted'`
- Cumulative tokens: SUM from submitted attempts only

**UI:**
- Two-button interface
- Practice attempt history panel (optional, nice-to-have)
- Enable/disable Submit button based on validation
- Navigation guard: can't advance without submitted attempt

**Tests:**
- Update ~30 scoring tests to filter by attempt_type
- Add validation tests (can't submit failed attempts)
- Update integration/E2E tests for two-button flow

## Implementation Notes

### Database Migration
```sql
ALTER TABLE attempts 
ADD COLUMN attempt_type VARCHAR(20) NOT NULL DEFAULT 'practice';

UPDATE attempts 
SET attempt_type = 'submitted' 
WHERE is_correct = TRUE;

CREATE INDEX ix_attempts_attempt_type ON attempts(attempt_type);
```

### Scoring Query Example
```python
# OLD (all attempts counted)
SELECT SUM(total_tokens) FROM attempts 
WHERE user_id=? AND challenge_id=?

# NEW (only submitted attempts)
SELECT MIN(total_tokens) FROM attempts 
WHERE user_id=? AND challenge_id=? AND attempt_type='submitted'
```

### Validation Rules
1. `action="practice"` → Always allowed
2. `action="submit"` → Only if `is_correct=True`
3. Attempting to submit failed attempt → HTTP 422 Validation Error
4. Can't navigate to next hole without at least one submitted attempt

## Alternatives Considered

### Alternative 1: Limited Practice Swings (5 max)
**Rejected:** Arbitrary limit doesn't add value, just frustration

### Alternative 2: Practice Swings Cost Half Tokens
**Rejected:** Confusing, still penalizes exploration

### Alternative 3: First Attempt Bonus
**Rejected:** Doesn't solve core problem, adds complexity

### Alternative 4: Time-Based Scoring
**Rejected:** Out of scope, different optimization axis

### Alternative 5: No Practice, Just Multiple Submits
**Rejected:** Loses the "strategic pick your best" mechanic, less clear when hole is "done"

## Status

- **Database:** ✅ Schema updated, migration complete
- **API:** 🚧 Models updated, endpoint logic in progress
- **UI:** ⏸️ Not started
- **Tests:** ⏸️ Not started
- **Documentation:** ✅ This ADR, updates pending

## References

- Original design: CLAUDE.md (pre-ADR 011)
- Database model: `app/models/attempt.py`
- Migration: `alembic/versions/87efb90c8ffb_add_attempt_type_for_practice_swings.py`
- Implementation tracking: `PRACTICE_SWINGS_IMPLEMENTATION.md`

## Future Considerations

1. **Practice Attempt History UI** - Show recent practice swings with token counts
2. **Analytics Dashboard** - Track practice patterns, optimization strategies
3. **Hints System** - Cost tokens, guide optimization (post-MVP)
4. **Best Practice Comparison** - Show user's best vs global best after submit
5. **Practice Limits** - Could add optional limits per challenge for advanced difficulty
