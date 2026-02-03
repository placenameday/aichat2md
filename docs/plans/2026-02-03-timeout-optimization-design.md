# Timeout Optimization Design

**Date**: 2026-02-03
**Status**: Approved
**Type**: Bug Fix + UX Enhancement

---

## Problem Statement

### Root Cause Analysis

**Issue 1: Playwright Timeout (30s)**
- **Symptom**: `Timeout 30000ms exceeded` on Gemini share links
- **Root Cause**: Fixed 30s timeout insufficient for slow networks + dynamic rendering
- **Evidence**: Gemini page loaded successfully on retry but failed initially

**Issue 2: API Timeout (60s)**
- **Symptom**: `Read timed out` during DeepSeek API response streaming
- **Root Cause**: Fixed 60s timeout doesn't scale with content size
- **Evidence**: 15K-17K character content consistently exceeds 60s

### User Impact

Long waits without feedback cause:
- Users think tool is frozen
- Manual interruption (Ctrl+C)
- Unnecessary retries
- Poor user experience

---

## Design Goals

1. **Reliability**: Handle slow networks and large content gracefully
2. **Simplicity**: Minimal code changes, zero breaking changes
3. **Transparency**: Clear progress feedback during long operations
4. **Compatibility**: No impact on existing tests or workflows

---

## Solution Overview

**Philosophy**: Conservative strategy - increase timeouts and add progress indicators

### Components

1. **Playwright timeout**: 30s → 60s (covers 95%+ scenarios)
2. **API timeout**: Dynamic calculation based on content size
3. **Progress feedback**: Animated spinner with elapsed time (yaspin)

---

## Technical Design

### 1. Playwright Timeout

**Change**: Increase default and hardcoded timeout to 60s

**Files Modified**:
- `aichat2md/extractors/playwright_extractor.py:43` - Function signature
- `aichat2md/extractors/playwright_extractor.py:73` - goto() call

**Code**:
```python
def extract_from_url(url: str, timeout: int = 60000) -> str:
    # ...
    page.goto(url, wait_until=wait_strategy, timeout=60000)
```

**Rationale**: Network conditions unpredictable, uniform timeout simpler than adaptive strategy

### 2. API Dynamic Timeout

**Formula**:
```python
timeout = min(60 + len(raw_text) // 100, 600)
```

**Examples**:
- 5K chars: 110s
- 15K chars: 210s (fixes current failure)
- 50K chars: 560s
- 100K+ chars: 600s (10-minute cap)

**Files Modified**:
- `aichat2md/structurizer.py:84`

**Code**:
```python
estimated_timeout = min(60 + len(raw_text) // 100, 600)
response = requests.post(api_url, headers=headers, json=payload, timeout=estimated_timeout)
```

**Rationale**: Content size predictably correlates with processing time, dynamic scaling more efficient than fixed high timeout

### 3. Progress Indicator

**Library**: yaspin (lightweight, pipe-safe, actively maintained)

**Files Modified**:
- `pyproject.toml` - Add dependency
- `aichat2md/cli.py` - Wrap long operations

**Dependency**:
```toml
dependencies = [
    "playwright>=1.40.0",
    "requests>=2.31.0",
    "yaspin>=3.0.0",
]
```

**Implementation**:
```python
from yaspin import yaspin

# URL extraction
with yaspin(text=f"Extracting from URL (up to 60s): {input_path}", timer=True) as sp:
    text = extract_from_url(input_path)
    sp.ok(f"✓ Extracted {len(text)} characters")

# API structurization
estimated = min(60 + len(raw_text) // 100, 600)
with yaspin(text=f"Structurizing {len(raw_text)} chars with {provider} (~{estimated}s)", timer=True) as sp:
    markdown = structurize_content(raw_text, config, source)
    sp.ok("✓ Structurized")
```

**User Experience**:
```
⠋ Extracting from URL (up to 60s): https://... [00:23]
✓ Extracted 15697 characters
⠙ Structurizing 15697 chars with https://api.deepseek.com (~216s) [01:48]
✓ Structurized
```

**Features**:
- Animated spinner shows tool is working
- Timer shows elapsed time
- Estimated time sets expectations
- Success checkmark confirms completion
- Pipe-safe (auto-disables in non-TTY)

---

## Implementation Checklist

- [ ] Add yaspin to dependencies in pyproject.toml
- [ ] Update Playwright timeout (2 locations)
- [ ] Add dynamic API timeout calculation
- [ ] Wrap URL extraction with yaspin
- [ ] Wrap API call with yaspin
- [ ] Test with real Gemini URLs (slow network)
- [ ] Test with large content (15K+ chars)
- [ ] Verify tests still pass (yaspin silent in test env)
- [ ] Update CLAUDE.md with new behavior

---

## Testing Strategy

### Manual Tests

1. **Slow network scenario**:
   ```bash
   aichat2md https://gemini.google.com/share/e885d6bca1d6
   ```
   - Expected: Completes within 60s, shows spinner progress

2. **Large content scenario**:
   ```bash
   aichat2md https://gemini.google.com/share/4bdd2bbad3c8
   ```
   - Expected: ~210s timeout, completes successfully

3. **Fast scenario** (baseline):
   ```bash
   aichat2md https://chatgpt.com/share/xxx  # Small conversation
   ```
   - Expected: Completes quickly, minimal spinner time

### Automated Tests

Existing tests should pass without modification:
- yaspin auto-detects non-TTY environment (test runners)
- Silently outputs without spinner in tests
- No test changes needed

---

## Backward Compatibility

✅ **Zero breaking changes**:
- Default behavior improved, not changed
- No API changes
- No config changes
- CLI interface unchanged
- Tests unaffected

✅ **Dependency risk**:
- yaspin: mature, stable, widely used
- Zero transitive dependencies
- Size: ~20KB
- Fallback: works without TTY (CI/CD safe)

---

## Trade-offs

### Accepted

- **New dependency**: yaspin adds ~20KB, acceptable for UX gain
- **Longer waits**: Users wait longer for truly slow operations (but see progress)

### Rejected

- **Retry logic**: Adds complexity, conservative timeouts sufficient
- **Zero dependencies**: Poor UX without progress feedback
- **Progress bar**: Overkill for unpredictable operations

---

## Future Enhancements

Not in scope, consider later:
- Streaming API support (token-by-token progress)
- Parallel processing for batch mode
- Configurable timeout multipliers
- Network speed detection

---

## Success Metrics

- ✅ Gemini 15K-char conversations complete successfully
- ✅ Users see progress during long operations
- ✅ No false timeout failures on slow networks
- ✅ Existing functionality unaffected
