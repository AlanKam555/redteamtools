# Methodology

> Authorised use only. [Disclaimer](../DISCLAIMER.md) · [Security policy](../SECURITY.md) · [Repository index](../README.md) · [Licence](../LICENSE) · [Contributing](../CONTRIBUTING.md)

These notes are the working method for an authorised assessment. They follow the shape used by [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final) (plan, identify, assess, analyse, report) and the test catalogue in the [OWASP Web Security Testing Guide](https://wstg.owasp.org/). MITRE ATT&CK is the language for describing adversary behaviour to a defender. It is used here as a reporting and detection vocabulary, not as a list of procedures to copy.

Read [the disclaimer](../DISCLAIMER.md) first. Every activity below assumes a current written authorisation and a rules of engagement.

## Phases

| Note | Question it answers |
| --- | --- |
| [Scoping and rules of engagement](01-scoping-and-rules-of-engagement.md) | What are we allowed to touch, when, and how hard? |
| [Reconnaissance](02-reconnaissance.md) | What has the organisation already made public, and what must go back to the scope conversation? |
| [Enumeration](03-enumeration.md) | Of the assets that are in scope, what is actually exposed? |
| [Vulnerability analysis](04-vulnerability-analysis.md) | Which of those exposures are real, which are theoretical, and which are false positives? |
| [Web application testing](05-web-application-testing.md) | How do you cover an application without turning the test into a payload dump? |
| [API testing](06-api-testing.md) | How do object, function, and property authorization fail in APIs? |
| [Post-exploitation concepts](07-post-exploitation-concepts.md) | How do you talk about impact and detection without writing an intrusion manual? |
| [Reporting](08-reporting.md) | How does a finding become a decision? |

## Vulnerability classes

Each note in [vulnerabilities/](vulnerabilities/README.md) uses the same headings:

- **What it is.** The class, the trust boundary it breaks, and the impact in plain language.
- **Where it appears.** The kinds of feature that deserve attention.
- **Responsible testing.** What to compare, what evidence looks like, and when to stop. This stays at the level of method. The strings used in a lab live in the cited public guides.
- **Safe confirmation.** The smallest proof that supports the finding on an authorised target.
- **Remediation.** Design and code changes that remove the class, not a one-line filter.
- **Detection.** What logs, tests, and reviews make the class visible after the assessment.
- **References.** Primary sources that were real at the time of writing.

## Working rules that apply to every phase

1. The rules of engagement win over curiosity. A newly discovered host, a third-party login, or a tempting production action goes back to the client before it is tested.
2. Prefer the environment the client named for destructive or stateful tests. Production, when it is in scope at all, is tested at a rate and a depth the rules allow.
3. Prove the class. Do not collect a trophy. A second test account, a canary record, or a harmless marker is the usual evidence. Real customer data, real credentials, and persistence are not.
4. Stop on instability. Error spikes, latency, a lockout of a real user, or a write you did not intend are a reason to pause and call the emergency contact.
5. Write down what you did while you do it. A finding you cannot explain next week is not a finding you can defend.
6. Pair every weakness with the control that would have stopped it and the control that would have detected it. A report that only lists defects does not improve the programme.

## Severity, briefly

Use [CVSS](https://www.first.org/cvss/), name the version, and then adjust for the client's impact. The FIRST qualitative bands (Informational through Critical) are a shared language. They are not a substitute for the sentence that says which business process is exposed. The reporting note expands on this.

## How the rest of the repository fits

- Checklists for the decisions: [scoping](../checklists/scoping.md), [rules of engagement](../checklists/rules-of-engagement.md), [web](../checklists/web-application-testing.md), [API](../checklists/api-testing.md), [reporting](../checklists/reporting.md).
- Templates: [rules of engagement](../templates/rules-of-engagement.md), [finding](../templates/finding.md), [report](../templates/report.md), [executive summary](../templates/executive-summary.md).
- Cheatsheets: [index](../cheatsheets/README.md). Defensive header and TLS checks: [tools](../tools/README.md).
- Class catalogue with the upstream links: [resources/vulnerability-classes.md](../resources/vulnerability-classes.md).

## Where the raw strings live

This repository does not carry a payload catalogue. When an authorised test or a lab exercise needs the concrete inputs, use [payload and wordlist libraries](../resources/payload-libraries.md) and follow each project's own licence and terms. That page is the list. The files themselves stay upstream.
