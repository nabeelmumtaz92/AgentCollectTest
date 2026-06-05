# ABOUT.md

## Why this role

**I have experience with this exact type of problem — during an internship I manually scraped the internet for company founder information and built a spreadsheet of over 500 companies. Since transitioning to software engineering, I am drawn to AI-native roles because they let me write code to automate what I once did by hand, making the process significantly more efficient and scalable.**

## How you work with AI tools

**I use ChatGPT, Codex, VS Copilot, and Claude daily. ChatGPT is my go-to for planning. Codex and VS Copilot are strongest for coding and building apps. Claude performs well across most categories.**

**My core principle is to stay with the same model for as long as possible on a given task. AI models perform best when they have full context — the longer I work with one model on a problem, the more accurate it becomes because it has built up the history of decisions and reasoning behind the work. Switching models mid-task means losing that context, so I treat it the way I would treat switching collaborators mid-project: only when necessary.**

**For this challenge, I used Claude Code throughout — from planning the architecture and discussing each section of PLAN.md, to building the pipeline. I directed the AI by discussing decisions before approving them rather than letting it write freely, which kept the output aligned with my own thinking.**

## Your last project (ReturnIt — a third-party return delivery service, built as two React Native apps and a React website)

- **One ambiguity**: **It wasn't clear early on that each retailer has different return policies, and that the critical variable is whether they allow third-party returns — which is what the entire service depends on. I only discovered this after building the app and reading through retailer policies, finding one that explicitly mentioned third-party returns. That reframed how I think about onboarding retailers going forward.**

- **One tradeoff**: **Still in MVP stage and working solo, I chose speed over design. All features needed to be functional for testing, so the UI — both layout and color theme — is not where I want it yet. Shipping a working product first was the right call.**

- **One mistake**: **I left Stripe payments active while I was the only user. Every test order required me to pay, and after fees I was losing money. I resolved it by disabling Stripe and allowing my email to bypass payments so I could accept and fulfill orders without charging myself.**

- **One review comment**: **Someone suggested featuring ReturnIt in email marketing campaigns. My original plan was flyers and Facebook, but the email idea was strong enough that I'm adding it to the marketing strategy.**

## Anything you'd improve about this challenge or our CLAUDE.md

**The overall structure was clear — plan first, then build the slice. However, the instructions use a lot of parenthetical clauses which made some directions harder to parse on first read. More direct phrasing would make it easier to follow, though I recognize that may be intentional to see how candidates handle ambiguity.**
