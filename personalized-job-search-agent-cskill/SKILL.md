---
name: personalized-job-search-agent
description: Your personal AI-powered job search assistant that searches, compares, analyzes, and applies for jobs based on your unique profile and preferences. Like having a dedicated recruitment agency working 24/7 just for you.
---

# Personalized Job Search Agent

## Overview

This intelligent agent acts as your personal recruitment service, automating the entire job search process from discovery to application. It learns your preferences, searches multiple job boards, scores opportunities based on your criteria, and can even apply for positions on your behalf.

## What This Agent Does

### 🎯 Core Capabilities

**1. Profile Management**
- Create and manage your comprehensive professional profile
- Store skills, experience, education, certifications
- Define preferences: salary range, location, remote/hybrid/onsite
- Set career goals and job criteria

**2. Intelligent Job Search**
- Search across multiple job boards simultaneously (LinkedIn, Indeed, Glassdoor, etc.)
- Filter by your specific criteria
- Find jobs you might have missed
- Daily automated searches for new opportunities

**3. AI-Powered Job Matching**
- Score each job based on your profile (0-100 match score)
- Weighted scoring algorithm considering:
  - Skills match (35%)
  - Salary alignment (25%)
  - Location preference (15%)
  - Company reputation (10%)
  - Benefits package (10%)
  - Culture fit (5%)

**4. Job Comparison & Analysis**
- Side-by-side comparison of multiple opportunities
- Pros/cons analysis for each position
- Salary benchmarking and negotiation insights
- Company research and reviews
- Career growth potential assessment

**5. Application Automation**
- Auto-fill applications with your profile data
- Generate customized cover letters for each position
- Track application status across all submissions
- Set up alerts for application updates
- Schedule interviews automatically

**6. Career Insights**
- Market trends for your field
- Skill gap analysis
- Salary expectations vs reality
- Career path recommendations
- Interview preparation tips

## When To Use This Skill

This skill activates when you want to:

✅ **Search for jobs**
- "Find me software engineering jobs in San Francisco"
- "Search for remote data scientist positions"
- "What are the best jobs for my skills?"

✅ **Setup your profile**
- "Create my job search profile"
- "Update my skills and preferences"
- "Here's my resume, extract my information"

✅ **Compare opportunities**
- "Compare these three job offers"
- "Which of these positions is the best fit for me?"
- "Analyze this job description"

✅ **Apply for jobs**
- "Apply for this position"
- "Submit applications to all matching jobs"
- "Generate a cover letter for this role"

✅ **Track applications**
- "Show my application status"
- "What jobs have I applied to?"
- "Any updates on my applications?"

## How It Works

### Phase 1: Profile Setup

The agent first needs to understand YOU. This includes:

**Professional Information**
```
- Current role and experience level
- Skills (technical and soft skills)
- Education and certifications
- Previous job titles and companies
- Years of experience per skill
- Notable achievements
```

**Preferences**
```
- Desired job titles/roles
- Preferred industries
- Location preferences (cities, remote, hybrid)
- Salary range (minimum, desired, maximum)
- Company size preference (startup, mid-size, enterprise)
- Benefits priorities (health insurance, 401k, stock options, etc.)
- Work-life balance priorities
- Career goals (short-term and long-term)
```

**Deal-Breakers**
```
- Must-have requirements
- Absolute no-gos
- Non-negotiables
```

### Phase 2: Job Discovery

The agent searches multiple platforms:

**Supported Job Boards**
- LinkedIn Jobs
- Indeed
- Glassdoor
- ZipRecruiter
- Monster
- CareerBuilder
- Dice (for tech roles)
- GitHub Jobs
- Stack Overflow Jobs
- Company career pages

**Search Strategy**
1. Uses your profile to create targeted search queries
2. Applies filters based on your preferences
3. Retrieves 50-100 jobs per platform per search
4. Removes duplicates across platforms
5. Filters out jobs you've already seen/applied to

### Phase 3: Job Scoring & Ranking

Each job is analyzed and scored:

