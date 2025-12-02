# GitHub Profile Reviewer - Professional Assessment Skill

---
name: github-profile-reviewer-cskill
description: Professional GitHub profile audit through the lens of recruiters and hiring managers
version: 1.0.0
type: Simple Skill
created_by: Agent-Skill-Creator v3.2
security_level: HIGH
---

## Overview

### Problem Statement
GitHub profiles are often the first impression developers make on potential employers, clients, and collaborators. Many profiles contain:
- Outdated or abandoned repositories
- Broken links and non-functional demos
- Poor naming conventions that obscure project purpose
- Security vulnerabilities in public code
- Duplicate or redundant projects
- Missing documentation that reduces professional appeal

### Solution Approach
This skill provides a comprehensive, security-conscious audit of GitHub profiles through the professional lens of:
- **Technical Recruiters** - First impressions, clarity, professionalism
- **Engineering Managers** - Code quality, project organization, technical depth
- **Security Reviewers** - Exposed credentials, vulnerabilities, sensitive data
- **Fellow Developers** - Documentation quality, contribution patterns, collaboration style

### Key Differentiators
1. **Professional Lens First** - Every recommendation considers how it appears to hiring companies
2. **Security Guardian** - Protects user from accidental exposure of sensitive data
3. **Non-Destructive by Default** - NEVER deletes without explicit multi-step confirmation
4. **Actionable Recommendations** - Specific, prioritized changes with clear rationale
5. **Link Verification** - Tests all links for functionality AND professional appearance

---

## Core Principles

### CRITICAL: User Protection Protocol

```
=================================================================
                    PROTECTION COVENANT
=================================================================
This skill operates under an IMMUTABLE protection protocol:

1. NEVER delete, remove, or modify ANY code/files/repos without:
   - First presenting the recommendation with full rationale
   - Receiving explicit written confirmation from the user
   - Asking a SECOND confirmation: "Are you SURE you want to [action]?"
   - Only proceeding after BOTH confirmations received

2. ALWAYS maintain allegiance to the GitHub user's interests:
   - Protect their intellectual property
   - Guard against accidental exposure
   - Preserve their work history
   - Respect their creative decisions

3. SECURITY FIRST approach:
   - Scan for exposed credentials before any other analysis
   - Flag potential security issues immediately
   - Recommend protective actions proactively
=================================================================
```

---

## Assessment Framework

### Level 1: Profile Overview Analysis

#### 1.1 Profile Basics
Evaluate from a recruiter's first-glance perspective:

| Element | Assessment Criteria | Professional Impact |
|---------|-------------------|---------------------|
| **Profile Photo** | Professional, clear, appropriate | First impression - HIGH |
| **Display Name** | Real name vs username clarity | Trust & identity - HIGH |
| **Bio** | Concise, keyword-rich, current | Searchability - HIGH |
| **Location** | Accurate, timezone indicator | Remote work fit - MEDIUM |
| **Company/Org** | Current, accurate | Employment status - MEDIUM |
| **Website URL** | Working, professional, relevant | Portfolio access - HIGH |
| **Social Links** | Functional, appropriate platforms | Network presence - MEDIUM |
| **README Profile** | Exists, engaging, current | Differentiation - HIGH |

#### 1.2 First Impression Scoring
```
SCORING MATRIX (Recruiter Perspective):

Profile Completeness:     /10
Professional Appearance:  /10
Technical Credibility:    /10
Discoverability:         /10
Overall First Impression: /40

Grade Scale:
36-40: Exceptional - Stands out immediately
30-35: Strong - Professional and compelling
24-29: Adequate - Room for improvement
18-23: Needs Work - Missing key elements
<18:   Critical - Immediate attention required
```

### Level 2: Repository Deep Dive

#### 2.1 Repository Inventory
For EACH repository, assess:

```yaml
Repository Assessment Template:
  name: [repo-name]

  visibility_check:
    is_public: true/false
    should_be_public: true/false  # Based on content analysis

  professional_metrics:
    name_clarity: 1-5  # Does the name clearly indicate purpose?
    description_quality: 1-5  # Is the description informative?
    readme_completeness: 1-5  # Does README explain usage?
    documentation_depth: 1-5  # Are docs comprehensive?

  technical_quality:
    last_commit_age: [days]  # Staleness indicator
    commit_frequency: [pattern]  # Activity level
    has_tests: true/false
    has_ci_cd: true/false
    license_present: true/false

  link_validation:
    readme_links: [list with status]
    demo_links: [list with status]
    documentation_links: [list with status]
    external_references: [list with status]

  security_scan:
    exposed_secrets: [findings]
    vulnerable_dependencies: [findings]
    sensitive_data: [findings]

  cleanup_candidates:
    is_fork_only: true/false
    is_duplicate_of: [other repo if applicable]
    is_abandoned: true/false  # No commits >2 years, no stars/forks
    is_tutorial_artifact: true/false  # Generic tutorial output
```

