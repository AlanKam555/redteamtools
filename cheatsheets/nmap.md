# Nmap

[Nmap](https://nmap.org/) discovers hosts and the services they expose. The manual is the [Nmap reference guide](https://nmap.org/book/man.html). Use it in the [enumeration](../methodology/03-enumeration.md) phase, against addresses the rules of engagement name.

## Before you run it

- Confirm the address is in scope. A CDN or shared cloud address often is not "the client's host".
- Agree a rate. Default timing is a reasonable start. The aggressive timing templates exist for laboratories and for networks you operate, not for a production assessment you have not load-tested.
- Exclude the ranges the client marked out, every time, with an exclude input you keep with the evidence.
- Decide whether version detection is in scope. It sends real probes. It is normal for an authorised host and too noisy for a wide sweep.
- Leave exploit-oriented scripts off. Enumeration answers "what is listening". Vulnerability analysis decides what is real. Mixing those steps is how a scan becomes an incident.

## A conservative service scan

Replace `TARGET` with an in-scope host or with a file of in-scope addresses.

```bash
nmap -sT -sV -p 1-1024 --open --reason \
  --max-retries 2 --host-timeout 5m \
  -oA evidence/nmap-scoped \
  TARGET
```

`-sT` is a TCP connect scan and does not need raw sockets. `-sV` asks the service for a version. `--open` keeps the notes readable. `-oA` writes the normal, greppable, and XML results next to the engagement evidence, not into this repository.

Add `-Pn` only when you know the host ignores discovery pings and the client has agreed you will hit every port anyway. Dropping host discovery by habit scans more addresses than you think.

UDP, full 65k port sweeps, and parallel scans of many hosts need an explicit line in the rules and a much calmer rate. Record what you actually ran, including the start time.

## What to write down

- The command, the time, and the target list.
- Open ports, the protocol you observed, and whether a version was confirmed or only claimed by a banner.
- Hosts that did not respond, so the report's limitations section is true.
- Anything that appeared and is not in the asset table. That goes back to scope before anyone tests it.

## What not to add

- Script categories whose purpose is exploitation or denial of service.
- A scan of a range because a name resolved into it and the neighbours looked interesting.
- A second, faster rerun because the first one was slow, without checking whether the first one is why it is slow.

## Official documentation

- Nmap — <https://nmap.org/>
- Reference guide — <https://nmap.org/book/man.html>

## Related in this repository

- [Cheatsheet index](README.md)
- [Enumeration](../methodology/03-enumeration.md)
- [ffuf](ffuf.md)
- [Scoping](../methodology/01-scoping-and-rules-of-engagement.md)
- [Disclaimer](../DISCLAIMER.md)