**Scoring Algorithm**
```python
total_score = (
    skills_match_score * 0.35 +      # How many of your skills match
    salary_score * 0.25 +             # Salary vs your expectations
    location_score * 0.15 +           # Location preference match
    company_score * 0.10 +            # Company reputation/size
    benefits_score * 0.10 +           # Benefits package quality
    culture_score * 0.05              # Culture fit indicators
)
```

**Match Categories**
- 90-100: Excellent Match ⭐⭐⭐⭐⭐
- 75-89: Great Match ⭐⭐⭐⭐
- 60-74: Good Match ⭐⭐⭐
- 45-59: Decent Match ⭐⭐
- Below 45: Poor Match ⭐

### Phase 4: Job Analysis

For each high-scoring job, the agent provides:

**Detailed Analysis**
- Match score breakdown
- Required skills vs your skills
- Skills you're missing (gap analysis)
- Salary comparison with market rates
- Company insights (funding, growth, culture, reviews)
- Similar roles at the company
- Career progression opportunities
- Commute/remote work analysis
- Benefits comparison

### Phase 5: Application

When you're ready to apply:

**Automated Application Process**
1. Extracts application requirements
2. Fills forms with your profile data
3. Generates customized cover letter
4. Attaches resume (can tailor to job)
5. Submits application
6. Saves confirmation/tracking number
7. Sets up status monitoring

**Smart Cover Letter Generation**
- Personalized for each job
- Highlights relevant experience
- Addresses specific requirements
- Professional tone matching company culture
- Mentions why you're interested in THIS company

### Phase 6: Tracking & Follow-up

**Application Tracking System**
- Status: Applied, Under Review, Interview Scheduled, Rejected, Offer
- Timeline visualization
- Follow-up reminders
- Interview preparation notes
- Offer comparison tools

## Usage Examples

### Example 1: Initial Setup

```
User: "I want to set up my job search profile. I'm a senior software engineer
with 8 years of experience in Python, JavaScript, AWS, and Docker. I'm looking
for remote senior or staff engineer roles paying $150k-$200k. I prefer startups
or mid-size companies in the fintech or healthtech space. Work-life balance is
important to me."

Agent: ✅ Profile Created!

📋 Profile Summary:
   • Role: Senior Software Engineer
   • Experience: 8 years
   • Skills: Python, JavaScript, AWS, Docker
   • Desired Roles: Senior Engineer, Staff Engineer
   • Salary Range: $150k-$200k
   • Location: Remote
   • Industries: Fintech, Healthtech
   • Company Size: Startup, Mid-size
   • Priority: Work-life balance

Your profile has been saved. Ready to start searching for jobs?
```

### Example 2: Job Search

```
User: "Find me jobs that match my profile"

Agent: 🔍 Searching across 8 job boards...

Found 147 jobs matching your criteria!

Top 5 Matches:

1. ⭐⭐⭐⭐⭐ Staff Software Engineer @ HealthTech Startup (95% match)
   💰 $160k-$190k | 📍 Remote | 🏢 Series B Startup
   ✅ 100% skills match | Great work-life balance reviews
   🔗 View Details | 📝 Apply

2. ⭐⭐⭐⭐⭐ Senior Backend Engineer @ Fintech Scale-up (92% match)
   💰 $155k-$185k | 📍 Remote | 🏢 Mid-size (200 employees)
   ✅ 95% skills match | Strong engineering culture
   🔗 View Details | 📝 Apply

3. ⭐⭐⭐⭐ Senior Full-Stack Engineer @ Digital Bank (88% match)
   💰 $150k-$175k | 📍 Remote (US) | 🏢 Well-funded startup
   ✅ 90% skills match | Excellent benefits
   🔗 View Details | 📝 Apply

[View all 147 jobs] | [Filter results] | [Save search]
```

### Example 3: Job Analysis