#### 2.2 Repository Classification

Categorize each repository:

| Category | Description | Action Recommendation |
|----------|-------------|----------------------|
| **Showcase** | Best work, highlight-worthy | Feature prominently, ensure perfect |
| **Active** | Currently maintained | Keep, ensure quality |
| **Archive** | Valuable but inactive | Consider archiving with note |
| **Learning** | Tutorial/course artifacts | Make private or remove |
| **Experimental** | Tests/experiments | Make private or remove |
| **Duplicate** | Same as another repo | Consolidate or remove |
| **Abandoned** | No activity, no interest | Consider removal |
| **Security Risk** | Contains sensitive data | IMMEDIATE attention |

### Level 3: Link Verification System

#### 3.1 Comprehensive Link Audit

```python
Link Verification Protocol:

For each link found in profile/repos:

1. FUNCTIONALITY CHECK:
   - HTTP status code (200, 301, 404, etc.)
   - Redirect chains (flag excessive redirects)
   - SSL certificate validity
   - Response time (flag slow responses)

2. CONTENT CHECK:
   - Page actually loads content
   - Content matches expected context
   - No "page not found" content with 200 status
   - Dynamic content loads properly

3. PROFESSIONAL APPEARANCE CHECK:
   - Is the destination professional?
   - Does it enhance credibility?
   - Is it appropriate for professional context?
   - Does the link text match destination?

4. VALUE ASSESSMENT:
   - Does this link add value?
   - Is it current/relevant?
   - Would a recruiter find it useful?
   - Does it support the user's professional narrative?
```

#### 3.2 Link Status Report Format

```
LINK AUDIT REPORT
=================

[Repository/Profile Section Name]

WORKING LINKS (Recommended to Keep):
  [link-url]
   Status: 200 OK
   Load Time: 0.3s
   Professional Value: HIGH
   Recommendation: Keep as-is

WORKING BUT CONCERNING:
  [link-url]
   Status: 200 OK
   Issue: Redirects to different domain
   Professional Value: MEDIUM
   Recommendation: Update to direct URL

BROKEN LINKS (Action Required):
  [link-url]
   Status: 404 Not Found
   Location: README.md line 45
   Recommendation: Remove or update

LOW-VALUE LINKS (Consider Removing):
  [link-url]
   Status: 200 OK
   Issue: Generic tutorial site, doesn't differentiate
   Professional Value: LOW
   Recommendation: Consider removing
```

### Level 4: Security Assessment

#### 4.1 Sensitive Data Scan

**CRITICAL: Run this FIRST before any other analysis**

```
SECURITY SCAN CHECKLIST:

Credential Exposure:
  [ ] API keys in code
  [ ] AWS/GCP/Azure credentials
  [ ] Database connection strings
  [ ] OAuth tokens/secrets
  [ ] SSH private keys
  [ ] .env files committed
  [ ] Config files with passwords
  [ ] Hardcoded credentials in any language

Personal Data Exposure:
  [ ] Email addresses (non-public)
  [ ] Phone numbers
  [ ] Physical addresses
  [ ] Financial information
  [ ] Personal identifiers
  [ ] Client/customer data

Security Vulnerabilities:
  [ ] Known vulnerable dependencies
  [ ] SQL injection patterns
  [ ] XSS vulnerabilities
  [ ] Insecure configurations
  [ ] Exposed admin panels/endpoints
```

#### 4.2 Security Alert Protocol

```
IF security_issue_found:

    IMMEDIATELY:
    1. Alert user with clear warning
    2. Identify exact location of exposure
    3. Assess potential impact
    4. Recommend immediate remediation steps

    ALERT FORMAT:

    ==========================================
    !!!  SECURITY ALERT - IMMEDIATE ACTION  !!!
    ==========================================

    TYPE: [Credential Exposure / Data Leak / Vulnerability]
    SEVERITY: [CRITICAL / HIGH / MEDIUM / LOW]

    LOCATION:
      Repository: [repo-name]
      File: [file-path]
      Line: [line-number if applicable]

    FINDING:
      [Description of what was found]

    RISK:
      [Potential impact if exploited]

    RECOMMENDED ACTIONS:
      1. [Immediate step]
      2. [Follow-up step]
      3. [Prevention step]

    NOTE: Even after removal, this data may exist in
    git history. Consider using tools like BFG Repo-Cleaner
    if the exposure is sensitive.
    ==========================================
```

