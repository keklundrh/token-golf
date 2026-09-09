# Challenge Format Specification

This document describes the YAML format for Token Golf challenges.

## Overview

Challenges are defined in YAML files located in `challenges/hole-XXX/challenge.yaml`. Each challenge represents one "hole" in the game, with a specific task for users to complete using an LLM.

## Directory Structure

```
challenges/
├── README.md                    # Challenge authoring guide
├── schema.yaml                  # YAML schema for validation
├── hole-001/
│   ├── challenge.yaml          # Challenge definition
│   └── assets/
│       ├── context_file_1.csv  # Context files
│       ├── context_file_2.txt
│       └── test_data.json      # Test data for validation
├── hole-002/
│   ├── challenge.yaml
│   └── assets/
│       └── ...
└── ...
```

## YAML Format

### Complete Example

```yaml
id: hole-001
name: "Sum Function"
difficulty: easy
description: |
  Write a Python function called `sum_numbers` that takes a list of integers
  and returns their sum.
  
  The function should handle empty lists by returning 0.
  
task_type: coding

validation:
  type: test_cases
  criteria:
    - name: "Basic sum"
      input: 
        numbers: [1, 2, 3]
      expected_output: 6
      
    - name: "Empty list"
      input:
        numbers: []
      expected_output: 0
      
    - name: "Negative numbers"
      input:
        numbers: [-5, 5, 10]
      expected_output: 10

context_files:
  - name: "examples.txt"
    path: "./challenges/hole-001/assets/examples.txt"
    description: "Example inputs and outputs"
    removable: true
    editable: false
    default_included: true

system_prompt:
  default: "You are a helpful Python coding assistant. Write clean, efficient code."
  removable: false
  editable: true

parameters:
  max_iterations: 10
  time_limit_seconds: null
  hints_available: 0

metadata:
  author: "Token Golf Team"
  created_date: "2026-09-09"
  tags: ["python", "basics", "functions"]
  estimated_tokens_expert: 150
  estimated_tokens_beginner: 800
  estimated_difficulty: 1.0
```

## Field Specifications

### Required Fields

#### `id` (string)
- Unique identifier for the challenge
- Format: `hole-XXX` where XXX is a zero-padded number
- Examples: `hole-001`, `hole-042`, `hole-150`

#### `name` (string)
- Display name for the challenge
- Short, descriptive title (< 50 characters)
- Examples: "Sum Function", "Extract Email Addresses", "Classify Sentiment"

#### `difficulty` (enum)
- One of: `easy`, `medium`, `hard`, `expert`
- Used for filtering and competition setup
- Should reflect token efficiency challenge, not task complexity

#### `description` (string, multi-line)
- Complete task description
- What the user needs to accomplish
- Any constraints or requirements
- Expected output format
- Use YAML multi-line syntax (`|` or `>`)

#### `task_type` (enum)
- One of: `coding`, `extraction`, `question_answering`, `generation`, `classification`, `transformation`
- Categorizes the type of challenge

#### `validation` (object)
- Defines how to validate user responses
- See **Validation Types** section below

### Optional Fields

#### `context_files` (list)
- Files available to the user as context
- Each file is an object with:
  - `name` (string): Display name
  - `path` (string): Relative path from repo root
  - `description` (string): What the file contains
  - `removable` (boolean): Can user remove this file?
  - `editable` (boolean): Can user edit this file in UI?
  - `default_included` (boolean): Included by default?

#### `system_prompt` (object)
- Default system prompt configuration
- Fields:
  - `default` (string): The default system prompt text
  - `removable` (boolean): Can user remove system prompt?
  - `editable` (boolean): Can user edit system prompt?

#### `parameters` (object)
- Game parameters for this challenge
- Fields:
  - `max_iterations` (int, nullable): Maximum attempts allowed (null = unlimited)
  - `time_limit_seconds` (int, nullable): Time limit (null = no limit)
  - `hints_available` (int): Number of hints available (future feature)

#### `metadata` (object)
- Challenge metadata
- Fields:
  - `author` (string): Challenge creator
  - `created_date` (string, YYYY-MM-DD): Creation date
  - `tags` (list of strings): Categorization tags
  - `estimated_tokens_expert` (int): Expected tokens for expert user
  - `estimated_tokens_beginner` (int): Expected tokens for beginner
  - `estimated_difficulty` (float): Numerical difficulty rating (1.0-10.0)

## Validation Types

### 1. Test Cases (`test_cases`)

For coding challenges where output can be verified programmatically.

```yaml
validation:
  type: test_cases
  language: python  # python, javascript, etc.
  criteria:
    - name: "Test case name"
      input:
        param1: value1
        param2: value2
      expected_output: expected_value
      timeout_ms: 1000
      
    - name: "Another test"
      input:
        param1: value3
      expected_output: expected_value2
```

**Execution:**
- Extract code from LLM response
- Execute code with test inputs
- Compare outputs

