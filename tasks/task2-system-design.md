# Task 2: System Design Challenge

## Background
Ask Bosco needs a robust architecture for its marketing analytics platform. The current system is starting to show limitations as the company scales. You need to design a next-generation architecture that can handle growth while maintaining reliability and cost-efficiency.

## The Challenge
Design a scalable, reliable system for a marketing analytics platform that ingests data from multiple sources, transforms it, applies AI/ML models, and serves insights to clients.

## Requirements
Design a system that can:
- **Ingest data** from 100+ diverse sources (Google Ads, Facebook Ads, GA4, Shopify, TikTok, etc.)
- **Handle scale:** 50,000+ API calls per day, 1TB+ of new data monthly
- **Transform data** to create unified marketing metrics across platforms
- **Support AI/ML:** Apply predictive models for campaign optimization
- **Serve analytics** through real-time dashboards and APIs
- **Ensure data quality:** Validation, monitoring, and alerting
- **Maintain 99.9% availability**
- **Cost-efficient** operation (clients expect margins)
- **Audit & lineage:** Track data provenance for compliance

## Expected Deliverables
1. **High-level architecture diagram** (use any tool - draw.io, Excalidraw, hand-drawn is fine)
2. **Written explanations** (1-2 pages) covering:
   - Key components and their responsibilities
   - Data flow through the system (ingestion → transformation → serving)
   - Technology choices and why (can be tool-agnostic: "data warehouse," "message queue," "orchestrator")
   - How you handle failures and ensure reliability
   - Security considerations (data encryption, access control, API security)
   - Monitoring and observability approach
   - Cost optimization strategies
3. **Implementation plan:** How would you roll this out incrementally?
   - What would you build first (MVP)?
   - What can wait for later phases?
   - How do you migrate from the current system without downtime?

## Constraints
- The company primarily uses **Google Cloud Platform** (but feel free to suggest alternatives)
- The development team has **5 engineers** with varying experience levels
- Marketing agencies are your clients - they expect **reliable, timely data** (their clients depend on it)
- **Cost is important** but reliability is the priority
- Must comply with **GDPR and data protection regulations**

## Special Considerations
1. **Data source variety:** Each platform has different APIs, rate limits, schemas, and reliability
2. **Schema evolution:** Marketing platforms change their APIs regularly
3. **Client customization:** Different clients need different metrics and data sources
4. **Peak loads:** Campaign launches can cause 10x spikes in data volume
5. **Time sensitivity:** Clients need "yesterday's" data available by 8am

## Time
You should spend approximately 20 minutes on this task.

## What We're Looking For
- **Architectural thinking:** Can you design systems that scale?
- **Trade-off analysis:** Understanding when to use which patterns
- **Pragmatism:** Not over-engineering, but also not under-engineering
- **Team awareness:** Considering team capabilities in your design
- **Business alignment:** Balancing technical excellence with business needs
- **Incremental approach:** How do you eat the elephant one bite at a time?

Remember, this is a VP Engineering role - we're looking for someone who can architect systems while considering team, cost, and business constraints.