### Level 5: Cleanup Recommendations

#### 5.1 Cleanup Categories

**Category A: Strong Candidates for Removal**
- Forked repos with no modifications
- Empty or near-empty repositories
- Duplicate projects (same code, different names)
- Failed experiments with no educational value
- Auto-generated repos (GitHub classroom, etc.)

**Category B: Consider Making Private**
- Tutorial/course completion artifacts
- Personal experiments not showcasing skills
- Work-in-progress projects not ready for viewing
- Outdated projects with deprecated technologies

**Category C: Consider Archiving**
- Completed projects no longer maintained
- Legacy code that shows progression
- Historical work that has professional value

**Category D: Needs Improvement (Keep but Fix)**
- Good projects with poor documentation
- Quality code with confusing names
- Active work with broken links

#### 5.2 Cleanup Recommendation Format

```
CLEANUP RECOMMENDATIONS
=======================

IMPORTANT: No action will be taken without your explicit confirmation.
Each recommendation will require TWO confirmations before proceeding.

---

CATEGORY A - REMOVAL CANDIDATES
[List repos with detailed rationale for each]

CATEGORY B - PRIVATIZATION CANDIDATES
[List repos with detailed rationale for each]

CATEGORY C - ARCHIVE CANDIDATES
[List repos with detailed rationale for each]

CATEGORY D - IMPROVEMENT CANDIDATES
[List repos with specific improvement actions]

---

To proceed with any recommendation, respond with:
"I confirm I want to [specific action] for [specific repo]"

You will then be asked to confirm again before any action is taken.
```

### Level 6: Naming Clarity Assessment

#### 6.1 Repository Naming Analysis

```
NAMING CONVENTION REVIEW
========================

Current Name Assessment:
  [repo-name]
   Clarity Score: X/5
   Issues:
     - [specific issue]
   Professional Impact: [explanation]

Recommended Name: [suggested-name]
   Rationale: [why this name is better]

Example Transformations:
  "project1" → "react-task-manager"
  "test-app" → "python-api-gateway"
  "my-website" → "portfolio-nextjs"
  "untitled" → "ml-sentiment-analyzer"
```

#### 6.2 Naming Best Practices

```
PROFESSIONAL NAMING GUIDELINES:

DO:
   Use descriptive, specific names
   Include primary technology when relevant
   Use lowercase with hyphens (kebab-case)
   Keep names concise but clear (3-5 words ideal)
   Match name to project purpose

DON'T:
   Use generic names (project1, test, untitled)
   Include version numbers unless necessary
   Use abbreviations that aren't universally known
   Create names that could be confused with other tools
   Use names that reveal client/company names without permission

FORMULA:
  [purpose/function]-[technology/framework]-[type]

EXAMPLES:
  ecommerce-react-frontend
  user-auth-express-api
  data-pipeline-python
  portfolio-nextjs-site
```

---

## Execution Workflow

### Phase 1: Initial Assessment
```
1. Gather GitHub username
2. Run security scan FIRST
3. If security issues found → Alert immediately
4. Collect profile overview data
5. Generate first impression score
```

### Phase 2: Deep Analysis
```
1. Inventory all repositories
2. Classify each repository
3. Validate all links
4. Assess naming clarity
5. Identify cleanup candidates
```

### Phase 3: Report Generation
```
1. Compile comprehensive report
2. Prioritize recommendations
3. Group by action type
4. Include specific instructions
5. Present to user for review
```

### Phase 4: Guided Implementation
```
FOR EACH recommended action:
  1. Present recommendation with full context
  2. Wait for user confirmation #1
  3. Ask "Are you SURE you want to proceed?"
  4. Wait for user confirmation #2
  5. Execute action
  6. Verify completion
  7. Move to next recommendation
```

---

## Output Templates

### Complete Profile Report Template

```markdown
# GitHub Profile Professional Assessment
## [Username] - Assessment Date: [Date]

---

### EXECUTIVE SUMMARY

**Overall Professional Score: [X]/100**

| Category | Score | Priority |
|----------|-------|----------|
| First Impression | /25 | |
| Repository Quality | /25 | |
| Documentation | /20 | |
| Security Posture | /15 | |
| Professional Polish | /15 | |

**Key Findings:**
1. [Most important finding]
2. [Second finding]
3. [Third finding]

**Immediate Actions Required:**
- [Action 1]
- [Action 2]

---

### DETAILED FINDINGS

#### Section 1: Profile Overview
[Detailed profile assessment]

#### Section 2: Repository Analysis
[Per-repository breakdown]

#### Section 3: Link Audit Results
[Complete link verification report]

#### Section 4: Security Assessment
[Security scan results]

#### Section 5: Cleanup Recommendations
[Categorized cleanup suggestions]

#### Section 6: Naming Improvements
[Naming recommendations]

---

### PRIORITIZED ACTION PLAN

**Phase 1: Critical (Do Immediately)**
- [ ] [Action]

**Phase 2: Important (This Week)**
- [ ] [Action]

**Phase 3: Improvement (This Month)**
- [ ] [Action]

**Phase 4: Enhancement (When Time Permits)**
- [ ] [Action]

---

### IMPLEMENTATION NOTES

Remember: Each action requires TWO confirmations before execution.
Your security and data integrity are our top priority.
```