**Fields:**
- `language`: Programming language (affects code extraction)
- `criteria`: List of test cases
  - `name`: Test case description
  - `input`: Dictionary of input parameters
  - `expected_output`: Expected result
  - `timeout_ms`: Execution timeout (optional)

### 2. Exact Match (`exact_match`)

For tasks with a single correct string answer.

```yaml
validation:
  type: exact_match
  criteria:
    expected_answer: "The exact correct answer"
    case_sensitive: false
    trim_whitespace: true
```

**Fields:**
- `expected_answer`: The correct answer string
- `case_sensitive`: Whether to match case (default: false)
- `trim_whitespace`: Whether to trim whitespace (default: true)

### 3. Semantic Similarity (`semantic_similarity`)

For open-ended answers where meaning matters more than exact wording.

```yaml
validation:
  type: semantic_similarity
  criteria:
    reference_answer: "The capital of France is Paris."
    similarity_threshold: 0.85
    model: "text-embedding-3-small"
```

**Fields:**
- `reference_answer`: The reference correct answer
- `similarity_threshold`: Minimum cosine similarity (0.0-1.0)
- `model`: Embedding model to use

**Execution:**
- Embed reference answer
- Embed user's answer
- Calculate cosine similarity
- Pass if similarity >= threshold

### 4. Pattern Match (`pattern_match`)

For extraction tasks with regex validation.

```yaml
validation:
  type: pattern_match
  criteria:
    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    description: "Valid email address"
    flags: ["IGNORECASE"]
```

**Fields:**
- `pattern`: Regular expression pattern
- `description`: Human-readable description
- `flags`: Regex flags (optional)

### 5. Multiple Choice (`multiple_choice`)

For classification tasks with predefined options.

```yaml
validation:
  type: multiple_choice
  criteria:
    correct_answer: "B"
    options:
      A: "Option A text"
      B: "Option B text"
      C: "Option C text"
```

**Fields:**
- `correct_answer`: The correct option key
- `options`: Dictionary of option keys to text

### 6. Custom Script (`custom_script`)

For complex validation requiring custom logic.

```yaml
validation:
  type: custom_script
  criteria:
    script_path: "./challenges/hole-042/validator.py"
    function_name: "validate_response"
```

**Script Requirements:**
- Python script with validation function
- Function signature: `def validate_response(user_response: str) -> ValidationResult`
- Returns object with `is_correct: bool` and `feedback: str`

Example validator:
```python
from typing import Dict, Any

def validate_response(user_response: str) -> Dict[str, Any]:
    """
    Custom validation logic.
    
    Args:
        user_response: The LLM's response text
        
    Returns:
        Dictionary with:
        - is_correct: bool
        - feedback: str (optional)
        - score: float (optional, 0.0-1.0)
    """
    # Custom validation logic here
    if some_condition(user_response):
        return {
            "is_correct": True,
            "feedback": "Excellent work!"
        }
    else:
        return {
            "is_correct": False,
            "feedback": "Try again. Hint: check the format."
        }
```

## Context Files

### Purpose
Context files provide additional information users can include in their prompts. Users can:
- Include/exclude files (if `removable: true`)
- Edit file content in UI (if `editable: true`)
- See which files are active via pill UI

### File Types
- `.txt` - Text documents
- `.csv` - Data files
- `.json` - Structured data
- `.md` - Markdown documentation
- `.py` / `.js` / etc. - Code samples

### Best Practices
1. Keep files small (< 10KB) to avoid token bloat
2. Include only relevant information
3. Make files truly optional (challenge should be solvable without them)
4. Use descriptive filenames
5. Document what each file contains

### Example Context File Structure

```
challenges/hole-025/assets/
├── customer_data.csv       # Sample data
├── schema_definition.txt   # Data schema
├── example_output.json     # Expected format
└── hints.md               # Optional hints
```

## Challenge Difficulty Guidelines

### Easy (estimated: 100-300 tokens)
- Clear, straightforward task
- Minimal context needed
- Single-step solution
- Obvious validation
- Example: "Write a function that adds two numbers"

### Medium (estimated: 300-800 tokens)
- Requires some reasoning
- Multiple pieces of context
- Multi-step solution
- Some ambiguity to resolve
- Example: "Parse CSV and calculate statistics"

### Hard (estimated: 800-2000 tokens)
- Complex task with edge cases
- Multiple context files
- Requires optimization
- Non-obvious solution
- Example: "Debug this code and optimize for performance"

### Expert (estimated: 2000+ tokens)
- Highly complex task
- Requires deep reasoning
- Many context files
- Multiple valid approaches
- Example: "Implement algorithm with specific constraints"

## Writing Good Challenges

### Principles

1. **Clear Success Criteria**
   - User should know exactly what "correct" means
   - Validation should be deterministic
   - No subjective evaluation

2. **Fair Token Counting**
   - Task should be achievable within reasonable token budget
   - Don't require excessive trial-and-error
   - Provide enough context without being wasteful