```
User: "Analyze the first job in detail"

Agent: 📊 Detailed Analysis: Staff Software Engineer @ HealthTech Startup

🎯 Match Score: 95/100 (Excellent Match)

Breakdown:
✅ Skills Match: 98/100 (10/10 required skills)
   Have: Python ✓, AWS ✓, Docker ✓, JavaScript ✓, PostgreSQL ✓
   Required: Python, AWS, Docker, React, PostgreSQL
   Nice-to-have: Kubernetes (you don't have), GraphQL (you don't have)

💰 Salary Match: 95/100
   Offered: $160k-$190k
   Your Range: $150k-$200k
   Market Average for role: $165k
   Assessment: Competitive, slightly above market

📍 Location Match: 100/100
   100% Remote (US-based)
   Matches your preference perfectly

🏢 Company Match: 90/100
   • Stage: Series B ($30M raised)
   • Size: 85 employees
   • Industry: Healthtech (matches preference)
   • Growth: 150% YoY
   • Glassdoor: 4.3/5 (83 reviews)

🎁 Benefits Score: 92/100
   ✅ Unlimited PTO
   ✅ Full health/dental/vision
   ✅ 401k with 4% match
   ✅ Stock options (0.15-0.3%)
   ✅ $3k annual learning budget
   ✅ Latest equipment

🌟 Culture Score: 88/100
   ✅ Work-life balance: 4.5/5 (from reviews)
   ✅ Engineering-driven company
   ✅ Flexible hours
   ✅ Async-first communication
   ⚠️ Some reviews mention rapid growth challenges

📈 Career Growth:
   • Clear path to Principal Engineer
   • Building team from ground up
   • High impact opportunity
   • Mentorship opportunities

⚠️ Potential Concerns:
   • Startup risk (but well-funded)
   • Small team (more responsibility)
   • Missing 2 nice-to-have skills

💡 Recommendation:
   This is an EXCELLENT opportunity that aligns very well with your goals.
   The company culture emphasizes work-life balance (your priority), the
   salary is competitive, and you have all required skills. The role offers
   significant growth potential in a growing healthtech company.

   Action: STRONGLY RECOMMEND APPLYING

[Apply Now] | [Save for Later] | [Compare with Others] | [See Similar Jobs]
```

### Example 4: Application

```
User: "Apply for this job"

Agent: 📝 Preparing application...

✅ Application form filled
✅ Resume tailored for this role
✅ Cover letter generated
✅ Documents attached

📄 Cover Letter Preview:
---
Dear Hiring Manager,

I am excited to apply for the Staff Software Engineer position at [Company].
With 8 years of experience building scalable backend systems using Python and
AWS, I am confident I can make immediate contributions to your healthtech
platform.

In my current role, I have:
• Led the migration of monolithic services to microservices on AWS, improving
  scalability by 300%
• Built and deployed Docker-based CI/CD pipelines reducing deployment time by 70%
• Mentored 5 junior engineers, fostering a culture of technical excellence

I am particularly drawn to your mission of improving healthcare accessibility
through technology. Your commitment to work-life balance and engineering
excellence aligns perfectly with my values and career goals.

I would welcome the opportunity to discuss how my experience can contribute
to your team's success.

Best regards,
[Your Name]
---

Ready to submit?
[Yes, Submit] | [Edit Cover Letter] | [Edit Resume] | [Cancel]
```

```
User: "Yes, submit"

Agent: ✅ Application Submitted Successfully!

📬 Confirmation Details:
   • Application ID: APP-2024-1234
   • Submitted: Dec 15, 2024 at 2:34 PM
   • Status: Under Review
   • Expected Response: 5-7 business days

📅 Next Steps:
   ✓ Application tracked in your dashboard
   ✓ Status monitoring activated
   ✓ Follow-up reminder set for Dec 22
   ✓ Interview prep materials prepared

🔔 You'll be notified of any status changes.

[View Application] | [Search More Jobs] | [Application Dashboard]
```

### Example 5: Comparison

