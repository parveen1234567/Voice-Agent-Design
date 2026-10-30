# 🏠 Home Credit LAP Voice Agent

<p align="center">
  <strong>An AI-powered Voice Agent solution designed for Home Credit Loan Against Property (LAP) qualification, customer eligibility assessment, lead screening, and outbound voice interactions using conversational AI and Bolna Voice Agents.</strong>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white">
  <img alt="AI Agent" src="https://img.shields.io/badge/AI-Agentic%20AI-purple">
  <img alt="Voice AI" src="https://img.shields.io/badge/Voice-Bolna-orange">
  <img alt="Frontend" src="https://img.shields.io/badge/UI-Web%20Chat-success">
  <img alt="Deployment" src="https://img.shields.io/badge/Deployment-Render-46E3B7">
</p>

<p align="center">
  <a href="https://home-credit-lap-demo.onrender.com/">🌐 Live Demo</a> •
  <a href="https://github.com/parveen1234567/Voice-Agent-Design">💻 Source Code</a>
</p>

---

# 🚀 Project Overview

The Home Credit LAP Voice Agent is an AI-driven customer qualification system designed to automate preliminary screening and eligibility assessment for Home Credit's Loan Against Property (LAP) offerings.

The solution uses conversational AI to engage customers, collect eligibility-related information, evaluate responses against predefined business rules, and determine whether a customer qualifies for further processing.

The application supports both text-based chat interaction and real outbound voice calls using Bolna Voice Agents.

---

# 💡 Problem Statement

Financial institutions often spend significant time and resources conducting initial loan qualification calls.

Traditional processes involve:

- Manual customer calls
- Repetitive eligibility screening
- Sales representative workload
- Delayed qualification decisions
- Inconsistent customer interactions

This project automates the qualification process while ensuring compliance with predefined business rules.

---

# 🎯 Product Value

The Home Credit LAP Voice Agent helps organizations streamline loan qualification workflows.

### For Customers

- Quick eligibility assessment
- Faster response times
- Consistent communication
- Convenient voice interactions

### For Sales Teams

- Automated lead qualification
- Reduced repetitive work
- Faster lead processing
- Improved efficiency

### For Financial Institutions

- Standardized qualification process
- Better lead management
- Reduced operational costs
- Increased productivity

---

# ✨ Core Features

## 🎙️ Voice Agent Integration

- Real outbound voice calls
- AI-powered conversations
- Human-like interaction flow
- Bolna voice platform support

---

## 💬 Browser Chat Demo

- Interactive web interface
- Simulated customer conversations
- Instant qualification testing

---

## ⚙️ Deterministic Qualification Engine

- Business rule enforcement
- Eligibility assessment
- Loan qualification workflow
- Structured conversation states

---

## 🔄 Conversation Flow Management

Handles:

- Eligibility checks
- Customer responses
- Qualification decisions
- Human handoff scenarios

---

## 📞 Callback Flow Support

Supports customer situations such as:

- Busy customers
- Call-back requests
- Rescheduled conversations

---

## 💸 EMI Reduction Scenarios

Handles:

- Existing loan inquiries
- Balance transfer requests
- EMI reduction discussions

---

## 🚫 Disqualification Logic

Supports automatic disqualification when:

- Business conditions are not met
- Customer does not satisfy requirements

---

## 🔀 Out-of-Order Responses

The system intelligently processes:

- Unexpected answers
- Non-linear conversations
- Follow-up clarifications

---

## 👨‍💼 Human Handoff Support

When required:

```text
AI Agent
    ↓
Human Agent
```

The interaction can be escalated to a human representative.

---

# 🏗️ System Architecture

## High-Level Architecture

```text
Customer
    │
    ▼
Voice / Chat Interface
    │
    ▼
Conversation Engine
    │
    ├── Eligibility Rules
    ├── State Management
    ├── Qualification Logic
    ├── Callback Handling
    └── Handoff Logic
    │
    ▼
Decision Output
```

---

## Voice Call Workflow

```text
Outbound Call
      │
      ▼
Customer Answers
      │
      ▼
AI Qualification Questions
      │
      ▼
Eligibility Evaluation
      │
      ▼
Qualified?
   ┌─────┴─────┐
   │           │
  YES          NO
   │           │
   ▼           ▼
Lead       Disqualified
Forward
```

---

# 📂 Project Structure

```text
Home-Credit-LAP-Voice-Agent/
│
├── system_prompt.md
│   └── Voice agent instructions
│
├── app.py
│   └── Terminal demo application
│
├── web_app.py
│   └── Browser demo server
│
├── render.yaml
│   └── Render deployment configuration
│
├── web/
│   └── index.html
│
├── voice_agent/
│   │
│   ├── conversation.py
│   │   └── Qualification business logic
│   │
│   ├── prompt_builder.py
│   │   └── Dynamic prompt rendering
│   │
│   └── bolna_client.py
│       └── Bolna API integration
│
├── tests/
│   └── test_conversation.py
│
└── README.md
```

---

# 🧰 Technology Stack

## Backend

| Technology | Purpose |
|------------|----------|
| Python | Core Development |
| REST APIs | Communication |
| JSON | Data Exchange |

---

## AI & Voice

| Technology | Purpose |
|------------|----------|
| Agentic AI | Customer Conversations |
| Bolna | Voice Calling Platform |
| Prompt Engineering | Conversational Flow |
| State Engine | Qualification Logic |

