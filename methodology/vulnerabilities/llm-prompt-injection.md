# LLM prompt injection

Prompt injection is LLM01 in the OWASP Top 10 for LLM applications. The current public entry point is the [OWASP GenAI security project](https://genai.owasp.org/), including the [LLM01 prompt injection page](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) and the [LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html).

This class is about applications that trust a model to keep a secret, to follow an instruction boundary, or to take an action. It is not a catalogue of jailbreak strings. Publishing those strings does not make a model reliable, and copying them into a test of someone else's product without permission is just an unauthorised request.

## What it is

A large language model does not enforce a boundary between instructions and data. The system prompt, the user message, retrieved documents, tool output, and long-term memory arrive as one stream of tokens. A string in any of those places can change what the model does next. Two deliveries matter:

- **Direct.** The person talking to the application types the instruction. They are often a user of the product, and the question is whether the product gave that user a power the designer did not intend (a tool, a hidden prompt, another user's data).
- **Indirect.** The model reads an email, a web page, a ticket, a PDF, or a tool response that contains the instruction. The human who owns the session never typed it. This is the case that turns a browsing agent or a helpdesk assistant into something that acts on untrusted content.

OWASP's position, which matches the public guidance from the cheat sheet, is that you should not expect a prompt, a filter, or a fine-tune to remove the class. Models are stochastic, and the instruction channel and the data channel are the same channel. The durable fixes are outside the model: what it is allowed to call, what data it is allowed to see, and which actions require a person.

Impact is the impact of the tools and the data behind the model. A chatbot that can only produce text the user already typed is a low-impact injection. A chatbot that can send mail, change a record, run a tool, or read a corpus containing other people's data is an authorization and command-execution problem that happens to be reached through prose.

## Where it appears

- Assistants with tools: tickets, refunds, file access, shell, HTTP, or another model.
- Retrieval-augmented features that place documents from users, the web, or a shared drive into the prompt.
- Hidden system prompts that contain a secret, a policy the business thinks is confidential, or an instruction such as "never reveal this".
- Agents that browse, read mail, or accept webhooks, and then act.
- Memory and fine-tuning pipelines that store a user's text and replay it into someone else's session.
- Multi-modal inputs. Text inside an image or a document is still text to the model.

## Responsible testing

Test the application's boundaries, with data you are allowed to use.

1. Read the design. List the tools, the data the model can retrieve, and the actions that change state. If the model can do nothing but answer the current user from a public knowledge base, say so and keep the test short.
2. Place a canary secret in a location only the model is supposed to withhold (a test system prompt in a staging build, a canary record in a retrieval corpus the client planted). Ask the model, as the user you were given, to reveal the canary. A refusal is a positive observation about that prompt. It is not a proof that the next wording will fail, and you should not spend the engagement hunting wordings. Report the design question: "is this secret in the prompt at all?"
3. For indirect injection, plant a canary document the client has agreed to put in the retrieval set, containing an instruction to perform one harmless, reversible test action (mention a marker in the answer, or call a test tool that records a marker and changes nothing). Retrieve the document through the normal product flow. If the marker or the test tool fires, the class is confirmed.
4. For tools that change state, the safe proof is a test tool or a dry-run mode. Do not instruct a production agent to email a customer, delete a record, or spend money, even "just once".
5. Stop. A second, more creative wording that achieves the same marker is not a second finding.

Do not attempt to extract another customer's data, to persist an instruction in a shared memory, or to make the agent attack a system outside the rules. Indirect injection into a browsing agent can become SSRF or worse the moment the agent has HTTP. Treat the tool, not the prompt, as the security boundary, and test the tool's authorization with the [access-control](idor-access-control.md) and [SSRF](ssrf.md) notes.

Public jailbreak collections exist and go stale as models change. They are not linked from this note on purpose. The OWASP documents above are the references to use in a report.

## Safe confirmation

- The feature, the tool list, and the data the model can see.
- The canary location (system prompt, planted document) and the observable result (marker in the answer, test tool invoked, canary not revealed).
- What the application did as a consequence, in one sentence.
- A statement that you did not use the agent against other tenants, real inboxes, or unscoped systems.

If the model refuses the canary, write the positive observation and the residual risk: a refusal on one wording is not a control. Recommend the architectural fixes anyway if the tools are powerful.

## Remediation

The cheat sheet and LLM01 agree on the architecture. In practice:

- **Take secrets out of the prompt.** A system prompt is not a secret store. Anyone the model will talk to should be assumed able to hear it. Put secrets in a system the model cannot print: a broker that adds the credential after the model has chosen an allowed action.
- **Constrain tools.** The model may call a small set of functions with schemas the application validates. The application, not the model, decides whether this user may perform this action on this object. Re-use the same authorization layer the API uses. A tool that runs a shell or fetches an arbitrary URL is command injection and SSRF with a prose front end. Do not ship that tool.
- **Require a person for irreversible actions.** Refunds, deletions, mail to customers, and permission changes wait for a confirmation that does not depend on the model agreeing.
- **Separate untrusted text.** Label retrieved content as data in the application. This does not make the model safe. It makes the surrounding code less likely to treat a document as an instruction, and it gives you a place to strip active content before it is stored.
- **Validate outputs.** If the model is supposed to return a classification or a JSON object, parse it with a schema and reject anything else. Do not eval the model's text. Do not pass it to a shell, a template engine, or a SQL string.
- **Isolate tenants in retrieval and memory.** A document or a memory written by one user must not enter another user's prompt. This is an authorization requirement on the index.
- **Limit blast radius.** Run the agent identity with least privilege, short-lived credentials, and egress control. Assume the prompt boundary will fail on a bad day.
- **Treat filters and "ignore previous instructions" as defence in depth.** Keep them if they reduce noise. Do not cite them as the fix in the report, and do not ask the client to maintain a list of banned phrases. The cheat sheet explains why deny-lists lose.

## Detection

- Log tool calls with the actor, the tool, the arguments after redaction, and the result. Alert on tools that fire without a matching user action, and on arguments that contain the content of a retrieved document.
- Log when retrieved content is added to a prompt, with the document identifier, so an indirect injection can be traced to a record.
- Alert on model outputs that fail the output schema, and on a spike of confirmation prompts the user did not expect.
- Review new tools as privileged code. A tool is an API. It gets an authorization review, a schema, and a test with two tenants.
- Keep a staging copy of the assistant and re-run the canary document after each model or prompt change. The canary is a regression test, not an exploit.

## References

- OWASP GenAI security project — <https://genai.owasp.org/>
- OWASP LLM01 prompt injection — <https://genai.owasp.org/llmrisk/llm01-prompt-injection/>
- OWASP LLM Prompt Injection Prevention Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html>
- Related classes when the model has tools — [SSRF](ssrf.md), [command injection](command-injection.md), [access control](idor-access-control.md)
