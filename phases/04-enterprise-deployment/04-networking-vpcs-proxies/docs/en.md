# Networking: VPCs, Private Links, Proxies, and the Firewall Ticket

**Phase 4 · Lesson 04 · ~1.5h**

## PROBLEM

Demo day at a global insurer. Your pilot runs from a container in their VPC, calls the customer's warehouse over private networking, and sends telemetry back to your SaaS. Everything worked in staging. In their production VPC the app boots, connects to the warehouse, and then hangs on the first outbound HTTPS call to *your* metrics endpoint. Ten minutes of confused packet-tracing later, the customer's netops engineer joins the call: "yeah, egress from this subnet goes through our forward proxy — you need to trust our internal CA bundle and set `HTTPS_PROXY`. Also, `metrics.yourco.com` isn't on the allowlist. Firewall ticket takes five business days." The demo becomes a whiteboard talk. The champion is polite about it. Two of the executives don't come back to the next meeting.

Networking is where the FDE meets the customer's *real* posture. Diagrams lie; packet flow doesn't. Every deployment involves at least three network questions that must be answered before code ships: how does traffic get *in*, how does traffic get *out*, and which CA does the proxy present.

## INTUITION

Enterprise networking almost always sorts your traffic into four flow types. Each has a canonical solution and a canonical failure mode.

**1. Inbound user traffic.** How do their users reach your app?
- *Public over TLS* — allowed only for zone-1 SaaS (see lesson 01).
- *Private via PrivateLink / Private Endpoint / Interconnect* — the customer's users hit a private DNS name that resolves inside their network to a VPC endpoint pointing at your service. No public internet.
- *VPN or bastion* — legacy but real. Users tunnel in, then hit an internal address.

**2. Outbound to customer data sources.** Your app calls their warehouse, their SFTP, their API.
- *In-VPC*: your workload is deployed inside their network, calls are local. Simplest.
- *Cross-VPC via PrivateLink or peering*: your VPC and theirs are stitched together.
- *Site-to-site VPN*: your cloud, their data center.

**3. Outbound to the internet.** Your app calls your metrics endpoint, model provider, license server.
- *Direct egress* — rare in regulated envs.
- *Forward proxy* (Zscaler, Blue Coat, Palo Alto, F5) — the norm. Your app must respect `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY`, and the proxy typically performs **TLS interception** — it terminates TLS, inspects, then re-encrypts with an internal CA. Your app must trust that CA or every HTTPS call fails with a cert error.
- *Egress allowlist* — the firewall only lets you talk to explicitly listed hostnames. Nothing else resolves.

**4. Control-plane / management.** How does *your team* reach the deployed app for support?
- *Bastion / jump host* — SSH via their gateway with MFA.
- *Break-glass IAM* — a role you assume only during incidents, logged.
- *No access at all* — air-gapped; support is over screen-share with a customer operator on the keyboard.

The mental model: **traffic is guilty until proven allowed.** Every hop between your process and its destination is a policy decision made by a team that isn't in your standup. Enumerate the hops before deployment; do not discover them during a demo.

## MAP IT

Before writing infra, build a **flow diagram + allowlist request** the customer's netops team can execute in one ticket.

1. Draw four columns: **user → your app**, **your app → their data**, **your app → the internet**, **your team → your app**. For each, list source, destination, port, protocol, and the mechanism (public TLS, PrivateLink, proxy, etc.).
2. For every outbound flow write the *exact* hostname(s) and ports needed. `api.openai.com:443`, `metrics.yourco.com:443`, `pypi.org:443`, `registry.yourco.com:443`. Do not write "and any dependencies" — the netops team will reject the ticket.
3. **CA bundle question.** Write one line: "does egress traverse a TLS-intercepting proxy? If yes, please provide the internal root CA bundle." This unblocks an entire class of failures.
4. **Proxy env vars.** Confirm the app respects `HTTPS_PROXY`, `HTTP_PROXY`, `NO_PROXY`. Test in staging with a proxy in front. Many libraries (Python `requests` yes, some HTTP/2 clients no) have subtle proxy behavior.
5. **DNS.** Ask: does the environment have public DNS resolution, or only internal? Air-gapped envs resolve nothing you didn't tell them about.
6. **Ticket lead time.** Ask: "how long does an egress allowlist change take?" Two days at some shops, twenty at others. Plan the pilot's demo dates around this number.

## FIELD NOTES

- The proxy CA problem is the number-one deployment surprise. Bake CA-bundle injection into your container: read `/etc/ssl/certs/customer-ca.pem` on startup, append to the trust store, log the fingerprint. Then TLS interception is a config change, not a rebuild.
- Never hard-code hostnames like `api.yourco.com` into hot paths. Every external endpoint must be an environment variable and every allowlist entry must be documented. Customers will demand you route through their own aliases (`vendor-yourco.internal.customer.com`) and you'll be glad you can.
- "PrivateLink" means different things across clouds: AWS PrivateLink (VPC endpoint services), Azure Private Endpoint, GCP Private Service Connect. Pattern is the same; details differ. When a customer says private link, ask which.
- Some enterprises have *two* proxies: one for cloud egress, another for corp traffic. Your workload will hit only one, but confirm which — the wrong bundle burns a day.
- Bastion access for support is an underestimated commitment. If the customer provides a jump host with 30-day-rotating passwords and no session recording, your on-call rotation just got harder. Negotiate scoped, logged, break-glass access in the contract, not the runbook.
- `NO_PROXY` matters. If your app talks to a local sidecar or the customer's internal warehouse and forgets to set `NO_PROXY`, calls route through the proxy and get denied. Set it explicitly to the internal domain suffix.
- IPv6 will bite you. Some enterprise networks are IPv6-first internally; your container defaults may prefer IPv4 and time out on AAAA lookups. Test in the actual environment.

## INTERVIEW ANGLE

Networking questions in FDE loops probe whether you've actually deployed into a real enterprise or only read about it. Interviewers want specifics — proxy env vars, allowlist requests, CA bundles.

Sample questions:

1. "You deploy your app in a customer's VPC and every outbound HTTPS call fails with a certificate error. Walk me through debugging." (Suspect TLS-intercepting proxy; check `HTTPS_PROXY` env; ask for the internal CA bundle; inject into trust store; verify with `openssl s_client`.)
2. "The customer's netops team asks for the exact list of hostnames and ports you need to reach. What do you send back?" (Structured allowlist: hostname, port, protocol, purpose. Split by category — customer-data, product-egress, package registries, telemetry, model providers. Include a change process for adding new ones.)
3. "How do you support a customer whose environment gives your team zero SSH access?" (Runbook-driven ops, structured logs the customer forwards, an on-call channel with the customer's operator on the keyboard, screen-share incident bridge, feature flags controlled from within the workload, health-check contracts the customer's monitoring can hit.)

## DRILL

Take the last app you deployed. Draw its four-column network flow diagram (in, out to data, out to internet, in for support). List every hostname the app talks to. Draft the egress allowlist request you would send to a bank's netops team — one page, one table, one CA-bundle question. Have a colleague review it as if they were the netops engineer; count how many follow-up questions they asked. Each follow-up is a day of pilot delay you prevented next time.
