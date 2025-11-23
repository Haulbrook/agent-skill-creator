# Personalized Job Search Agent 🎯

Your AI-powered personal recruitment service that searches, compares, analyzes, and applies for jobs 24/7 based on your unique profile and preferences.

## What It Does

This intelligent agent automates your entire job search workflow:

### 🔍 **Intelligent Job Discovery**
- Searches multiple job boards simultaneously (LinkedIn, Indeed, Glassdoor, etc.)
- Filters based on your specific criteria
- Daily automated searches for new opportunities
- Smart deduplication across platforms

### 🎯 **AI-Powered Job Matching**
- Scores each job 0-100 based on your profile
- Weighted algorithm considering:
  - Skills match (35%)
  - Salary alignment (25%)
  - Location preference (15%)
  - Company fit (10%)
  - Benefits (10%)
  - Culture fit (5%)

### 📊 **Job Comparison & Analysis**
- Side-by-side comparison of opportunities
- Pros/cons analysis for each position
- Salary benchmarking
- Company research and reviews
- Career growth assessment

### 🤖 **Application Automation**
- Auto-fill applications with your profile
- Generate customized cover letters
- Track application status
- Interview scheduling assistance

### 💡 **Career Insights**
- Market trends for your field
- Skill gap analysis
- Salary negotiation strategies
- Career path recommendations

## Quick Start

### Installation

```bash
# 1. Install the agent in Claude Code
/plugin marketplace add ./personalized-job-search-agent-cskill

# 2. Install dependencies
cd personalized-job-search-agent-cskill
pip install -r requirements.txt

# 3. Setup API keys (optional, for full functionality)
cp .env.example .env
# Edit .env with your API keys
```

### First-Time Setup

```
User: "Create my job search profile. I'm a senior software engineer with 8 years
of experience in Python, JavaScript, and AWS. I'm looking for remote senior or
staff engineer roles paying $150k-$200k at fintech or healthtech startups."

Agent: ✅ Profile Created!
```

### Search for Jobs

```
User: "Find me jobs that match my profile"

Agent: 🔍 Found 147 jobs matching your criteria!

Top 5 Matches:
1. ⭐⭐⭐⭐⭐ Staff Software Engineer @ HealthTech Startup (95% match)
   💰 $160k-$190k | 📍 Remote
```

### Analyze Opportunities

```
User: "Analyze the first job in detail"

Agent: 📊 Detailed Analysis: Staff Software Engineer

🎯 Match Score: 95/100 (Excellent Match)
✅ Skills Match: 98/100 (10/10 required skills)
💰 Salary Match: 95/100 ($160k-$190k vs your $150k-$200k range)
...
```

### Apply for Jobs

```
User: "Apply for this job"

Agent: 📝 Preparing application...
✅ Cover letter generated
✅ Resume tailored
Ready to submit?
```

## Features

### Profile Management
- Store skills, experience, education, certifications
- Define salary range, location, remote/hybrid preferences
- Set career goals and job criteria
- Import from resume (AI-powered extraction)

### Multi-Platform Search
Supported job boards:
- ✅ LinkedIn Jobs
- ✅ Indeed
- ✅ Glassdoor
- ✅ ZipRecruiter
- ✅ Monster
- ✅ CareerBuilder
- ✅ Dice (tech roles)
- ✅ GitHub Jobs
- ✅ Stack Overflow Jobs

### Intelligent Matching
- **Skills Analysis**: Match required vs your skills, identify gaps
- **Salary Analysis**: Compare offers with market rates
- **Location Scoring**: Remote, hybrid, onsite preferences
- **Company Fit**: Size, industry, culture, growth
- **Benefits Comparison**: Prioritize what matters to you

### Application Tracking
- Track all applications in one place
- Status updates: Applied → Under Review → Interview → Offer
- Interview scheduling and preparation
- Offer comparison and negotiation tools

## Usage Examples

### Create Profile

```python
{
  "professional": {
    "current_role": "Senior Software Engineer",
    "experience_years": 8,
    "skills": [
      {"name": "Python", "years": 8, "proficiency": "expert"},
      {"name": "JavaScript", "years": 6, "proficiency": "advanced"}
    ]
  },
  "preferences": {
    "desired_roles": ["Staff Engineer", "Senior Engineer"],
    "salary_min": 150000,
    "salary_max": 200000,
    "locations": ["remote"],
    "industries": ["fintech", "healthtech"]
  }
}
```

### Search with Filters