---

## Frontend

| Technology | Purpose |
|------------|----------|
| HTML | Interface Structure |
| CSS | Styling |
| JavaScript | Client Interactions |

---

## Deployment

| Technology | Purpose |
|------------|----------|
| Render | Cloud Hosting |
| GitHub | Source Control |

---

# 🔄 Qualification Flow

## Step 1: Initiate Contact

```text
Customer Contacted
```

---

## Step 2: Collect Information

Agent gathers:

- Customer details
- Loan requirements
- Property information
- Existing liabilities

---

## Step 3: Validate Eligibility

Business rules evaluate:

- Qualification criteria
- Eligibility conditions
- Loan requirements

---

## Step 4: Determine Outcome

Possible outcomes:

```text
Qualified

Disqualified

Callback Required

Transfer Required
```

---

## Step 5: Final Action

```text
Qualified Leads
       │
       ▼
Sales Team Follow-Up
```

---

# 🚀 Running the Project

## Terminal Demo

```bash
python app.py
```

---

## Browser Demo

```bash
python web_app.py
```

Open:

```text
http://localhost:8000
```

---

## Run Tests

```bash
python -m unittest discover -s tests -v
```

---

# 📞 Bolna Voice Integration

The application supports real voice calls through Bolna.

### Features

- Outbound AI calls
- Call status tracking
- Transcript retrieval
- Recording links
- Voice qualification workflow

### Required Variables

```env
BOLNA_API_KEY=your_key

BOLNA_AGENT_ID=your_agent_id

WEB_ADMIN_TOKEN=your_admin_token
```

---

# 🚀 Deployment

## Live Application

🌐 https://home-credit-lap-demo.onrender.com/

## Hosting Platform

Render

## Deployment Architecture

```text
GitHub Repository
        │
        ▼
      Render
        │
        ▼
 Home Credit LAP Voice Agent
        │
        ▼
 Browser Demo + Voice Integration
```

The application is deployed on Render and can be accessed directly through the provided public URL.

---

# 🧪 Testing & Quality Assurance

Unit tests cover:

✅ Customer Qualification

✅ Busy Customer Callback

✅ Disqualification Rules

✅ EMI Transfer Scenarios

✅ Out-of-Order Responses

✅ Human Handoff Logic

✅ State Transitions

✅ Business Rule Validation

---

# 🧩 Challenges Faced

## Conversation State Management

Managing customer interactions across multiple conversation stages.

### Learning

State-driven workflows improve consistency and reliability.

---

## Voice Agent Integration

Integrating conversational logic with an external voice platform.

### Learning

Voice experiences require robust error handling and flexible dialogue management.

---

## Business Rule Enforcement

Ensuring customer qualification follows strict lending policies.

### Learning

Financial workflows require deterministic decision-making instead of generic chatbot responses.

---

## Edge Case Handling

Managing unexpected customer behavior and response patterns.

### Learning

Real-world conversations rarely follow a fixed script.

---

# 📈 Future Enhancements

Future versions could include:

- 🤖 Advanced LLM-based Conversations
- 🌐 Multi-language Support
- 📊 Analytics Dashboard
- 📱 WhatsApp Integration
- 🎯 CRM Integration
- ☎️ Automated Follow-Ups
- 🔔 SMS Notifications
- ☁️ Database Persistence
- 🧠 Personalized Lead Scoring
- 📈 AI Sales Insights

---

# 📚 What I Learned

This project helped me gain practical experience in:

- Agentic AI Systems
- Prompt Engineering
- State Machine Design
- Voice Agent Development
- Qualification Workflow Design
- Business Rule Automation
- API Integration
- Conversation Management
- Deployment on Render
- AI-Powered Customer Engagement

---

# 🎯 Why This Project?

This project demonstrates how conversational AI can automate structured financial qualification processes while maintaining business compliance and consistent customer interactions.

Instead of relying entirely on human representatives, organizations can use AI-powered voice agents to qualify leads, improve efficiency, and reduce operational effort.

> **Qualify Leads. Automate Conversations. Accelerate Lending Decisions.**

---

# 📌 Project Highlights

- ✅ Agentic AI Architecture
- ✅ Voice Agent Integration
- ✅ Loan Qualification Workflow
- ✅ Browser Chat Simulator
- ✅ Bolna API Integration
- ✅ Conversation State Management
- ✅ Callback Handling
- ✅ Human Handoff Support
- ✅ Deployment on Render
- ✅ Recruiter-Friendly AI Project

---

# 🔗 Links

| Resource | Link |
|-----------|------|
| 🌐 Live Application | https://home-credit-lap-demo.onrender.com/ |
| 💻 GitHub Repository | https://github.com/parveen1234567/Voice-Agent-Design |
| 👨‍💻 GitHub Profile | https://github.com/parveen1234567 |
| 💼 LinkedIn | https://linkedin.com/in/shaik-chinthapalli-parveen-983668257 |

---

# 🙌 Final Note

The Home Credit LAP Voice Agent project represents my exploration of Agentic AI, voice automation, business-rule-driven conversations, and customer qualification workflows.

It demonstrates how AI agents can move beyond simple chatbots to support real business processes, automate customer interactions, and improve operational efficiency in the financial services domain.

> **Home Credit LAP Voice Agent — Engage. Qualify. Convert.**
