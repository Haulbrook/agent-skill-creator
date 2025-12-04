# Release Checkpoint Template

## Release Information
- **Version**: [X.Y.Z]
- **Release Name**: [Optional Name]
- **Date**: [YYYY-MM-DD]
- **Release Manager**: [Name]

---

## Pre-Release Verification

### Code Quality Gate
| Metric | Required | Actual | Status |
|--------|----------|--------|--------|
| Reasoning Score | >= 85 | __ | [ ] |
| Test Coverage | >= 80% | __% | [ ] |
| Code Review | Approved | __ | [ ] |
| Security Scan | Pass | __ | [ ] |
| Performance | Acceptable | __ | [ ] |

### Documentation Gate
- [ ] README is current
- [ ] API documentation updated
- [ ] Changelog updated
- [ ] Migration guide (if needed)
- [ ] Release notes prepared

### Testing Gate
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Manual testing complete
- [ ] Regression testing complete
- [ ] Performance testing complete

---

## Reasoning Assessment

### Phase-by-Phase Final Scores

#### Phase 1: Comprehension [__/20]
- Requirements fully documented: [Yes/No]
- Code purpose is clear: [Yes/No]
- I/O specifications complete: [Yes/No]

#### Phase 2: Strategy [__/20]
- Approach is documented: [Yes/No]
- Design decisions recorded: [Yes/No]
- Architecture is sound: [Yes/No]

#### Phase 3: Execution [__/20]
- Code follows plan: [Yes/No]
- Implementation is clean: [Yes/No]
- Steps are documented: [Yes/No]

#### Phase 4: Review [__/20]
- All edge cases handled: [Yes/No]
- Error handling complete: [Yes/No]
- Security reviewed: [Yes/No]

#### Phase 5: Refinement [__/20]
- No TODOs remaining: [Yes/No]
- Code is optimized: [Yes/No]
- Polish is complete: [Yes/No]

### Final Score: __/100 (Grade: __)

---

## Release Checklist

### Build Verification
- [ ] Build succeeds
- [ ] No build warnings
- [ ] Dependencies are locked
- [ ] Version numbers updated

### Deployment Preparation
- [ ] Deployment scripts ready
- [ ] Environment configs verified
- [ ] Rollback plan exists
- [ ] Monitoring configured

### Communication
- [ ] Stakeholders notified
- [ ] Release notes distributed
- [ ] Support team briefed
- [ ] External communication prepared

---

## Risk Assessment

### Known Issues
| Issue | Severity | Mitigation | Accept Risk? |
|-------|----------|------------|--------------|
| [Issue 1] | [H/M/L] | [Mitigation] | [ ] |
| [Issue 2] | [H/M/L] | [Mitigation] | [ ] |

### Rollback Triggers
- [Condition 1 that would trigger rollback]
- [Condition 2 that would trigger rollback]

---

## Final Approval

### Sign-off Requirements

| Role | Name | Approved | Date |
|------|------|----------|------|
| Developer | [Name] | [ ] | |
| Reviewer | [Name] | [ ] | |
| QA | [Name] | [ ] | |
| Release Manager | [Name] | [ ] | |

### Release Decision

- [ ] **APPROVED** - Proceed with release
- [ ] **CONDITIONAL** - Release with noted exceptions
- [ ] **REJECTED** - Do not release

### Conditions/Notes
[Any conditions or notes for conditional approval]

---

## Post-Release

### Verification Steps
1. [ ] Deployment successful
2. [ ] Smoke tests passing
3. [ ] Monitoring shows healthy metrics
4. [ ] No critical alerts

### Rollback Status
- **Rollback Required**: [Yes/No]
- **Rollback Executed**: [N/A / DateTime]
- **Rollback Reason**: [N/A / Reason]

---

**Release Timestamp**: [DateTime]
**Verified By**: [Name/System]
