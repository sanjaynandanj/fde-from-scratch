# On-Prem and Air-Gapped: Shipping Software You Can't SSH Into

**Phase 4 · Lesson 05 · ~1.5h**

## PROBLEM

Your team lands a pilot with a defense prime. The environment is a classified enclave in a SCIF — no internet, no VPN, no operator access from your side, and updates enter the enclave on a physical media transfer that runs twice a week. Your senior FDE flies out for a two-day install. Day one: the offline install script assumes it can `pip install` a missing dependency and fails at step 4. Day two: the fix requires a new tarball, but the media transfer is Friday, and it's Thursday afternoon. The customer's operator is patient but tired; the sponsor is watching. The pilot's schedule loses two weeks.

The mistake was easy to make and hard to unlearn: the team's install muscle memory assumed *some* connectivity — a package registry, a container pull, a fallback to public DNS. Air-gapped environments punish every implicit assumption. Software that ships into them must be *complete* on delivery, verifiable without the internet, and operable by a human who is not you.

## INTUITION

"Air-gapped" is a spectrum. In order of increasing pain:

1. **On-prem, internet-connected.** Their data center, but egress to the internet exists (usually via proxy). You can pull images, updates, and licenses. Roughly zone-3 rules with a longer cable.
2. **On-prem, restricted egress.** A short allowlist of package mirrors and license servers is permitted. Everything else denied. Common in financial services co-los.
3. **On-prem, no egress.** Nothing outbound. Updates come via internal mirrors the customer maintains, which they populate on their own schedule.
4. **True air-gap.** Physically disconnected network. Updates enter via approved media transfer — signed tarballs on a scanned USB, or a one-way data diode. No return channel except a phone call.
5. **Classified enclave.** Air-gap plus clearance requirements plus limited physical access.

The design shift from SaaS to air-gapped is not a config change — it's a philosophical reversal. In SaaS you *pull*: fetch config, phone-home telemetry, auto-update. In air-gapped you *ship*: everything the software needs must be in the artifact you handed over, verifiable offline, runnable by their operator following a runbook.

Four principles carry you:

**Bundle everything.** Base image, application code, all Python wheels or binaries, config templates, seed data, license files, CA bundles, docs. One artifact. `sha256sum` published separately so the customer can verify integrity before install.

**No phone home.** No implicit outbound calls. No telemetry-on-by-default. No license check that fails closed when the license server is unreachable. Every network call must be explicitly configured and off by default.

**Runbook-driven ops.** Every operation your team would normally do (restart, config change, log collection, upgrade) must be documented as a runbook the customer's operator executes. If a step requires you to be there, either script it or eliminate it.

**Versioned everything.** Air-gapped customers upgrade on their calendar, not yours. You will have six versions of your product running at six customers simultaneously. Every artifact, every schema, every API contract must carry a version and support N-2 compatibility at minimum.

## MAP IT

Build an **offline install pack** as your artifact spec before writing any of it.

1. **Manifest.** Write out every file that ships: image tarball (`docker save`), wheelhouse of deps, config templates, install script, uninstall script, verify script, runbook PDF, release notes, checksums, signature. One directory, one tarball.
2. **Preflight checklist.** A script the operator runs first: checks OS version, kernel, cgroup version, disk space, required ports free, container runtime present and version, correct user/permissions. Fails loudly with a clear message per check. Exit non-zero and don't touch anything on failure.
3. **Install script.** Idempotent. Every step logs to a timestamped file. No network calls. Every subprocess call has a timeout. Rolls back on failure. Prints a big banner at the end: version installed, config path, log path, next steps.
4. **Verify script.** Runs after install. Hits internal health endpoints. Confirms schema version. Prints a report. This is what the operator screenshots and sends back as evidence the install succeeded.
5. **Runbook.** Ten operations, each a page: start/stop, health check, log collection, config change, credential rotation, backup, restore, upgrade, downgrade, uninstall. Written for a competent operator who has never seen your product before.
6. **Support kit.** A `collect-diagnostics.sh` that bundles logs, config (with secrets redacted), version info, environment metadata into a single archive the customer can send you out-of-band. This will be the only debugging channel you have.

## FIELD NOTES

- Media transfer schedules are religion. If updates enter Fridays, ship on Thursday, not Monday — your fix will wait a week. Ask about the schedule before promising SLAs.
- The customer's operator is a person, and their day is not just you. Runbooks that assume undivided attention lose. Steps must be atomic, resumable, and idempotent. If the operator gets pulled to a fire in the middle of step 6, step 6 must be re-runnable safely.
- License-fail-closed is a real outage cause. If your product refuses to run because it can't reach a license server it was never supposed to reach, you have shipped a self-DoS. Fail open with loud logging, not closed with silence.
- Assume no shared filesystem, no internal registry, no monitoring stack you can rely on. If the customer has one, great; design as if they don't and treat their infra as a bonus.
- Version compatibility matters more than in SaaS. Your API contracts with their upstream systems must survive six months of drift on their side. Every schema field is a promise.
- Documentation is a first-class artifact. Air-gapped customers will read your PDF more carefully than SaaS customers ever read your marketing site. Typos in the runbook cost real support calls.
- Practice the install *in a lab that mirrors their constraints* — no internet, minimal privileges, the exact OS version they run. Every FDE team should have a "cold cell" VM for this.

## INTERVIEW ANGLE

Air-gapped shipping is a differentiator in FDE loops. Most SWE candidates have never done it; the ones who have are visibly senior. Interviewers probe both the technical patterns and the empathy for the operator.

Sample questions:

1. "Design the offline install experience for a product that today ships as a Helm chart pulling from public registries." (Bundle all images and charts, ship as tarball with checksums, private local registry option or `docker load`, preflight + install + verify scripts, runbook, no phone-home.)
2. "The customer says 'we can update this quarterly, at most.' What does that constrain in your product design?" (No breaking schema changes without migration, N-2 API compatibility, feature flags shipped defaulted-off, config-driven behavior over code, telemetry-free debugging via structured logs.)
3. "Your product needs to check licenses. The environment has no internet. How?" (Offline license file signed by your key, verified locally; grace period on expiry; fail-open with alarm rather than fail-closed; rotate via file drop.)

## DRILL

Take your last SaaS deployment. List every implicit outbound network call it makes — package installs, telemetry, license, CDN, model provider, DNS. Now write the plan to eliminate or bundle each one for an air-gapped ship. Estimate the work in engineer-weeks. Then write a one-page runbook for how the customer's operator restarts the app safely, including the health-check output that proves the restart succeeded. If either the plan or the runbook takes more than an hour, that's the honest gap between your product today and an air-gapped-ready product — and the honest slide to bring to your engineering leadership.
