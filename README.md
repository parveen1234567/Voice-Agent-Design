# Home Credit LAP Voice Agent Project

This project implements a reference flow for the SalesAgents AI Home Credit Loan Against Property (LAP) qualification use case. It includes a local terminal demo, a browser-based text demo, and an optional Bolna integration for real outbound voice calls.

## What is included

- A structured system prompt for the voice agent
- A deterministic conversation-state engine for qualification logic
- A browser chat interface served by a lightweight Python web server
- Optional outbound voice calls through a Bolna agent
- Bolna call status, transcript, and recording link retrieval
- A Render Blueprint configuration in `render.yaml`
- Edge-case handling for:
  - busy customer callback flow
  - transfer / EMI-reduction scenarios
  - disqualification rules
  - out-of-order answers
  - maximum loan cap handling
  - final human handoff
- Unit tests covering the most important scenarios

## Files

- `system_prompt.md` — final system prompt text for a voice platform
- `voice_agent/conversation.py` — eligibility state and business logic
- `voice_agent/prompt_builder.py` — prompt rendering with runtime variables
- `app.py` — terminal demo runner
- `web_app.py` and `web/index.html` — browser demo and API
- `voice_agent/bolna_client.py` — Bolna outbound call and execution API client
- `render.yaml` — one-click Render service configuration
- `tests/test_conversation.py` — coverage for the core flows

## Run the terminal demo

```bash
python app.py
```

## Run the browser demo locally

From the project folder:

```bash
python web_app.py
```

Open <http://localhost:8000> in a browser.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Connect a real voice agent with Bolna

This integration calls an agent that you configure in your Bolna account. It does not create an account, purchase a number, or configure speech providers automatically.

1. Create/sign in to a Bolna account at <https://platform.bolna.ai>.
2. Create a voice agent in the Bolna dashboard. Configure its language, voice, and outbound telephony in Bolna.
3. Copy the contents of `system_prompt.md` into that agent's system prompt. Replace the `{{...}}` context placeholders with the appropriate values or configure equivalent dynamic variables in Bolna.
4. Save the agent and copy its agent ID.
5. In Bolna's dashboard, create an API key under **Developers → API Keys**.
6. Configure these environment variables on the server. Never put the Bolna API key in browser code, source control, or a public `.env` file:

   | Variable | Value |
   | --- | --- |
   | `BOLNA_API_KEY` | Bolna API key |
   | `BOLNA_AGENT_ID` | ID of the agent created above |
   | `WEB_ADMIN_TOKEN` | A long, unique private token that authorizes using the outbound-call feature |

7. Restart/redeploy the web app. When Bolna is configured, the browser page shows a **Make a real voice test call with Bolna** section.
8. Enter a test number in E.164 format (for example, `+919876543210`), the call-admin token, and confirm you are authorized and the recipient consents. Place calls only to numbers you are authorized to contact. Bolna call usage may incur charges.
9. The page will show the Bolna execution status and, when available, the transcript and recording link.

Bolna's official API quickstart documents the call endpoint (`POST https://api.bolna.ai/call`) and execution lookup (`GET https://api.bolna.ai/executions/{execution_id}`): <https://www.bolna.ai/docs/quickstarts/api>. API keys are sent to Bolna from the server using bearer authentication.

### Configure Bolna on Render

After creating the Render service, open its **Environment** settings and add `BOLNA_API_KEY`, `BOLNA_AGENT_ID`, and `WEB_ADMIN_TOKEN` as secret environment variables. Save changes and redeploy. Keep the service URL and admin token private; the token protects the outbound-call endpoint.

### Configure Bolna locally in PowerShell

Set the variables in the same PowerShell window before running the web server:

```powershell
$env:BOLNA_API_KEY = "your-bolna-api-key"
$env:BOLNA_AGENT_ID = "your-bolna-agent-id"
$env:WEB_ADMIN_TOKEN = "a-long-private-call-admin-token"
python web_app.py
```

Do not paste credentials into chat or commit them to the project.

## Deploy the app on Render

1. Push this project folder to a GitHub repository.
2. Sign in to Render and choose **New +** → **Blueprint**.
3. Connect the GitHub repository and select the branch containing `render.yaml`.
4. Review the `home-credit-lap-demo` web service and create it.
5. When the deployment finishes, open the Render URL shown for the service.

The service uses `python web_app.py` as its start command and reads Render's `PORT` environment variable automatically. To enable real Bolna calls, also add the three Bolna-related environment variables above.

## Important limitations

- The text demo is a browser-based simulation. The optional Bolna setup enables actual outbound phone calls through the configured Bolna agent.
- Conversation sessions are held in server memory and may be lost when the service restarts; this is for demos, not production customer data.
- Do not use this demo with real customer financial or property information.
- Outbound calls incur usage charges and must comply with consent, telemarketing, and privacy requirements.


##Deploy link:
https://home-credit-lap-demo.onrender.com/
