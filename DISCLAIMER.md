# Disclaimer

This repository is a knowledge and methodology reference for **authorised** security testing and defence. It is written for people who already have permission to assess a system, and for the engineers who have to fix what those assessments find.

## Authorised use only

Use this material only where all of the following are true:

- You own the target, or you hold a current written authorisation from the owner (a statement of work, rules of engagement, or an equivalent legal instrument).
- The activity stays inside the agreed assets, time window, methods, and data-handling rules.
- You comply with the laws that apply to you and to the system under test, including computer-misuse and privacy law in the relevant jurisdictions.
- You stop when the rules of engagement tell you to stop, and you report issues through the agreed channel.

Accessing, scanning, or testing a system without permission can be a crime. Permission to test one host is not permission to test the host next to it, the vendor that operates it, or the customers who use it.

## What this repository is

The notes follow the same public tradition as the [OWASP Web Security Testing Guide](https://wstg.owasp.org/), the [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/), [MITRE ATT&CK](https://attack.mitre.org/), and [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final). They describe vulnerability **classes**, how an authorised tester recognises them at a high level, how to confirm impact with the least possible disturbance, and how to **fix and detect** them.

The small programs under `tools/` perform read-only configuration checks or local document checks. They run only against a target the operator names, and the network tools refuse to run until the operator sets an explicit authorisation flag.

## What this repository will not do for you

This repository does not ship exploit code, malware, ransomware, credential stealers, or a catalogue of ready-to-run attack strings. Where a public project already maintains raw test strings for authorised lab use, the notes link to that project instead of copying it. Those links are citations, not an invitation to use the material against systems you do not have permission to test.

## No professional relationship

Nothing here is legal advice, a contract, or a substitute for a signed rules-of-engagement document. It is not a representation that any particular test is lawful in your jurisdiction, or that any particular remediation is complete for your design. You are responsible for scoping, authorisation, safety, and the accuracy of reports you issue.

## No warranty

The software and the documents are provided under the MIT licence, without warranty of any kind. Security guidance goes out of date. Confirm behaviour against current vendor documentation and against the primary sources cited in each note before you rely on it in an engagement or a design review.

## Trademarks

OWASP, MITRE, ATT&CK, NIST, and the names of tools cited here belong to their respective owners. Citation does not imply endorsement by those projects.