```
User: "Compare my top 3 job offers"

Agent: 📊 Job Offer Comparison

┌─────────────────┬────────────────┬────────────────┬────────────────┐
│                 │ HealthTech     │ Fintech        │ Digital Bank   │
│                 │ Startup        │ Scale-up       │                │
├─────────────────┼────────────────┼────────────────┼────────────────┤
│ Match Score     │ 95% ⭐⭐⭐⭐⭐  │ 92% ⭐⭐⭐⭐⭐  │ 88% ⭐⭐⭐⭐    │
├─────────────────┼────────────────┼────────────────┼────────────────┤
│ Salary          │ $160k-$190k    │ $155k-$185k    │ $150k-$175k    │
│                 │ 💰 Best        │ 💰 Good        │ 💰 Acceptable  │
├─────────────────┼────────────────┼────────────────┼────────────────┤
│ Equity          │ 0.15-0.3%      │ 0.1-0.2%       │ 0.05-0.15%     │
│                 │ 🚀 Highest     │ 🚀 Good        │ 🚀 Lower       │
├─────────────────┼────────────────┼────────────────┼────────────────┤
│ Stage           │ Series B       │ Series C       │ Series B       │
│                 │ Higher risk    │ Lower risk     │ Medium risk    │
├─────────────────┼────────────────┼────────────────┼────────────────┤
│ Team Size       │ 85 employees   │ 200 employees  │ 120 employees  │
├─────────────────┼────────────────┼────────────────┼────────────────┤
│ Work-Life       │ 4.5/5 ⭐ Best  │ 3.8/5 ⭐⭐⭐    │ 4.0/5 ⭐⭐⭐⭐   │
│ Balance         │                │                │                │
├─────────────────┼────────────────┼────────────────┼────────────────┤
│ Remote Policy   │ 100% Remote    │ 100% Remote    │ Hybrid (3/2)   │
│                 │ ✅ Matches     │ ✅ Matches     │ ⚠️ Doesn't     │
├─────────────────┼────────────────┼────────────────┼────────────────┤
│ PTO             │ Unlimited      │ 25 days        │ 20 days        │
├─────────────────┼────────────────┼────────────────┼────────────────┤
│ Learning Budget │ $3k/year       │ $2k/year       │ $1.5k/year     │
├─────────────────┼────────────────┼────────────────┼────────────────┤
│ 401k Match      │ 4%             │ 5% ⭐ Best     │ 3%             │
├─────────────────┼────────────────┼────────────────┼────────────────┤
│ Career Growth   │ High impact    │ Structured     │ Moderate       │
│                 │ Staff → Prin.  │ Senior → Lead  │ Senior → Lead  │
└─────────────────┴────────────────┴────────────────┴────────────────┘

🏆 Recommendation: HealthTech Startup (95% match)

Reasoning:
1. ✅ Highest compensation (salary + equity)
2. ✅ Best work-life balance (your #1 priority)
3. ✅ 100% remote (matches preference)
4. ✅ Healthtech industry (matches preference)
5. ✅ Highest impact / fastest growth
6. ⚠️ Slightly higher risk (but well-funded)

However, consider Fintech Scale-up if:
• You prefer more structure and lower risk
• Better 401k match is important
• You want established processes

[View Detailed Analysis] | [Apply to Top Choice] | [Negotiate Offer]
```

### Example 6: Tracking

```
User: "Show my application status"

Agent: 📊 Application Dashboard

Active Applications: 12
└─ Under Review: 7
└─ Interview Scheduled: 3
└─ Offer Received: 2

🎯 Recent Activity:

1. HealthTech Startup - Staff Engineer
   Status: OFFER RECEIVED 🎉
   Applied: Dec 15 | Offer: Dec 22
   Next: Respond by Dec 29

2. Fintech Scale-up - Senior Backend Engineer
   Status: INTERVIEW SCHEDULED 📅
   Applied: Dec 14 | Interview: Dec 23 at 2:00 PM
   Type: Technical (90 min)
   Next: Review prep materials

3. Digital Bank - Senior Full-Stack Engineer
   Status: INTERVIEW SCHEDULED 📅
   Applied: Dec 13 | Interview: Dec 21 at 10:00 AM
   Type: Phone Screen (30 min)
   Next: Prepare questions

4. AI Startup - ML Engineer
   Status: UNDER REVIEW ⏳
   Applied: Dec 16 | Updated: Dec 18
   Expected Response: Dec 21-23

5. Cloud Company - Platform Engineer
   Status: UNDER REVIEW ⏳
   Applied: Dec 15
   Expected Response: Dec 20-22

[View All Applications] | [Prepare for Interviews] | [Manage Offers]
```

