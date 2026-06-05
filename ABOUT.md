# ABOUT: TradeBuddy (Rebranding to Edgara)

Reflective product engineering review outlining architectural decisions, trade-offs, and critical system insights from my prior platform development.

---

## Project Breakdown: TradeBuddy

### One Ambiguity: Balancing AI Flexibility with Risk Boundaries

When building the TradeBuddy AI assistant, deciding how open-ended the context prompts should be was a major hurdle. If the prompt was too rigid, the AI gave generic advice; if it was too loose, it risked sounding like unaligned financial advice. I had to implement a strict meta-prompting layer that enforces risk-aware guardrails and requires market context strings before delivering strategy breakdowns.

### One Tradeoff: Monolithic Simplicity vs. Real-Time Responsiveness

For the "Learn & Earn" progression tracks and leaderboards, I chose to handle data calculation and persistence directly via a robust Spring Boot core. While a separate microservice architecture could have isolated the gamification logic, keeping it in the primary Spring Boot backend drastically simplified transactional consistency for user balances, XP updates, and quiz submissions.

### One Mistake: State Synchronization Across Parallel Navigation

Early on, users completing a lesson quiz would experience an inconsistent UI state if they navigated away before the Spring Boot API finished processing the XP reward. The front-end leaderboard would lag behind. I had to refactor the React frontend client to use centralized global state management (Redux) to optimistically update the UI metrics while the backend database synchronized.

### One Review Comment That Changed My Mind

> _"Don't just track user profit; gamify the discipline."_

An early tester noted that a standard portfolio tracker feels discouraging during market drawdowns. Because of that feedback, I overhauled the entire system design to center around a "Learn & Earn" engine. Shifting the core loop to rewarding users with XP for completing risk-management courses and passing quizzes completely transformed the platform retention.
