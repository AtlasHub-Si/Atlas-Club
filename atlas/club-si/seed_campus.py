"""
AtlasClub Campus Bootstrap Seeder (`club.atlas-si.com`)
Creates the 6 canonical AtlasClub UserGroups (Free PT, Free FR, Premium, Paid Courses,
VIP Mentorship, Projects Lab) via LearnHouse REST API and prints a ready-to-paste
offers.json ID mapping for AtlasPayBridge (pay.atlashub.si).

Zero external dependencies (Python 3.10+ stdlib).
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

CANONICAL_GROUPS: list[dict[str, str]] = [
    {
        "offer_code": "club_free_pt",
        "name": "club-free-pt",
        "description": "Comunidade Free · AtlasClub Genesis (Português)",
    },
    {
        "offer_code": "club_free_fr",
        "name": "club-free-fr",
        "description": "Comunidade Free · AtlasClub France (Français)",
    },
    {
        "offer_code": "club_premium",
        "name": "club-premium",
        "description": "Comunidade Premium · AtlasClub Pro (Biblioteca, Calls & Ferramentas)",
    },
    {
        "offer_code": "course_atlas_harness",
        "name": "courses-pro",
        "description": "Cursos Pagos · Formação Atlas-Harness & Engenharia Agêntica",
    },
    {
        "offer_code": "mentorship_vip",
        "name": "mentorship-vip",
        "description": "Mentorias Pagas · Acompanhamento VIP & Executivos",
    },
    {
        "offer_code": "projects_lab",
        "name": "projects-lab",
        "description": "Projetos & Atlas Lab · Implementações e Turmas Dedicadas",
    },
]


def _req(
    method: str,
    url: str,
    token: str | None = None,
    json_body: dict[str, Any] | None = None,
    form_body: dict[str, str] | None = None,
) -> Any:
    headers: dict[str, str] = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data: bytes | None = None
    if form_body is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = urllib.parse.urlencode(form_body).encode("utf-8")
    elif json_body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(json_body).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw.strip() else {}


def run(api_url: str, email: str, password: str, org_id: int, org_slug: str, dry_run: bool) -> int:
    base = api_url.rstrip("/")
    print(f"[AtlasClub Seed] Target API: {base} | org_id={org_id} | dry_run={dry_run}")

    if dry_run:
        print("\n[DRY-RUN] Planned Authentication:")
        print(f"  POST {base}/auth/login (application/x-www-form-urlencoded: username={email})")
        print(f"  GET  {base}/usergroups/org/{org_id}")
        print("\n[DRY-RUN] Canonical UserGroups to ensure:")
        sim_mapping = {}
        for idx, grp in enumerate(CANONICAL_GROUPS, start=101):
            print(f"  - POST {base}/usergroups/ -> name={grp['name']!r} | offer={grp['offer_code']}")
            sim_mapping[grp["offer_code"]] = {
                "learnhouse_org_id": org_id,
                "learnhouse_usergroup_id": idx,
                "learnhouse_usergroup_name": grp["name"],
            }
        print("\n[DRY-RUN] Sample offers.json mapping:")
        print(json.dumps(sim_mapping, indent=2, ensure_ascii=False))
        return 0

    if not email or not password:
        print("Error: --email and --password are required when running without --dry-run", file=sys.stderr)
        return 1

    form: dict[str, str] = {"username": email, "password": password}
    if org_slug:
        form["org_slug"] = org_slug
    auth_resp = _req("POST", f"{base}/auth/login", form_body=form)
    token = auth_resp.get("access_token") or (auth_resp.get("tokens") or {}).get("access_token")
    if not token:
        print("Error: Login succeeded but no access_token returned.", file=sys.stderr)
        return 1

    existing = _req("GET", f"{base}/usergroups/org/{org_id}", token=token)
    by_name = {str(g.get("name")): g for g in (existing if isinstance(existing, list) else [])}

    mapping: dict[str, Any] = {}
    for grp in CANONICAL_GROUPS:
        if grp["name"] in by_name:
            found = by_name[grp["name"]]
            print(f"  [EXISTS] {grp['name']} -> id={found['id']}")
            ug_id = found["id"]
        else:
            created = _req(
                "POST",
                f"{base}/usergroups/",
                token=token,
                json_body={
                    "name": grp["name"],
                    "description": grp["description"],
                    "org_id": org_id,
                },
            )
            ug_id = created["id"]
            print(f"  [CREATED] {grp['name']} -> id={ug_id}")

        mapping[grp["offer_code"]] = {
            "learnhouse_org_id": org_id,
            "learnhouse_usergroup_id": ug_id,
            "learnhouse_usergroup_name": grp["name"],
        }

    print("\n[OK] Paste these IDs into AtlasPayBridge/config/offers.json:")
    print(json.dumps(mapping, indent=2, ensure_ascii=False))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed canonical UserGroups in AtlasClub LearnHouse")
    parser.add_argument("--api-url", default="https://club.atlas-si.com/api/v1")
    parser.add_argument("--email", default="")
    parser.add_argument("--password", default="")
    parser.add_argument("--org-id", type=int, default=1)
    parser.add_argument("--org-slug", default="atlasclub")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    sys.exit(run(args.api_url, args.email, args.password, args.org_id, args.org_slug, args.dry_run))


if __name__ == "__main__":
    main()