## Technical Implementation

### Architecture

```
personalized-job-search-agent/
├── scripts/
│   ├── search/
│   │   ├── linkedin_search.py      # LinkedIn job search
│   │   ├── indeed_search.py        # Indeed job search
│   │   ├── glassdoor_search.py     # Glassdoor job search
│   │   ├── unified_search.py       # Multi-platform orchestration
│   │   └── search_utils.py         # Common search utilities
│   ├── analysis/
│   │   ├── job_scorer.py           # Job scoring algorithm
│   │   ├── skills_matcher.py       # Skills matching engine
│   │   ├── salary_analyzer.py      # Salary analysis
│   │   ├── company_research.py     # Company info gathering
│   │   └── comparison_engine.py    # Job comparison logic
│   ├── application/
│   │   ├── form_filler.py          # Auto-fill applications
│   │   ├── cover_letter_gen.py     # AI cover letter generation
│   │   ├── resume_tailor.py        # Resume customization
│   │   └── application_tracker.py  # Track submissions
│   ├── storage/
│   │   ├── profile_manager.py      # User profile management
│   │   ├── job_database.py         # Job storage and retrieval
│   │   └── application_db.py       # Application tracking DB
│   └── main.py                     # Main orchestration
├── assets/
│   ├── user_profile.json           # Your profile data
│   ├── jobs_database.json          # Discovered jobs
│   ├── applications.json           # Application tracking
│   └── preferences.json            # Search preferences
├── references/
│   ├── API_SETUP.md                # API key setup guide
│   ├── USER_GUIDE.md               # User manual
│   ├── ALGORITHMS.md               # Scoring algorithm details
│   └── PRIVACY.md                  # Privacy and data handling
└── tests/
    └── test_*.py                   # Unit tests
```

### Data Models

**User Profile**
```json
{
  "personal": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "location": "San Francisco, CA"
  },
  "professional": {
    "current_role": "Senior Software Engineer",
    "experience_years": 8,
    "skills": [
      {"name": "Python", "years": 8, "proficiency": "expert"},
      {"name": "JavaScript", "years": 6, "proficiency": "advanced"},
      {"name": "AWS", "years": 5, "proficiency": "advanced"}
    ],
    "education": [
      {"degree": "BS Computer Science", "school": "Stanford", "year": 2015}
    ],
    "certifications": ["AWS Solutions Architect", "Kubernetes CKAD"]
  },
  "preferences": {
    "desired_roles": ["Staff Engineer", "Senior Engineer", "Tech Lead"],
    "industries": ["fintech", "healthtech"],
    "salary_min": 150000,
    "salary_desired": 175000,
    "salary_max": 200000,
    "locations": ["remote"],
    "company_sizes": ["startup", "midsize"],
    "benefits_priorities": ["work_life_balance", "equity", "learning"],
    "dealbreakers": ["no_remote", "below_salary_min", "excessive_hours"]
  }
}
```

**Job Object**
```json
{
  "id": "job_12345",
  "title": "Staff Software Engineer",
  "company": "HealthTech Startup",
  "location": "Remote",
  "salary_range": [160000, 190000],
  "description": "...",
  "requirements": ["Python", "AWS", "Docker"],
  "nice_to_have": ["Kubernetes", "GraphQL"],
  "benefits": ["unlimited_pto", "health_insurance", "equity"],
  "posted_date": "2024-12-10",
  "source": "linkedin",
  "url": "https://...",
  "match_score": 95,
  "score_breakdown": {
    "skills": 98,
    "salary": 95,
    "location": 100,
    "company": 90,
    "benefits": 92,
    "culture": 88
  },
  "analysis": {
    "missing_skills": ["Kubernetes", "GraphQL"],
    "recommendations": "Strong fit. Apply soon.",
    "career_growth": "High potential",
    "risk_level": "medium"
  }
}
```

