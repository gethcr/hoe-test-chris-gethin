# Task 3: Engineering Leadership Challenge

## Scenario
You've been VP Engineering at Ask Bosco for just two weeks. The company is preparing for a major product launch and expansion, with a critical demo to a large agency client in 3 weeks. The following situations all require attention from your engineering team:

## Your Team
- 2 Data Engineers (1 senior, 1 mid-level)
- 1 Data Scientist (senior, focused on AI/ML models)
- 2 Full-stack Developers (both mid-level, working on dashboards and APIs)

## Competing Priorities

### 1. Data Quality Crisis (Critical)
**What happened:** A major agency client (20% of revenue) discovered their revenue attribution reports have been showing incorrect numbers for the past 2 weeks. The CEO is getting daily calls from their CMO.

**Root cause:** Initial investigation shows a bug in the data pipeline that's mis-attributing conversions when multiple channels are involved in the customer journey.

**Estimated fix:** 3-4 days of engineering time to fix the bug, validate historical data, and implement better testing.

**Impact:** Client threatening to churn, reputation damage, potential legal liability for bad data.

---

### 2. Feature Commitment (High Pressure)
**What happened:** Your VP of Sales committed to integrating 5 new data sources (TikTok Ads, Pinterest Ads, Klaviyo, Attentive, Yotpo) for a key prospect before month-end (3 weeks away). The deal is worth $500K ARR.

**Technical reality:** Each integration typically takes 1 week of data engineer time, including schema mapping, testing, and validation (5 weeks total if done sequentially).

**Current state:** No work has started yet.

**VP Sales perspective:** "We promised this, we can't lose this deal."

---

### 3. Cost Overrun (CFO Pressure)
**What happened:** Your cloud data warehouse costs have increased from $15K/month to $45K/month over the last 8 weeks. The CFO has flagged this as unsustainable and wants immediate action.

**Investigation findings:** 
- Several inefficient queries running hourly
- No query result caching
- Some data sources being fully re-ingested daily instead of incrementally
- Test data not being cleaned up

**Estimated fix:** 1-2 weeks of optimization work across the stack.

**CFO's ask:** "Cut this by 50% within 30 days."

---

### 4. Pipeline Performance (Client Experience)
**What happened:** Your data pipelines are taking 4-5 hours to complete, meaning client dashboards don't show "yesterday's" data until 10am-11am. Marketing agencies need data by 8am for their morning standup meetings.

**Client feedback:** Multiple complaints about stale data, threatening the NPS score.

**Technical cause:** Sequential processing, no parallelization, some inefficient transformations.

**Estimated fix:** 2-3 weeks to refactor for parallel processing.

---

### 5. Team Development (Productivity Drain)
**What happened:** Your mid-level data engineer is struggling significantly. Their pull requests require 2-3 rounds of extensive revisions, they're not following Python best practices, and their code is causing bugs in production.

**Impact:** The senior data engineer is spending 30-40% of their time on code reviews and mentoring, slowing down critical work.

**Team morale:** The mid-level engineer seems discouraged. The senior engineer is getting frustrated.

**Context:** The mid-level engineer was hired 4 months ago and showed promise initially.

---

## Your Task

As VP Engineering, create a comprehensive plan for the next 3 weeks. Your response should include:

### 1. Prioritization (Most Important)
- List these 5 items in priority order
- Provide clear justification for your prioritization
- Explain any trade-offs you're making

### 2. Action Plans
For each of the top 3 priorities:
- Specific actions you would take
- Timeline and milestones
- Success metrics
- Risk mitigation strategies

### 3. Delegation Strategy
- What would you handle personally?
- What would you delegate (and to whom specifically)?
- How would you ensure accountability?

### 4. Stakeholder Communication
Outline how you would communicate your plan to:
- **Your engineering team** (what's the message and tone?)
- **The CEO** (what does she need to know?)
- **VP of Sales** (how do you manage expectations?)
- **CFO** (how do you address cost concerns?)
- **The affected client** (if you communicate directly, what do you say?)

### 5. Process Improvements
- What processes or systems would you implement to better handle competing priorities in the future?
- How do you prevent these situations from recurring?

### 6. Tough Calls
Be prepared to discuss:
- Would you push back on the Sales commitment? If so, how?
- Would you consider adding headcount? When and for what roles?
- What would you sacrifice or defer?

## Time
You should spend approximately 20 minutes on this task.

## What We're Looking For
- **Judgment & Prioritization:** Can you distinguish truly critical issues from urgent-but-not-critical ones?
- **Leadership Communication:** How do you deliver hard messages while maintaining trust?
- **Delegation Skills:** Do you know when to be hands-on vs. when to empower your team?
- **Strategic Thinking:** Are you just firefighting or also building systems to prevent fires?
- **Empathy & Team Health:** Do you consider the human element in your decisions?
- **Business Acumen:** Do you understand the business impact of technical decisions?

**Remember:** There are no perfect answers. Real leadership is about making the best decision with incomplete information and constraint resources. We want to see how you think through these trade-offs.