```
"Find remote Python jobs paying 150k+ at startups"
"Search for senior engineering roles in San Francisco"
"What are the best jobs for my skills in fintech?"
```

### Compare Offers

```
"Compare these three job offers"
"Which position has better career growth potential?"
"Show me salary vs benefits tradeoffs"
```

### Track Applications

```
"Show my application status"
"What jobs have I applied to this week?"
"Any updates on my applications?"
```

## Configuration

### API Keys (Optional)

For full functionality, configure these APIs:

```bash
# .env file
LINKEDIN_API_KEY=your_key_here          # LinkedIn job search
INDEED_PUBLISHER_ID=your_id_here        # Indeed job search
ANTHROPIC_API_KEY=your_key_here         # AI cover letters
GLASSDOOR_API_KEY=your_key_here         # Company reviews
```

Free tiers available for all services!

### Matching Weights

Customize scoring weights in `assets/preferences.json`:

```json
{
  "matching_algorithm": {
    "skills_weight": 0.35,
    "salary_weight": 0.25,
    "location_weight": 0.15,
    "company_weight": 0.10,
    "benefits_weight": 0.10,
    "culture_weight": 0.05
  }
}
```

## File Structure

```
personalized-job-search-agent-cskill/
├── scripts/
│   ├── main.py                    # Main orchestration
│   ├── search/                    # Job search modules
│   │   └── unified_search.py      # Multi-platform search
│   ├── analysis/                  # Analysis and scoring
│   │   ├── job_scorer.py          # Matching algorithm
│   │   └── comparison_engine.py   # Job comparison
│   ├── application/               # Application automation
│   │   ├── cover_letter_gen.py    # Cover letter generation
│   │   └── application_tracker.py # Application management
│   └── storage/                   # Data management
│       ├── profile_manager.py     # Profile storage
│       ├── job_database.py        # Job storage
│       └── application_db.py      # Application tracking
├── assets/                        # Data storage
│   ├── user_profile.json          # Your profile
│   ├── jobs_database.json         # Discovered jobs
│   └── applications.json          # Application tracking
├── references/                    # Documentation
├── SKILL.md                       # Skill definition
└── README.md                      # This file
```

## Advanced Features

### Skill Gap Analysis

```
"What skills am I missing for senior ML engineer roles?"

→ Analyzes 50+ job postings
→ Identifies most common requirements
→ Recommends learning priorities
→ Estimates impact on match rate
```

### Salary Negotiation

```
"Should I negotiate this $160k offer?"

→ Compares with market data
→ Provides negotiation strategy
→ Suggests alternative benefits
→ Drafts negotiation email
```

### Auto-Application

```
"Auto-apply to all jobs with 90%+ match, but ask me first"

→ Finds high-match jobs
→ Generates custom cover letters
→ Prepares applications
→ Asks for approval before submitting
```

## Privacy & Security

✅ **Local-First**: All personal data stored locally
✅ **Encrypted**: Sensitive data encrypted at rest
✅ **No Sharing**: Your profile never shared without permission
✅ **Secure APIs**: Credentials stored in environment variables
✅ **Consent-Based**: Application automation requires explicit approval

## Cost Estimates

### Free Tier (Recommended to Start)
- Indeed API: 1000 queries/month
- JSearch API: 100 searches/month
- Anthropic Claude: $5/month typical usage
- **Total: ~$5-10/month**

### Paid Tier (Heavy Users)
- LinkedIn API: $50/month
- Multiple job boards: $30/month
- AI generation: $20/month
- **Total: ~$100/month**

## Troubleshooting

### No jobs found
- Broaden search criteria
- Check API keys are configured
- Verify profile is complete

### Low match scores
- Update skills in profile
- Review skill gap analysis
- Adjust salary expectations

### Application fails
- Some sites block automation
- Use manual application for those
- Check Selenium/Chrome setup

## Future Enhancements

🚀 **Coming Soon**:
- [ ] Interview scheduling automation
- [ ] Video interview practice
- [ ] Portfolio generation
- [ ] LinkedIn profile optimization
- [ ] Networking recommendations
- [ ] Referral request automation
- [ ] Job market trend predictions

## Support

Need help?
- See `references/USER_GUIDE.md` for detailed manual
- See `references/API_SETUP.md` for API configuration
- See `references/TROUBLESHOOTING.md` for common issues

## License

Apache 2.0

---

**Remember**: This agent is a tool to augment your job search, not replace your judgment. Always review opportunities carefully and trust your instincts about what's right for your career.

Happy job hunting! 🎯