### APIs Used

**Job Search APIs**
- LinkedIn Jobs API (via RapidAPI)
- Indeed API
- Glassdoor API
- JSearch (aggregated job search API)
- SerpAPI (for Google Jobs)

**Company Research**
- Clearbit API (company data)
- Glassdoor API (reviews)
- Crunchbase API (funding info)

**AI/ML**
- Anthropic Claude API (cover letters, analysis)
- OpenAI GPT-4 (alternative for text generation)
- Scikit-learn (matching algorithms)

**Application Automation**
- Selenium WebDriver (form automation)
- BeautifulSoup4 (HTML parsing)

## Privacy & Security

### Data Protection

✅ **Local-First Storage**: All your personal data is stored locally on your machine
✅ **Encryption**: Sensitive data is encrypted at rest
✅ **No Data Sharing**: Your profile is never shared without explicit permission
✅ **Secure API Keys**: API credentials stored in environment variables
✅ **Consent-Based**: Application automation requires explicit approval

### What Data Is Stored

- Your profile information (local)
- Job search history (local)
- Application tracking (local)
- API credentials (environment variables)

### What Data Is NOT Stored

- Your social media passwords
- Credit card or payment information
- Private messages or emails

## Setup Requirements

### Prerequisites

1. **Python 3.9+** installed
2. **Chrome browser** (for Selenium automation)
3. **API Keys** (free tiers available):
   - LinkedIn API key (or RapidAPI)
   - Indeed Publisher ID
   - Anthropic API key (for AI features)
   - Optional: OpenAI API key

### Installation

```bash
# 1. Install the agent
/plugin marketplace add ./personalized-job-search-agent-cskill

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# 4. Create your profile
"Create my job search profile"
```

### Cost Estimates

**Free Tier Usage (Recommended to Start)**
- Indeed API: 1000 queries/month (free)
- JSearch API: 100 searches/month (free)
- Anthropic Claude: $5/month for typical usage
- Total: ~$5-10/month

**Paid Usage (For Heavy Users)**
- LinkedIn API: $50/month
- Multiple job boards: $30/month
- AI generation: $20/month
- Total: ~$100/month

## Advanced Features

### Skill Gap Analysis

```
User: "What skills am I missing for senior ML engineer roles?"

Agent: 📊 Skill Gap Analysis: Senior ML Engineer

Based on 50 job postings analyzed:

✅ Skills You Have:
   • Python (required in 98% of jobs)
   • Machine Learning (required in 100% of jobs)
   • TensorFlow (required in 45% of jobs)
   • SQL (required in 60% of jobs)

⚠️ Skills Often Required (You're Missing):
   • PyTorch (required in 75% of jobs) ← HIGH PRIORITY
   • Kubernetes (required in 55% of jobs)
   • MLOps (required in 50% of jobs)
   • Spark (required in 40% of jobs)

💡 Recommendations:
   1. Learn PyTorch - Would increase your match rate by 30%
   2. Get MLOps experience - High demand skill
   3. Consider Kubernetes certification - Common requirement

📚 Learning Resources:
   • PyTorch Course: [link]
   • MLOps Specialization: [link]
   • Kubernetes for ML: [link]

Impact: Learning top 3 skills would boost your average match score from 72% to 89%
```

### Salary Negotiation