3. **Educational Value**
   - Each challenge teaches something about token efficiency
   - Progressive difficulty helps users improve
   - Feedback helps users understand their mistakes

4. **Engaging Content**
   - Interesting, realistic tasks
   - Variety in task types
   - Appropriate difficulty progression

### Anti-Patterns

❌ **Ambiguous Requirements**
```yaml
description: "Make the code better"
# Too vague - what does "better" mean?
```

✅ **Clear Requirements**
```yaml
description: |
  Refactor this function to reduce its cyclomatic complexity
  from 12 to below 5 while maintaining all existing tests.
```

❌ **Unfair Validation**
```yaml
validation:
  type: exact_match
  criteria:
    expected_answer: "Paris"  # Case-sensitive, whitespace-sensitive
```

✅ **Fair Validation**
```yaml
validation:
  type: exact_match
  criteria:
    expected_answer: "Paris"
    case_sensitive: false
    trim_whitespace: true
```

❌ **Token Trap**
```yaml
# Requires 5 large context files, all necessary
# Forces users to waste tokens
```

✅ **Efficient Context**
```yaml
# Most files are optional
# Users can strategize which to include
```

## Testing Your Challenges

Before committing a challenge, test it:

1. **Solve it yourself**
   - Try to complete the challenge
   - Record token usage
   - Verify validation works

2. **Test edge cases**
   - What if user provides minimal response?
   - What if user provides excessive response?
   - What if response is almost correct?

3. **Verify metadata**
   - Are token estimates realistic?
   - Is difficulty appropriate?
   - Are tags accurate?

4. **Run validation script**
   ```bash
   python scripts/validate_challenges.py challenges/hole-XXX/
   ```

## Challenge Validation Script

The system should include a script to validate challenge files:

```python
# scripts/validate_challenges.py

def validate_challenge(challenge_path: str) -> List[str]:
    """
    Validate a challenge YAML file.
    
    Returns list of errors (empty if valid).
    """
    errors = []
    
    # Check required fields
    # Validate field types
    # Check file paths exist
    # Verify validation criteria is complete
    # Test with sample solutions
    
    return errors
```

Run before committing:
```bash
python scripts/validate_challenges.py challenges/
```

## Versioning Challenges

When updating a challenge:

1. **Breaking changes** (affects validation logic):
   - Create new challenge with new ID
   - Archive old version
   - Update metadata to reference replacement

2. **Non-breaking changes** (typos, clarifications):
   - Edit challenge in place
   - Update `metadata.modified_date`
   - Document change in commit message

3. **Difficulty adjustment**:
   - Based on actual user data
   - Update `estimated_tokens_*` fields
   - May change `difficulty` classification

## Challenge Repository Guidelines

### File Naming
- Challenge files: `challenge.yaml` (not `challenge.yml`)
- Assets: descriptive names, lowercase, underscores

### Asset Management
- Keep assets small (< 1MB total per challenge)
- Use git LFS for large files if necessary
- Commit assets with challenge definition

### Documentation
- Each challenge should be self-documenting
- Include clear descriptions in YAML
- Add inline comments for complex validation

### Contributions
- Submit challenges via PR to `dev` branch
- Include test results in PR description
- Request review from challenge design team

## Example Challenges by Type

### Coding Challenge
```yaml
id: hole-003
name: "FizzBuzz Implementation"
difficulty: easy
task_type: coding
description: |
  Implement the classic FizzBuzz algorithm.
  Write a function that returns a list of strings for numbers 1 to n:
  - "Fizz" for multiples of 3
  - "Buzz" for multiples of 5
  - "FizzBuzz" for multiples of both
  - The number as a string otherwise
```

### Extraction Challenge
```yaml
id: hole-010
name: "Extract Email Addresses"
difficulty: medium
task_type: extraction
description: |
  Extract all valid email addresses from the provided text file.
  Return them as a JSON array, one email per element.
  Remove duplicates and sort alphabetically.
```

### Question Answering Challenge
```yaml
id: hole-015
name: "Document Q&A"
difficulty: medium
task_type: question_answering
description: |
  Read the provided research paper abstract and answer:
  "What methodology did the researchers use?"
  
  Provide a concise 2-3 sentence answer.
```

### Classification Challenge
```yaml
id: hole-020
name: "Sentiment Analysis"
difficulty: easy
task_type: classification
description: |
  Classify the sentiment of the provided customer reviews.
  Return one of: POSITIVE, NEGATIVE, or NEUTRAL
```

## Future Enhancements

- **Hints system**: Progressive hints that cost tokens
- **Difficulty adaptation**: Challenges adjust based on user performance
- **Community challenges**: User-submitted challenges
- **Challenge variants**: Multiple versions of similar challenges
- **Interactive validation**: Real-time feedback as user types
- **Code execution sandbox**: Safe execution environment
- **Multi-language support**: Challenges in different spoken languages