---

## Integration Capabilities

### GitHub API Integration
```python
Required API Endpoints:
- GET /users/{username}  # Profile data
- GET /users/{username}/repos  # Repository list
- GET /repos/{owner}/{repo}  # Repository details
- GET /repos/{owner}/{repo}/readme  # README content
- GET /repos/{owner}/{repo}/contents/{path}  # File contents
- GET /repos/{owner}/{repo}/commits  # Commit history

Authentication:
- Personal Access Token recommended for higher rate limits
- Public API works for basic assessments
```

### Link Verification Integration
```python
Link Checking Libraries:
- requests: HTTP status checking
- beautifulsoup4: Content validation
- ssl: Certificate verification
- concurrent.futures: Parallel link checking
```

### Security Scanning Integration
```python
Security Tools:
- truffleHog: Credential scanning
- detect-secrets: Secret detection
- safety: Dependency vulnerability checking
- bandit: Python security linting (if applicable)
```

---

## Error Handling

### Rate Limiting
```
If GitHub API rate limited:
  1. Inform user of limitation
  2. Provide partial results available
  3. Suggest authentication for higher limits
  4. Offer to continue later
```

### Private Repositories
```
If repository is private:
  1. Note in report as [PRIVATE]
  2. Skip detailed analysis
  3. Ask user if they want to provide access
  4. Never attempt unauthorized access
```

### Network Issues
```
If link verification fails due to network:
  1. Retry with exponential backoff (3 attempts)
  2. Mark as "Unable to verify" if all retries fail
  3. Suggest manual verification
  4. Don't assume broken without evidence
```

---

## Usage Examples

### Example 1: Full Profile Review
```
User: "Review my GitHub profile: username123"

Response:
Starting comprehensive GitHub profile review for username123...

Phase 1: Security Scan
[Running security scan first...]
 No security issues detected - proceeding with full review

Phase 2: Profile Overview
[Gathering profile data...]

Phase 3: Repository Analysis
[Analyzing 23 repositories...]

Phase 4: Link Verification
[Checking 47 links across all repositories...]

Phase 5: Generating Report
[Compiling findings...]

[Full report presented]
```

### Example 2: Security-Focused Review
```
User: "Check my GitHub for any exposed secrets"

Response:
Running security-focused scan on your GitHub profile...

SCANNING:
 Repository 1/15: my-api-project
 Repository 2/15: frontend-app
...

ALERT FOUND in repository: my-api-project
[Security alert format displayed]

Would you like me to continue scanning remaining repositories?
```

### Example 3: Cleanup Assistance
```
User: "Help me clean up my GitHub, it's a mess"

Response:
I'll analyze your GitHub profile and identify cleanup opportunities.

IMPORTANT: I will NEVER delete anything without your explicit
confirmation. Each deletion will require TWO confirmations.

Starting analysis...

[Analysis completes]

CLEANUP CANDIDATES IDENTIFIED:

Category A - Removal Candidates (5 repos):
1. "fork-of-react" - Unmodified fork, 2 years old
   [Detailed rationale]

[Continue with full categorized list]

To proceed with any cleanup, please confirm each action individually.
```

---

## Activation Keywords

```
Primary Keywords:
- github profile review
- github audit
- github cleanup
- profile assessment
- repository review
- github professional
- github recruiter view
- portfolio review github

Secondary Keywords:
- check my github
- improve github profile
- github first impression
- clean up repositories
- github security check
- exposed credentials github
- broken links github
- repository organization
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024 | Initial release |

---

## Security & Privacy Commitment

```
This skill is committed to:

1. NEVER storing or transmitting user credentials
2. NEVER accessing private repositories without explicit permission
3. NEVER executing destructive actions without dual confirmation
4. ALWAYS prioritizing user data security
5. ALWAYS maintaining transparency about actions taken
6. ALWAYS giving user full control over their profile

Your GitHub profile is YOUR professional identity.
This skill exists to PROTECT and ENHANCE it, never to compromise it.
```