```
User: "Should I negotiate this $160k offer?"

Agent: 💰 Salary Analysis & Negotiation Strategy

Offer: $160,000 base salary
Role: Staff Software Engineer
Location: Remote
Company: HealthTech Startup (Series B)

📊 Market Data:
   • Average for role: $165,000
   • Range: $145k - $195k (25th - 75th percentile)
   • Your offer: 48th percentile (slightly below average)

✅ Reasons to Negotiate:
   1. You have all required skills + 3 years extra experience
   2. Market average is $5k higher
   3. Your salary requirement was up to $200k
   4. Startup can likely offer more equity if salary is constrained
   5. You have 2 other competing offers

💡 Negotiation Strategy:

   Recommended Ask: $175,000 base + 0.25% equity
   Fallback: $170,000 base + 0.20% equity
   Minimum: $165,000 (market average)

   Sample Script:
   "Thank you for the offer. I'm excited about the role and company. Based on
   my research and the market rate for this position, as well as my relevant
   experience, I was hoping we could discuss a base salary of $175,000. I'm
   also open to discussing additional equity if that's more feasible."

📈 Expected Outcome:
   • 70% chance of increase to $165k-$170k
   • 40% chance of hitting $175k
   • 90% chance of more equity

Alternative: If they can't budge on salary, ask for:
   - Signing bonus ($10-20k)
   - Extra equity (0.05-0.10% more)
   - Extra PTO (5 more days)
   - Larger learning budget

[Generate Negotiation Email] | [Compare with Other Offers] | [Accept Current Offer]
```

### Auto-Application with Approval

```
User: "Auto-apply to all jobs with 90%+ match, but ask me first"

Agent: 🤖 Auto-Application Mode: Approval Required

Settings:
   ✅ Minimum match score: 90%
   ✅ Approval required before each application
   ✅ Customized cover letters
   ✅ Tailored resumes

Found 5 jobs matching criteria (90%+):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Job 1/5: Staff Engineer @ HealthTech (95% match)
💰 $160k-$190k | 📍 Remote | ⭐⭐⭐⭐⭐

Generated Application:
   ✅ Resume: Emphasized Python + AWS experience
   ✅ Cover Letter: Highlighted healthtech passion
   📄 [Preview Cover Letter]

Apply to this job?
[Yes] [No] [Maybe Later]
```

## Limitations & Disclaimers

⚠️ **Important Notes**

1. **API Rate Limits**: Free tiers have limits. Heavy usage may require paid plans.
2. **Application Success**: Automation increases quantity, not guarantee of success.
3. **Platform ToS**: Some platforms may prohibit automation. Use responsibly.
4. **Data Accuracy**: Job data depends on third-party APIs. Always verify details.
5. **No Guarantee**: This tool helps you search and apply, but doesn't guarantee job offers.
6. **Human Review**: Always review applications before submission.
7. **Legal Compliance**: Ensure compliance with local employment laws.

## Troubleshooting

### Common Issues

**Issue: No jobs found**
- Solution: Broaden your search criteria
- Check if API keys are configured
- Verify your profile is complete

**Issue: Low match scores**
- Solution: Update your skills in profile
- Review skill gap analysis
- Consider upskilling or adjusting expectations

**Issue: Application automation fails**
- Solution: Some sites block automation
- Use manual application for those
- Check if Selenium/Chrome is configured correctly

**Issue: API rate limit exceeded**
- Solution: Wait for reset (usually 24 hours)
- Upgrade to paid tier
- Reduce search frequency

## Future Enhancements

🚀 **Roadmap**

- [ ] Interview scheduling automation
- [ ] Salary negotiation templates
- [ ] Video interview practice
- [ ] Portfolio generation from projects
- [ ] LinkedIn profile optimization
- [ ] Networking recommendations
- [ ] Referral request automation
- [ ] Job market trend predictions
- [ ] Career path simulator
- [ ] Skills course recommendations

## Support

Need help? Check:
- `references/USER_GUIDE.md` - Detailed user manual
- `references/API_SETUP.md` - API configuration help
- `references/TROUBLESHOOTING.md` - Common issues

---

**Remember**: This agent is a tool to augment your job search, not replace your judgment. Always review opportunities carefully and trust your instincts about what's right for your career.

Happy job hunting! 🎯
