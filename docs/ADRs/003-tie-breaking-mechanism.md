# ADR 003: Tie-Breaking Mechanism

## Status

Accepted

## Context

In Token Golf, players compete to complete challenges using the fewest tokens. It is likely that multiple players will achieve the same token count on a given challenge, especially:
- Easy challenges with obvious optimal solutions
- When players share strategies
- In large conference settings with many participants

We need a fair, engaging way to determine a single winner when players tie for first place.

### Considered Factors
- Golf traditionally handles ties with playoff holes
- Educational value - more play = more learning
- Conference demo excitement - tiebreakers are dramatic
- Fairness - all players should have equal opportunity
- Simplicity - easy to understand and implement

## Decision

**When multiple players tie for first place, they will compete in an additional challenge ("sudden death playoff") until a single winner emerges.**

### Specifics
- Only applies to ties for **first place** (not other positions)
- Tiebreaker challenge is selected from the challenge pool
- Can be same difficulty or increased difficulty (TBD - likely same)
- Repeat process if they tie again on the tiebreaker
- All other rankings remain unchanged during tiebreaker
- Tiebreaker tokens count separately (not added to original score)

### Example Flow
```
Original Challenge Results:
1. Blue-Augusta-7: 150 tokens
1. Green-Pebble-3: 150 tokens (TIE)
3. Red-StAndrews-5: 180 tokens

→ Tiebreaker Challenge for Blue-Augusta-7 and Green-Pebble-3

Tiebreaker Results:
- Blue-Augusta-7: 200 tokens
- Green-Pebble-3: 175 tokens

Final Results:
1. Green-Pebble-3 (winner)
2. Blue-Augusta-7
3. Red-StAndrews-5
```

## Consequences

### Positive Consequences

- **True to Golf Spirit**: Playoff holes are authentic to golf
- **Educational**: Players get more practice optimizing prompts
- **Engaging**: Creates drama and excitement in competitions
- **Fair**: All tied players compete on equal footing
- **Simple**: Easy to understand and explain
- **Deterministic**: Eventually produces a single winner
- **Flexible**: Can repeat indefinitely until tie is broken

### Negative Consequences

- **Longer Events**: Tiebreakers extend competition time
- **Unpredictable Duration**: Can't guarantee when event will end
- **Player Fatigue**: Multiple tiebreakers could be exhausting
- **Luck Factor**: Tiebreaker challenge might favor certain players

### Risks

- **Risk**: Tiebreakers go on indefinitely
  - **Mitigation**: Set maximum tiebreaker rounds (e.g., 3), then use secondary metric
  - **Likelihood**: Low - probability decreases with each round

- **Risk**: Players intentionally tie to get more practice
  - **Mitigation**: Not really a problem - more engagement is good
  - **Likelihood**: Low - competitive players want to win

- **Risk**: Conference schedule runs long
  - **Mitigation**: Include tiebreaker time in event planning, set hard cutoffs
  - **Likelihood**: Medium - plan for this in scheduling

## Alternatives Considered

### Alternative 1: First to Complete Wins

- **Description**: If tied on tokens, earliest completion time wins
- **Pros**: 
  - Simple to implement
  - Immediate resolution
  - Rewards speed
- **Cons**: 
  - Penalizes careful optimization
  - Timestamp precision issues
  - Less engaging (no additional play)
  - Not true to golf spirit
- **Why not chosen**: Penalizes thoughtful play, less exciting

### Alternative 2: Shared Victory

- **Description**: Multiple winners can share first place
- **Pros**: 
  - No additional complexity
  - Event ends on schedule
  - Recognizes equal achievement
- **Cons**: 
  - Less satisfying for competitive players
  - Not traditional in golf
  - Anticlimatic for demos
  - Harder to award prizes
- **Why not chosen**: Less engaging, not true to competitive spirit

### Alternative 3: Fewest Attempts Wins

- **Description**: Use number of attempts as tiebreaker
- **Pros**: 
  - Simple
  - Immediate
  - Rewards efficiency
- **Cons**: 
  - Penalizes learning/iteration
  - Players might rush
  - Secondary metric feels arbitrary
  - Not golf-like
- **Why not chosen**: Penalizes the learning process we want to encourage

### Alternative 4: Random Selection

- **Description**: Randomly pick winner from tied players
- **Pros**: 
  - Immediate
  - Simple
  - No bias
- **Cons**: 
  - Not skill-based
  - Feels unfair
  - Anticlimactic
  - Not educational
- **Why not chosen**: Eliminates skill component, not engaging

### Alternative 5: Token Cost Tiebreaker

- **Description**: Lowest dollar cost wins (some models cost more per token)
- **Pros**: 
  - Teaches cost optimization
  - Rewards cheaper models
- **Cons**: 
  - Depends on provider pricing
  - May not apply to all deployments
  - Adds complexity
  - Not always available (OpenShift AI)
- **Why not chosen**: Not applicable in all environments

## Implementation Notes

### Database Schema Impact
- Add `is_tiebreaker` boolean to challenges
- Track `tiebreaker_for_session` to link to original competition
- Record `tiebreaker_round` number (1, 2, 3...)

### UI Changes
- Display "TIEBREAKER" badge on tiebreaker challenges
- Show original tied players during tiebreaker
- Update leaderboard to show tiebreaker in progress

### Game Flow
```python
def check_for_tiebreaker(session_id):
    """Check if tiebreaker is needed."""
    scores = get_final_scores(session_id)
    first_place_score = scores[0].total_tokens
    tied_players = [s for s in scores if s.total_tokens == first_place_score]
    
    if len(tied_players) > 1:
        return create_tiebreaker_challenge(tied_players, session_id)
    return None
```

### Future Enhancements
- Allow configuration of tiebreaker difficulty (same, harder, easier)
- Set maximum tiebreaker rounds
- Display tiebreaker history
- Statistics on tiebreaker frequency

## References

- [PGA Playoff Rules](https://www.pga.com/rules/playoff-formats)
- [Golf Sudden Death Format](https://en.wikipedia.org/wiki/Sudden_death_(sport))

---

**Date**: 2026-09-09  
**Author**: Token Golf Team  
**Reviewers**: Karl Eklund
