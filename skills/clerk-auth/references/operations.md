# Post-setup operations: gatekeeping + organizations

Load when the user wants to control who can sign up, send invitations, or
when org settings look wrong after dashboard onboarding.

## Gatekeeping: control who can sign up (CLI, verified)

All via CLI; on PowerShell follow the quoting rules in windows-cli.md.
Config changes are live immediately; verify with `clerk config pull` and
re-read the field (dry-run output can be swallowed by redirects).

- Restrict sign-up entirely — patch
  `{"auth_access_control": {"sign_up_mode": "restricted"}}` (enum:
  `public | restricted | waitlist`). `restricted` = strangers cannot sign up
  at all. Combine with invitations:
  `clerk api /invitations -X POST --file body.json --yes` -> invitation
  email sent, status `pending`. "email address is taken" = that person
  already has a Clerk account — no invitation needed.
- Email allowlist alternative:
  `{"auth_access_control": {"allowlist_enabled": true}}`.

## Org auto-enable trap

Dashboard onboarding (especially when enabling social connections/SSO)
silently flips `organization_settings.enabled: true` +
`force_organization_selection: true`, forcing every new signup through an
org-creation wall. Not using orgs? Patch
`{"organization_settings": {"enabled": false}}`.

## Orgs vs your own tenant model (product advice)

Single-tenant products often don't need Clerk Organizations at all: if the
app already has its own tenant key + role model, Clerk orgs duplicate
membership plumbing you would still have to map (`org_id` -> your tenant
id). Keep your tenant key as source of truth; revisit orgs only for
self-serve tenant creation or enterprise SAML/SCIM.

Reference: https://clerk.com/docs/guides/organizations/overview
