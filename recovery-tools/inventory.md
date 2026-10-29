# Bestands-Scan Portal + Crawler

- Zeitpunkt: 2026-10-29 18:58 CET
- Vergleichsbasis: portal = `39d9500`, crawler = `57c71a5`
- Arbeitskopien: 46 (mit eigener Arbeit: 43)

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage-wt-t_ee790195
- Branch: `integration/follow-profile-fixes-t_ee790195` · HEAD `c58d5cd` · Basis `39d9500`
- letzter Commit: 2026-10-29T18:01:37+01:00 — Merge fix/user-images-int-id-t_5c9697c9 + feat/follow-ui-wiring-t_94b0b061 into main
- **Commits über der Baseline: 109** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  233 files changed, 24463 insertions(+), 2865 deletions(-)
    - c58d5cd Merge fix/user-images-int-id-t_5c9697c9 + feat/follow-ui-wiring-t_94b0b061 into main
    - 1ee172d Merge fix/user-images-int-id-t_5c9697c9 (6725151 UUID-Regex + 9ef5096 int-ID) into main
    - d9eaa5b Integration: #15 Extension-Paket (Detailrouten, q-Param-Contract, Upload-Statusbanner) (#77)
    - e04ff8a test: fix inherited TypeScript diagnostics in signals/live-pins specs (issues #58/#71) (#78)
    - f43ae66 fix(design-tokens): Primitive-Verhalten + isoliertes Layout-Token-Paket (#60, Review R1) (#74)
    - d335137 fix(layout): Home rendert Navigation/Footer nur noch via LayoutShell (#60, Review R1) (#76)
    - 9c75478 docs(agents): Codegraph als erstes Werkzeug bei Code-Fragen verankern (#75)
    - d59742a fix(follows): FollowBlock liest Event-Namen auf Top-Level (data?.name) — Helper-Zeile rendered jetzt auf Occurrences (t_94b0b061)
    - 9ef5096 fix(user-profile): user_images.id ist integer - DELETE/PATCH validierten UUID
    - e219026 feat(follows): Follow-UI auf Detailseiten verdrahten (t_94b0b061)
    - 6725151 fix(user-profile): UUID-Regex fehlte eine Segment-Gruppe (friends+images)
    - e2d40e5 fix(signals): GET /api/signals uses active_signal RPC instead of st_x/st_y select
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)

## [portal] /Volumes/External Disk/Users/thomas/.hermes/kanban/workspaces/t_21aa1a63/wt
- Branch: `fix/extension-upload-cancel-status-t_21aa1a63` · HEAD `8b54adb` · Basis `39d9500`
- letzter Commit: 2026-10-29T13:30:52+01:00 — fix(extension): recompute upload summary banner; cancel batch reports abgebrochen instead of success wording
- **Commits über der Baseline: 108** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  205 files changed, 22437 insertions(+), 2384 deletions(-)
    - 8b54adb fix(extension): recompute upload summary banner; cancel batch reports abgebrochen instead of success wording
    - f022126 docs(extension): file header references q search param (review r1, t_d51fbf20)
    - 3718304 fix(extension): send documented q search param (test contract alignment, t_d51fbf20)
    - f0b6a27 test(extension): q-Param-Contract im events-Spec (Drift-Fix) und Upload-Contract-Suite wiederhergestellt
    - 45bdc96 fix(extension): restore Event-/Album-Detailrouten (aus 3b5c04e, risikogeprüft)
    - 54d3d60 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten
    - 463ac32 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - 2aeeea9 fix(signals): close F2/F3 SELECT/Realtime exposure vs privacy contract (t_cd58d2e2)
    - 127b153 fix(security): signals/signal_reports — remove authenticated INSERT grant+policy (Issue #58 F1)
    - cfec965 F6a: Add per-user rate limit to POST /api/signals/report
    - 5eb0b87 fix: Separate typecheck/test infra for Deno Edge Functions and E2E tests
    - 746e8f1 backup: haertetes DEV-Backup-Script (Credentials nur env/geschuetzte Datei, Ref-Assert ajbzqvderhzmrknwgryq, TLS verify-full mit Supabase-Prod-CA, Umask 077) + offizielle CA
    - d57c1d0 test: add regression test for location category 404 behavior
    - 1f552a0 fix: return 404 for unknown location categories instead of empty 200
    - 4b3c2b8 fix: handle location_categories array in event location links

## [portal] /Volumes/External Disk/Users/thomas/.hermes/kanban/workspaces/t_97d6fc6c/portal
- Branch: `wip/layout-parity-2026-10-29` · HEAD `511c8b3` · Basis `39d9500`
- letzter Commit: 2026-10-29T11:41:05+01:00 — fix(design-tokens): CitySidebar + LocationDetailContent auf semantische Tokens (bg-card/border-border/primary/muted-foreground), Dark-Mode-kompatibel
- **Commits über der Baseline: 107** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  225 files changed, 23834 insertions(+), 2895 deletions(-)
    - 511c8b3 fix(design-tokens): CitySidebar + LocationDetailContent auf semantische Tokens (bg-card/border-border/primary/muted-foreground), Dark-Mode-kompatibel
    - 6c4023f fix(components): Semantische Tokens statt Hardcodes in Footer, CityEventCard, ClaimModal, DatabaseEventTimeline, CityNewsSection (Dark-Mode-kompatibel)
    - 1d859d9 feat(design-tokens): success/warning/info Farbtokens (light+dark), ui-Primitives-Index, Box/Text aufgeraeumt
    - 2ad6bf7 wip(layout-parity): Sicherung der uncommitteten Paritaets-Arbeit (Navigation, Footer, Breadcrumbs, Homepage, Tests) - Stand 29.10. 08:53
    - 54d3d60 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten
    - 463ac32 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - 2aeeea9 fix(signals): close F2/F3 SELECT/Realtime exposure vs privacy contract (t_cd58d2e2)
    - 127b153 fix(security): signals/signal_reports — remove authenticated INSERT grant+policy (Issue #58 F1)
    - cfec965 F6a: Add per-user rate limit to POST /api/signals/report
    - 5eb0b87 fix: Separate typecheck/test infra for Deno Edge Functions and E2E tests
    - 746e8f1 backup: haertetes DEV-Backup-Script (Credentials nur env/geschuetzte Datei, Ref-Assert ajbzqvderhzmrknwgryq, TLS verify-full mit Supabase-Prod-CA, Umask 077) + offizielle CA
    - d57c1d0 test: add regression test for location category 404 behavior
    - 1f552a0 fix: return 404 for unknown location categories instead of empty 200
    - 4b3c2b8 fix: handle location_categories array in event location links
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)

## [portal] /Volumes/External Disk/Users/thomas/.hermes/kanban/workspaces/t_d243e1a9/wt
- Branch: `qa/extension-retest-t_d243e1a9` · HEAD `f022126` · Basis `39d9500`
- letzter Commit: 2026-10-29T12:48:58+01:00 — docs(extension): file header references q search param (review r1, t_d51fbf20)
- **Commits über der Baseline: 107** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  204 files changed, 22205 insertions(+), 2384 deletions(-)
    - f022126 docs(extension): file header references q search param (review r1, t_d51fbf20)
    - 3718304 fix(extension): send documented q search param (test contract alignment, t_d51fbf20)
    - f0b6a27 test(extension): q-Param-Contract im events-Spec (Drift-Fix) und Upload-Contract-Suite wiederhergestellt
    - 45bdc96 fix(extension): restore Event-/Album-Detailrouten (aus 3b5c04e, risikogeprüft)
    - 54d3d60 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten
    - 463ac32 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - 2aeeea9 fix(signals): close F2/F3 SELECT/Realtime exposure vs privacy contract (t_cd58d2e2)
    - 127b153 fix(security): signals/signal_reports — remove authenticated INSERT grant+policy (Issue #58 F1)
    - cfec965 F6a: Add per-user rate limit to POST /api/signals/report
    - 5eb0b87 fix: Separate typecheck/test infra for Deno Edge Functions and E2E tests
    - 746e8f1 backup: haertetes DEV-Backup-Script (Credentials nur env/geschuetzte Datei, Ref-Assert ajbzqvderhzmrknwgryq, TLS verify-full mit Supabase-Prod-CA, Umask 077) + offizielle CA
    - d57c1d0 test: add regression test for location category 404 behavior
    - 1f552a0 fix: return 404 for unknown location categories instead of empty 200
    - 4b3c2b8 fix: handle location_categories array in event location links
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage/.worktrees/t_d51fbf20
- Branch: `fix/extension-q-param-contract-t_d51fbf20` · HEAD `f022126` · Basis `39d9500`
- letzter Commit: 2026-10-29T12:48:58+01:00 — docs(extension): file header references q search param (review r1, t_d51fbf20)
- **Commits über der Baseline: 107** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  204 files changed, 22205 insertions(+), 2384 deletions(-)
    - f022126 docs(extension): file header references q search param (review r1, t_d51fbf20)
    - 3718304 fix(extension): send documented q search param (test contract alignment, t_d51fbf20)
    - f0b6a27 test(extension): q-Param-Contract im events-Spec (Drift-Fix) und Upload-Contract-Suite wiederhergestellt
    - 45bdc96 fix(extension): restore Event-/Album-Detailrouten (aus 3b5c04e, risikogeprüft)
    - 54d3d60 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten
    - 463ac32 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - 2aeeea9 fix(signals): close F2/F3 SELECT/Realtime exposure vs privacy contract (t_cd58d2e2)
    - 127b153 fix(security): signals/signal_reports — remove authenticated INSERT grant+policy (Issue #58 F1)
    - cfec965 F6a: Add per-user rate limit to POST /api/signals/report
    - 5eb0b87 fix: Separate typecheck/test infra for Deno Edge Functions and E2E tests
    - 746e8f1 backup: haertetes DEV-Backup-Script (Credentials nur env/geschuetzte Datei, Ref-Assert ajbzqvderhzmrknwgryq, TLS verify-full mit Supabase-Prod-CA, Umask 077) + offizielle CA
    - d57c1d0 test: add regression test for location category 404 behavior
    - 1f552a0 fix: return 404 for unknown location categories instead of empty 200
    - 4b3c2b8 fix: handle location_categories array in event location links
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage/.worktrees/t_21bd5d2f
- Branch: `fix/pnpm-lockfile-t_21bd5d2f` · HEAD `f11652a` · Basis `39d9500`
- letzter Commit: 2026-10-29T18:29:34+01:00 — fix: declare @upstash/redis + @upstash/ratelimit as optionalDependencies — resolvable in fresh install (t_21bd5d2f)
- **Commits über der Baseline: 105** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  233 files changed, 33748 insertions(+), 2855 deletions(-)
    - f11652a fix: declare @upstash/redis + @upstash/ratelimit as optionalDependencies — resolvable in fresh install (t_21bd5d2f)
    - 24920fb build: commit pnpm-lock.yaml — reproduzierbarer pnpm install (t_21bd5d2f)
    - d9eaa5b Integration: #15 Extension-Paket (Detailrouten, q-Param-Contract, Upload-Statusbanner) (#77)
    - e04ff8a test: fix inherited TypeScript diagnostics in signals/live-pins specs (issues #58/#71) (#78)
    - f43ae66 fix(design-tokens): Primitive-Verhalten + isoliertes Layout-Token-Paket (#60, Review R1) (#74)
    - d335137 fix(layout): Home rendert Navigation/Footer nur noch via LayoutShell (#60, Review R1) (#76)
    - 9c75478 docs(agents): Codegraph als erstes Werkzeug bei Code-Fragen verankern (#75)
    - e2d40e5 fix(signals): GET /api/signals uses active_signal RPC instead of st_x/st_y select
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b

## [portal] /private/tmp/wt-t_55d899b3
- Branch: `fix/admin-login-redirect-t_55d899b3` · HEAD `5408617` · Basis `39d9500`
- letzter Commit: 2026-10-29T17:21:00+01:00 — fix: preserve login target across Keycloak flow (#t_55d899b3)
- **Commits über der Baseline: 104** · ungepusht: 0 · uncommittet: 1 Dateien
- Umfang:  234 files changed, 24386 insertions(+), 2859 deletions(-)
    - 5408617 fix: preserve login target across Keycloak flow (#t_55d899b3)
    - d9eaa5b Integration: #15 Extension-Paket (Detailrouten, q-Param-Contract, Upload-Statusbanner) (#77)
    - e04ff8a test: fix inherited TypeScript diagnostics in signals/live-pins specs (issues #58/#71) (#78)
    - f43ae66 fix(design-tokens): Primitive-Verhalten + isoliertes Layout-Token-Paket (#60, Review R1) (#74)
    - d335137 fix(layout): Home rendert Navigation/Footer nur noch via LayoutShell (#60, Review R1) (#76)
    - 9c75478 docs(agents): Codegraph als erstes Werkzeug bei Code-Fragen verankern (#75)
    - e2d40e5 fix(signals): GET /api/signals uses active_signal RPC instead of st_x/st_y select
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)
    - (uncommittet) ?? dev.log

## [portal] /Volumes/External Disk/Users/thomas/.hermes/kanban/workspaces/t_38c574a5/wt
- Branch: `fix/signals-api-surface-t_61f40720` · HEAD `c8a2f38` · Basis `39d9500`
- letzter Commit: 2026-10-29T09:37:40+01:00 — feat(db): signals api surface — nearby_signals (recovered) + active_signal RPCs
- **Commits über der Baseline: 104** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  199 files changed, 21478 insertions(+), 2384 deletions(-)
    - c8a2f38 feat(db): signals api surface — nearby_signals (recovered) + active_signal RPCs
    - 54d3d60 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten
    - 463ac32 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - 2aeeea9 fix(signals): close F2/F3 SELECT/Realtime exposure vs privacy contract (t_cd58d2e2)
    - 127b153 fix(security): signals/signal_reports — remove authenticated INSERT grant+policy (Issue #58 F1)
    - cfec965 F6a: Add per-user rate limit to POST /api/signals/report
    - 5eb0b87 fix: Separate typecheck/test infra for Deno Edge Functions and E2E tests
    - 746e8f1 backup: haertetes DEV-Backup-Script (Credentials nur env/geschuetzte Datei, Ref-Assert ajbzqvderhzmrknwgryq, TLS verify-full mit Supabase-Prod-CA, Umask 077) + offizielle CA
    - d57c1d0 test: add regression test for location category 404 behavior
    - 1f552a0 fix: return 404 for unknown location categories instead of empty 200
    - 4b3c2b8 fix: handle location_categories array in event location links
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)

## [portal] /Volumes/External Disk/Users/thomas/.hermes/kanban/workspaces/t_8e391736
- Branch: `fix/signals-own-get-rpc-t_71` · HEAD `f995bd8` · Basis `39d9500`
- letzter Commit: 2026-10-29T11:14:48+01:00 — fix(signals): GET /api/signals uses active_signal RPC instead of st_x/st_y select
- **Commits über der Baseline: 104** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  199 files changed, 21558 insertions(+), 2393 deletions(-)
    - f995bd8 fix(signals): GET /api/signals uses active_signal RPC instead of st_x/st_y select
    - 54d3d60 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten
    - 463ac32 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - 2aeeea9 fix(signals): close F2/F3 SELECT/Realtime exposure vs privacy contract (t_cd58d2e2)
    - 127b153 fix(security): signals/signal_reports — remove authenticated INSERT grant+policy (Issue #58 F1)
    - cfec965 F6a: Add per-user rate limit to POST /api/signals/report
    - 5eb0b87 fix: Separate typecheck/test infra for Deno Edge Functions and E2E tests
    - 746e8f1 backup: haertetes DEV-Backup-Script (Credentials nur env/geschuetzte Datei, Ref-Assert ajbzqvderhzmrknwgryq, TLS verify-full mit Supabase-Prod-CA, Umask 077) + offizielle CA
    - d57c1d0 test: add regression test for location category 404 behavior
    - 1f552a0 fix: return 404 for unknown location categories instead of empty 200
    - 4b3c2b8 fix: handle location_categories array in event location links
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)

## [portal] /Volumes/External Disk/Users/thomas/Documents/.hermes/kanban/workspaces/t_ef17b388/wt
- Branch: `fix/ext-detail-routes-t_ef17b388` · HEAD `45bdc96` · Basis `39d9500`
- letzter Commit: 2026-10-29T09:20:32+01:00 — fix(extension): restore Event-/Album-Detailrouten (aus 3b5c04e, risikogeprüft)
- **Commits über der Baseline: 104** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  203 files changed, 22081 insertions(+), 2384 deletions(-)
    - 45bdc96 fix(extension): restore Event-/Album-Detailrouten (aus 3b5c04e, risikogeprüft)
    - 54d3d60 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten
    - 463ac32 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - 2aeeea9 fix(signals): close F2/F3 SELECT/Realtime exposure vs privacy contract (t_cd58d2e2)
    - 127b153 fix(security): signals/signal_reports — remove authenticated INSERT grant+policy (Issue #58 F1)
    - cfec965 F6a: Add per-user rate limit to POST /api/signals/report
    - 5eb0b87 fix: Separate typecheck/test infra for Deno Edge Functions and E2E tests
    - 746e8f1 backup: haertetes DEV-Backup-Script (Credentials nur env/geschuetzte Datei, Ref-Assert ajbzqvderhzmrknwgryq, TLS verify-full mit Supabase-Prod-CA, Umask 077) + offizielle CA
    - d57c1d0 test: add regression test for location category 404 behavior
    - 1f552a0 fix: return 404 for unknown location categories instead of empty 200
    - 4b3c2b8 fix: handle location_categories array in event location links
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage-wt-devslots
- Branch: `docs/agents-dev-slots` · HEAD `755650e` · Basis `39d9500`
- letzter Commit: 2026-10-29T16:49:59+01:00 — docs(agents): Devserver-Slots als Pflicht auf dem Entwicklungsrechner
- **Commits über der Baseline: 104** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  232 files changed, 24392 insertions(+), 2854 deletions(-)
    - 755650e docs(agents): Devserver-Slots als Pflicht auf dem Entwicklungsrechner
    - d9eaa5b Integration: #15 Extension-Paket (Detailrouten, q-Param-Contract, Upload-Statusbanner) (#77)
    - e04ff8a test: fix inherited TypeScript diagnostics in signals/live-pins specs (issues #58/#71) (#78)
    - f43ae66 fix(design-tokens): Primitive-Verhalten + isoliertes Layout-Token-Paket (#60, Review R1) (#74)
    - d335137 fix(layout): Home rendert Navigation/Footer nur noch via LayoutShell (#60, Review R1) (#76)
    - 9c75478 docs(agents): Codegraph als erstes Werkzeug bei Code-Fragen verankern (#75)
    - e2d40e5 fix(signals): GET /api/signals uses active_signal RPC instead of st_x/st_y select
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage-wt-t_d513d72f
- Branch: `feat/15-extension-test-contract` · HEAD `cc86cdc` · Basis `39d9500`
- letzter Commit: 2026-10-29T11:38:14+01:00 — test(extension): q-Param-Contract im events-Spec (Drift-Fix) und Upload-Contract-Suite wiederhergestellt
- **Commits über der Baseline: 104** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  199 files changed, 21516 insertions(+), 2384 deletions(-)
    - cc86cdc test(extension): q-Param-Contract im events-Spec (Drift-Fix) und Upload-Contract-Suite wiederhergestellt
    - 54d3d60 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten
    - 463ac32 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - 2aeeea9 fix(signals): close F2/F3 SELECT/Realtime exposure vs privacy contract (t_cd58d2e2)
    - 127b153 fix(security): signals/signal_reports — remove authenticated INSERT grant+policy (Issue #58 F1)
    - cfec965 F6a: Add per-user rate limit to POST /api/signals/report
    - 5eb0b87 fix: Separate typecheck/test infra for Deno Edge Functions and E2E tests
    - 746e8f1 backup: haertetes DEV-Backup-Script (Credentials nur env/geschuetzte Datei, Ref-Assert ajbzqvderhzmrknwgryq, TLS verify-full mit Supabase-Prod-CA, Umask 077) + offizielle CA
    - d57c1d0 test: add regression test for location category 404 behavior
    - 1f552a0 fix: return 404 for unknown location categories instead of empty 200
    - 4b3c2b8 fix: handle location_categories array in event location links
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage/.worktrees/t_25d029aa
- Branch: `fix/admin-fallback-t_25d029aa` · HEAD `d76ed15` · Basis `39d9500`
- letzter Commit: 2026-10-29T15:52:58+01:00 — fix(admin): unbekannte /admin/*-Pfade zeigen Admin-404 statt öffentlicher [lang]-Seite
- **Commits über der Baseline: 104** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  234 files changed, 24409 insertions(+), 2854 deletions(-)
    - d76ed15 fix(admin): unbekannte /admin/*-Pfade zeigen Admin-404 statt öffentlicher [lang]-Seite
    - d9eaa5b Integration: #15 Extension-Paket (Detailrouten, q-Param-Contract, Upload-Statusbanner) (#77)
    - e04ff8a test: fix inherited TypeScript diagnostics in signals/live-pins specs (issues #58/#71) (#78)
    - f43ae66 fix(design-tokens): Primitive-Verhalten + isoliertes Layout-Token-Paket (#60, Review R1) (#74)
    - d335137 fix(layout): Home rendert Navigation/Footer nur noch via LayoutShell (#60, Review R1) (#76)
    - 9c75478 docs(agents): Codegraph als erstes Werkzeug bei Code-Fragen verankern (#75)
    - e2d40e5 fix(signals): GET /api/signals uses active_signal RPC instead of st_x/st_y select
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage/.worktrees/t_d79b8737
- Branch: `fix/i18n-en-header-hero-t_d79b8737` · HEAD `4be027a` · Basis `39d9500`
- letzter Commit: 2026-10-29T16:00:16+01:00 — fix(i18n): Header-CTAs und Hero auf /en übersetzen (#81, t_d79b8737)
- **Commits über der Baseline: 104** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  234 files changed, 24467 insertions(+), 2880 deletions(-)
    - 4be027a fix(i18n): Header-CTAs und Hero auf /en übersetzen (#81, t_d79b8737)
    - d9eaa5b Integration: #15 Extension-Paket (Detailrouten, q-Param-Contract, Upload-Statusbanner) (#77)
    - e04ff8a test: fix inherited TypeScript diagnostics in signals/live-pins specs (issues #58/#71) (#78)
    - f43ae66 fix(design-tokens): Primitive-Verhalten + isoliertes Layout-Token-Paket (#60, Review R1) (#74)
    - d335137 fix(layout): Home rendert Navigation/Footer nur noch via LayoutShell (#60, Review R1) (#76)
    - 9c75478 docs(agents): Codegraph als erstes Werkzeug bei Code-Fragen verankern (#75)
    - e2d40e5 fix(signals): GET /api/signals uses active_signal RPC instead of st_x/st_y select
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage/.worktrees/t_fe9cd670
- Branch: `HEAD` · HEAD `d9eaa5b` · Basis `39d9500`
- letzter Commit: 2026-10-29T15:09:35+01:00 — Integration: #15 Extension-Paket (Detailrouten, q-Param-Contract, Upload-Statusbanner) (#77)
- **Commits über der Baseline: 103** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  232 files changed, 24370 insertions(+), 2854 deletions(-)
    - d9eaa5b Integration: #15 Extension-Paket (Detailrouten, q-Param-Contract, Upload-Statusbanner) (#77)
    - e04ff8a test: fix inherited TypeScript diagnostics in signals/live-pins specs (issues #58/#71) (#78)
    - f43ae66 fix(design-tokens): Primitive-Verhalten + isoliertes Layout-Token-Paket (#60, Review R1) (#74)
    - d335137 fix(layout): Home rendert Navigation/Footer nur noch via LayoutShell (#60, Review R1) (#76)
    - 9c75478 docs(agents): Codegraph als erstes Werkzeug bei Code-Fragen verankern (#75)
    - e2d40e5 fix(signals): GET /api/signals uses active_signal RPC instead of st_x/st_y select
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)
    - 30386db fix(signals): REASON_LABELS als lokales Konstante, nicht als Route-Export

## [portal] /Volumes/External Disk/Users/thomas/.hermes/kanban/workspaces/t_97d6fc6c/portal-layout
- Branch: `HEAD` · HEAD `a8a28df` · Basis `39d9500`
- letzter Commit: 2026-10-29T15:08:26+01:00 — merge: origin/main in fix/design-tokens-layout-60
- **Commits über der Baseline: 102** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  225 files changed, 23340 insertions(+), 2724 deletions(-)
    - a8a28df merge: origin/main in fix/design-tokens-layout-60
    - d335137 fix(layout): Home rendert Navigation/Footer nur noch via LayoutShell (#60, Review R1) (#76)
    - 9c75478 docs(agents): Codegraph als erstes Werkzeug bei Code-Fragen verankern (#75)
    - 30e25a1 fix(design-tokens): Primitive-Verhalten + isoliertes Layout-Token-Paket (#60, Review R1)
    - e2d40e5 fix(signals): GET /api/signals uses active_signal RPC instead of st_x/st_y select
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)
    - 30386db fix(signals): REASON_LABELS als lokales Konstante, nicht als Route-Export
    - 13b5f83 Merge branch 'main' into pr-22

## [portal] /Volumes/External Disk/Users/thomas/.hermes/kanban/workspaces/t_70a32347/wt-60-fix
- Branch: `fix/home-nav-footer-60` · HEAD `47887ac` · Basis `39d9500`
- letzter Commit: 2026-10-29T12:43:27+01:00 — fix(layout): Home rendert Navigation/Footer nur noch via LayoutShell (#60)
- **Commits über der Baseline: 100** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  225 files changed, 23327 insertions(+), 2724 deletions(-)
    - 47887ac fix(layout): Home rendert Navigation/Footer nur noch via LayoutShell (#60)
    - 30e25a1 fix(design-tokens): Primitive-Verhalten + isoliertes Layout-Token-Paket (#60, Review R1)
    - e2d40e5 fix(signals): GET /api/signals uses active_signal RPC instead of st_x/st_y select
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)
    - 30386db fix(signals): REASON_LABELS als lokales Konstante, nicht als Route-Export
    - 13b5f83 Merge branch 'main' into pr-22
    - 3916703 feat(messenger): Realtime-Auth über Keycloak-Access-Token (Supabase Third-Party Auth) (#46)
    - f0650be Merge pull request #44 from Code-TT/fix/dockerfile-standalone

## [portal] /Volumes/External Disk/Users/thomas/.hermes/kanban/workspaces/t_e9c7eb9b/wt
- Branch: `integration/extension-15-t_e9c7eb9b` · HEAD `367a867` · Basis `39d9500`
- letzter Commit: 2026-10-29T14:33:13+01:00 — security(harness): remove operational ext-detail harness from integration scope
- **Commits über der Baseline: 100** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  205 files changed, 22416 insertions(+), 2276 deletions(-)
    - 367a867 security(harness): remove operational ext-detail harness from integration scope
    - c848aca integration: #15 Extension-Paket (Detailrouten, q-Param-Contract, Upload-Cancel-/Retry-Statusbanner)
    - e2d40e5 fix(signals): GET /api/signals uses active_signal RPC instead of st_x/st_y select
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)
    - 30386db fix(signals): REASON_LABELS als lokales Konstante, nicht als Route-Export
    - 13b5f83 Merge branch 'main' into pr-22
    - 3916703 feat(messenger): Realtime-Auth über Keycloak-Access-Token (Supabase Third-Party Auth) (#46)
    - f0650be Merge pull request #44 from Code-TT/fix/dockerfile-standalone

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage-wt-codegraph-doc
- Branch: `docs/agents-md-codegraph` · HEAD `21b37ac` · Basis `39d9500`
- letzter Commit: 2026-10-29T12:18:36+01:00 — docs(agents): Codegraph als erstes Werkzeug bei Code-Fragen verankern
- **Commits über der Baseline: 99** · ungepusht: 1 · uncommittet: 0 Dateien
- Umfang:  199 files changed, 21582 insertions(+), 2276 deletions(-)
    - 21b37ac docs(agents): Codegraph als erstes Werkzeug bei Code-Fragen verankern
    - e2d40e5 fix(signals): GET /api/signals uses active_signal RPC instead of st_x/st_y select
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)
    - 30386db fix(signals): REASON_LABELS als lokales Konstante, nicht als Route-Export
    - 13b5f83 Merge branch 'main' into pr-22
    - 3916703 feat(messenger): Realtime-Auth über Keycloak-Access-Token (Supabase Third-Party Auth) (#46)
    - f0650be Merge pull request #44 from Code-TT/fix/dockerfile-standalone
    - ba36a77 fix(docker): Standalone-Server starten statt 'next start'

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage/.worktrees/t_fece09b2
- Branch: `fix/test-typecheck-58-71-t_fece09b2` · HEAD `b37de88` · Basis `39d9500`
- letzter Commit: 2026-10-29T14:30:22+01:00 — test: fix inherited TypeScript diagnostics in signals/live-pins specs (issues #58/#71)
- **Commits über der Baseline: 99** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  200 files changed, 21752 insertions(+), 2406 deletions(-)
    - b37de88 test: fix inherited TypeScript diagnostics in signals/live-pins specs (issues #58/#71)
    - e2d40e5 fix(signals): GET /api/signals uses active_signal RPC instead of st_x/st_y select
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)
    - 30386db fix(signals): REASON_LABELS als lokales Konstante, nicht als Route-Export
    - 13b5f83 Merge branch 'main' into pr-22
    - 3916703 feat(messenger): Realtime-Auth über Keycloak-Access-Token (Supabase Third-Party Auth) (#46)
    - f0650be Merge pull request #44 from Code-TT/fix/dockerfile-standalone
    - ba36a77 fix(docker): Standalone-Server starten statt 'next start'

## [portal] /Volumes/External Disk/Users/thomas/.hermes/kanban/workspaces/t_48399a34/wt
- Branch: `fix/signals-admin-queue-t_48399a34` · HEAD `0f76035` · Basis `39d9500`
- letzter Commit: 2026-10-29T12:36:43+01:00 — feat(admin): bind Signals-Moderation queue into route and menu (#70)
- **Commits über der Baseline: 98** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  200 files changed, 21426 insertions(+), 2268 deletions(-)
    - 0f76035 feat(admin): bind Signals-Moderation queue into route and menu (#70)
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)
    - 30386db fix(signals): REASON_LABELS als lokales Konstante, nicht als Route-Export
    - 13b5f83 Merge branch 'main' into pr-22
    - 3916703 feat(messenger): Realtime-Auth über Keycloak-Access-Token (Supabase Third-Party Auth) (#46)
    - f0650be Merge pull request #44 from Code-TT/fix/dockerfile-standalone
    - ba36a77 fix(docker): Standalone-Server starten statt 'next start'
    - a6f7a5f Merge pull request #43 from Code-TT/chore/dockerfile-deploy

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage-wt-t_506ee203
- Branch: `fix/signals-insert-policies-t_506ee203` · HEAD `3f6d137` · Basis `39d9500`
- letzter Commit: 2026-10-29T06:52:37+01:00 — fix(security): signals/signal_reports — remove authenticated INSERT grant+policy (Issue #58 F1)
- **Commits über der Baseline: 98** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  188 files changed, 20080 insertions(+), 2254 deletions(-)
    - 3f6d137 fix(security): signals/signal_reports — remove authenticated INSERT grant+policy (Issue #58 F1)
    - 746e8f1 backup: haertetes DEV-Backup-Script (Credentials nur env/geschuetzte Datei, Ref-Assert ajbzqvderhzmrknwgryq, TLS verify-full mit Supabase-Prod-CA, Umask 077) + offizielle CA
    - d57c1d0 test: add regression test for location category 404 behavior
    - 1f552a0 fix: return 404 for unknown location categories instead of empty 200
    - 4b3c2b8 fix: handle location_categories array in event location links
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)
    - 30386db fix(signals): REASON_LABELS als lokales Konstante, nicht als Route-Export
    - 13b5f83 Merge branch 'main' into pr-22
    - 3916703 feat(messenger): Realtime-Auth über Keycloak-Access-Token (Supabase Third-Party Auth) (#46)
    - f0650be Merge pull request #44 from Code-TT/fix/dockerfile-standalone
    - ba36a77 fix(docker): Standalone-Server starten statt 'next start'
    - a6f7a5f Merge pull request #43 from Code-TT/chore/dockerfile-deploy

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage
- Branch: `HEAD` · HEAD `5e673f3` · Basis `39d9500`
- letzter Commit: 2026-10-29T08:30:05+01:00 — fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
- **Commits über der Baseline: 97** · ungepusht: 0 · uncommittet: 1 Dateien
- Umfang:  198 files changed, 21403 insertions(+), 2267 deletions(-)
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)
    - 30386db fix(signals): REASON_LABELS als lokales Konstante, nicht als Route-Export
    - 13b5f83 Merge branch 'main' into pr-22
    - 3916703 feat(messenger): Realtime-Auth über Keycloak-Access-Token (Supabase Third-Party Auth) (#46)
    - f0650be Merge pull request #44 from Code-TT/fix/dockerfile-standalone
    - ba36a77 fix(docker): Standalone-Server starten statt 'next start'
    - a6f7a5f Merge pull request #43 from Code-TT/chore/dockerfile-deploy
    - 4cd338a build(docker): Dockerfile + .dockerignore - deterministischer Coolify-Build
    - (uncommittet) ?? .worktrees/

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage-wt-t_d2169c36
- Branch: `fix/signals-upsert-hardening-t_d2169c36` · HEAD `e3ff93a` · Basis `39d9500`
- letzter Commit: 2026-10-29T07:21:04+01:00 — fix(security): qualify created_at in carry-over SELECT (PL/pgSQL OUT-variable ambiguity, found in DEV apply)
- **Commits über der Baseline: 97** · ungepusht: 0 · uncommittet: 1 Dateien
- Umfang:  191 files changed, 20517 insertions(+), 2264 deletions(-)
    - e3ff93a fix(security): qualify created_at in carry-over SELECT (PL/pgSQL OUT-variable ambiguity, found in DEV apply)
    - cc74d91 fix(security): upsert_signal — hidden-state carry-over + per-user advisory xact lock (Issue #58 F4/F5)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)
    - 30386db fix(signals): REASON_LABELS als lokales Konstante, nicht als Route-Export
    - 13b5f83 Merge branch 'main' into pr-22
    - 3916703 feat(messenger): Realtime-Auth über Keycloak-Access-Token (Supabase Third-Party Auth) (#46)
    - f0650be Merge pull request #44 from Code-TT/fix/dockerfile-standalone
    - ba36a77 fix(docker): Standalone-Server starten statt 'next start'
    - a6f7a5f Merge pull request #43 from Code-TT/chore/dockerfile-deploy
    - 4cd338a build(docker): Dockerfile + .dockerignore - deterministischer Coolify-Build
    - (uncommittet) ?? .hermes-fn-diff.txt

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/wt-hermes-merge
- Branch: `main` · HEAD `5e673f3` · Basis `39d9500`
- letzter Commit: 2026-10-29T08:30:05+01:00 — fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
- **Commits über der Baseline: 97** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  198 files changed, 21403 insertions(+), 2267 deletions(-)
    - 5e673f3 fix(security): Signals — Insert-Lockdown, SELECT/Realtime-Vertrag, Rate-Limit, Upsert-Hardening (#58 F1–F6) (#69)
    - 0fcdbb4 feat(db): merge_location() als einziger Weg zum Zusammenführen von Location-Dubletten (#68)
    - 3627233 fix(breadcrumb): Kategoriename statt Slug, kein ID-Suffix im letzten Krümel (#66)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)
    - 30386db fix(signals): REASON_LABELS als lokales Konstante, nicht als Route-Export
    - 13b5f83 Merge branch 'main' into pr-22
    - 3916703 feat(messenger): Realtime-Auth über Keycloak-Access-Token (Supabase Third-Party Auth) (#46)
    - f0650be Merge pull request #44 from Code-TT/fix/dockerfile-standalone
    - ba36a77 fix(docker): Standalone-Server starten statt 'next start'
    - a6f7a5f Merge pull request #43 from Code-TT/chore/dockerfile-deploy
    - 4cd338a build(docker): Dockerfile + .dockerignore - deterministischer Coolify-Build

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage-wt-t_cd58d2e2
- Branch: `fix/signals-select-realtime-contract-t_cd58d2e2` · HEAD `6b18679` · Basis `39d9500`
- letzter Commit: 2026-10-29T07:10:44+01:00 — fix(signals): close F2/F3 SELECT/Realtime exposure vs privacy contract (t_cd58d2e2)
- **Commits über der Baseline: 95** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  186 files changed, 19847 insertions(+), 2256 deletions(-)
    - 6b18679 fix(signals): close F2/F3 SELECT/Realtime exposure vs privacy contract (t_cd58d2e2)
    - 67c7294 fix(qa): #59 Event-Location-Link + #50 Location-Breadcrumb JSON-LD (#65)
    - fca6b2f fix(events): geom-Trigger für events + Backfill der Bestandsdaten (#62)
    - 6274b1d fix(nearby): nearby_events nutzt locations.geom als Fallback (#61)
    - a34d7f0 Merge pull request #22 from Code-TT/recovery/signals-nearby-parity-t_a48f342b
    - 4d8fa90 fix(build): Service-Key erst zur Laufzeit lesen — next build scheitert sonst ohne Secret (#57)
    - 30386db fix(signals): REASON_LABELS als lokales Konstante, nicht als Route-Export
    - 13b5f83 Merge branch 'main' into pr-22
    - 3916703 feat(messenger): Realtime-Auth über Keycloak-Access-Token (Supabase Third-Party Auth) (#46)
    - f0650be Merge pull request #44 from Code-TT/fix/dockerfile-standalone
    - ba36a77 fix(docker): Standalone-Server starten statt 'next start'
    - a6f7a5f Merge pull request #43 from Code-TT/chore/dockerfile-deploy
    - 4cd338a build(docker): Dockerfile + .dockerignore - deterministischer Coolify-Build
    - 7f4a650 Merge pull request #42 from Code-TT/chore/nixpacks-config
    - 76cf331 chore(build): nixpacks.toml - npm-Install und Start festnageln

## [portal] /Volumes/External Disk/Users/thomas/.local/share/kilo/worktree-pool/002-eventspage-f5c61679ca08/jealous-printer
- Branch: `HEAD` · HEAD `001ba89` · Basis `39d9500`
- letzter Commit: 2026-10-28T22:43:26+01:00 — Merge pull request #40 from Code-TT/chore/orphan-scan-script
- **Commits über der Baseline: 79** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  157 files changed, 15744 insertions(+), 2188 deletions(-)
    - 001ba89 Merge pull request #40 from Code-TT/chore/orphan-scan-script
    - b640ace chore(scripts): scan-orphans.ts - Read-only Bestandsaufnahme verwaister Storage-Objekte
    - 6b93171 Merge pull request #39 from Code-TT/fix/package-manager-npm
    - 673ee05 fix(build): packageManager-Feld entfernen - Nixpacks erzwang pnpm ohne Lockfile
    - c649156 Merge pull request #38 from Code-TT/fix/admin-routes-no-hardcoded-key
    - 5c81aa3 fix(security): Service-Role-Key aus dem Quellcode entfernen, Admin-Routen absichern
    - e3548f6 fix(extension): Album-Upload nutzt die Rollen-Leiter und den richtigen Bucket
    - 0927865 Merge pull request #37 from Code-TT/feat/extension-consolidation
    - 0338f14 feat(extension): Content-Hash-Dedupe, search-Parameter, Upload-Abbruch, fbcdn-Host (aus qa/extension-integrated)
    - 1c17bfb Merge pull request #36 from Code-TT/fix/migrations-views-repair
    - 6a5ef5e fix(migrations): defekte Views repararieren und Reihenfolge korrigieren
    - 5673029 Merge pull request #35 from Code-TT/feat/image-pipeline-roles-loader
    - 2cacac2 fix(images): Polaroid beschneidet das Event-Bild nicht mehr (contain statt cover)
    - 1f0b37b fix(images): Hero beschneidet keine Banner mehr — Bild vollstaendig auf unscharfem Hintergrund
    - 1c3cb0e feat(scripts): Querformat-Bilder als Banner klassifizieren (Crawler-Altlast)

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/recovery-worktrees/event-detail-issue-6
- Branch: `fix/migrations-views-repair` · HEAD `6a5ef5e` · Basis `39d9500`
- letzter Commit: 2026-10-28T20:05:20+01:00 — fix(migrations): defekte Views repararieren und Reihenfolge korrigieren
- **Commits über der Baseline: 69** · ungepusht: 0 · uncommittet: 1 Dateien
- Umfang:  153 files changed, 15549 insertions(+), 2118 deletions(-)
    - 6a5ef5e fix(migrations): defekte Views repararieren und Reihenfolge korrigieren
    - 5673029 Merge pull request #35 from Code-TT/feat/image-pipeline-roles-loader
    - 2cacac2 fix(images): Polaroid beschneidet das Event-Bild nicht mehr (contain statt cover)
    - 1f0b37b fix(images): Hero beschneidet keine Banner mehr — Bild vollstaendig auf unscharfem Hintergrund
    - 1c3cb0e feat(scripts): Querformat-Bilder als Banner klassifizieren (Crawler-Altlast)
    - b3cf5ea feat(images): Hero zeigt Hochformat-Master (Flyer) vollstaendig auf unscharfem Hintergrund statt 16:9-Crop
    - ab828f1 feat(images): Fallback auf Master, wenn eine Leiterstufe fehlt (kleinere Master)
    - 90ff29c fix(images): Admin-Vorschau baut Varianten-URLs ohne -original, Mirror legt WebP-Master statt -original an
    - 406a6cd feat(images): Location-Detail und LocationCard nutzen Slots (Banner 21:9, Foto, Logo)
    - f9fdab1 fix(migration): 45s-Timeout auf alle Storage-Requests (ein haengender Download blockierte den Lauf)
    - 6bbeeb0 fix(migration): Altbestand-Master auch -banner/-logo/-photo-N/-hero_N/-banner_N erkennen
    - db7faab fix(images): Hero nutzt 16:9-Crop statt Breitenstufe, Listenkarten (CityEventCard) auf card-Slot
    - e431bf3 feat(images): eigener Loader aktiv, Hero/Karte/Polaroid nutzen Slots
    - 6c7f5bf fix(scripts): Rehost-Paginierung ohne Offset (aktualisierte Zeilen fielen sonst aus dem Filter)
    - 20a4b52 feat(images): Werkzeuge fuer Umgebung (Bucket-Spiegelung, externe Bilder einholen)
    - (uncommittet) D ".design-vorlage/profil-vervollsta\314\210ndigen.png"

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage-hygiene
- Branch: `feat/image-pipeline-roles-loader` · HEAD `2cacac2` · Basis `39d9500`
- letzter Commit: 2026-10-28T09:04:11+01:00 — fix(images): Polaroid beschneidet das Event-Bild nicht mehr (contain statt cover)
- **Commits über der Baseline: 67** · ungepusht: 0 · uncommittet: 3 Dateien
- Umfang:  153 files changed, 15891 insertions(+), 2101 deletions(-)
    - 2cacac2 fix(images): Polaroid beschneidet das Event-Bild nicht mehr (contain statt cover)
    - 1f0b37b fix(images): Hero beschneidet keine Banner mehr — Bild vollstaendig auf unscharfem Hintergrund
    - 1c3cb0e feat(scripts): Querformat-Bilder als Banner klassifizieren (Crawler-Altlast)
    - b3cf5ea feat(images): Hero zeigt Hochformat-Master (Flyer) vollstaendig auf unscharfem Hintergrund statt 16:9-Crop
    - ab828f1 feat(images): Fallback auf Master, wenn eine Leiterstufe fehlt (kleinere Master)
    - 90ff29c fix(images): Admin-Vorschau baut Varianten-URLs ohne -original, Mirror legt WebP-Master statt -original an
    - 406a6cd feat(images): Location-Detail und LocationCard nutzen Slots (Banner 21:9, Foto, Logo)
    - f9fdab1 fix(migration): 45s-Timeout auf alle Storage-Requests (ein haengender Download blockierte den Lauf)
    - 6bbeeb0 fix(migration): Altbestand-Master auch -banner/-logo/-photo-N/-hero_N/-banner_N erkennen
    - db7faab fix(images): Hero nutzt 16:9-Crop statt Breitenstufe, Listenkarten (CityEventCard) auf card-Slot
    - e431bf3 feat(images): eigener Loader aktiv, Hero/Karte/Polaroid nutzen Slots
    - 6c7f5bf fix(scripts): Rehost-Paginierung ohne Offset (aktualisierte Zeilen fielen sonst aus dem Filter)
    - 20a4b52 feat(images): Werkzeuge fuer Umgebung (Bucket-Spiegelung, externe Bilder einholen)
    - e1cb738 fix(images): Migrationsskript idempotent (Leiterstufen im Stem erfassen), WebP-Umwandlung fuer JPG-Master, cache-control ohne doppeltes Praefix
    - 7fc7c76 feat(images): --apply fuer die Migration (Master umbenennen, Leiter erzeugen, DB-URLs umschreiben) + MIGRATION_URL/KEY-Override
    - (uncommittet) ?? migration-report-log.jsonl
    - (uncommittet) ?? migration-report.json
    - (uncommittet) ?? migration-report.md

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage-wt-t_5fbc97b8
- Branch: `qa/profile-regression-t_5fbc97b8` · HEAD `f55d8de` · Basis `39d9500`
- letzter Commit: 2026-10-29T13:27:19+01:00 — merge: feat/follow-ui-wiring-t_94b0b061 in QA-Basis
- **Commits über der Baseline: 37** · ungepusht: 2 · uncommittet: 0 Dateien
- Umfang:  89 files changed, 8024 insertions(+), 1145 deletions(-)
    - f55d8de merge: feat/follow-ui-wiring-t_94b0b061 in QA-Basis
    - 6fdb31d merge: fix/user-profile-uuid-regex-t_04511b36 in QA-Basis
    - d59742a fix(follows): FollowBlock liest Event-Namen auf Top-Level (data?.name) — Helper-Zeile rendered jetzt auf Occurrences (t_94b0b061)
    - e219026 feat(follows): Follow-UI auf Detailseiten verdrahten (t_94b0b061)
    - 6725151 fix(user-profile): UUID-Regex fehlte eine Segment-Gruppe (friends+images)
    - 8cbdb8a fix(follows): UUID-Regex fehlte eine Gruppe
    - 09a98ad fix(db): Migration fuer User-Profil-Assets rekonstruiert
    - 103b4f6 recovery(parity-2): Merkliste, Follows-API und UserProfileModal
    - 2058402 Merge pull request #19 from Code-TT/fix/production-build-green
    - 8eb6c26 fix(deps): Next.js 15.3.0-canary.1 auf 15.5.28 aktualisieren
    - 413f660 fix(deps): Tiptap-Versionskonflikt aufloesen (2.27.2 + 3.32.0 parallel)
    - c240728 merge(location): Location-Konfliktauflösung in den Build-Fix integrieren
    - 46d6d11 fix(build): Production-Build-Typfehler beheben (signals-ParserError + Tailwind-Source-Globs)
    - 4f4f4ad fix(locations): Banner ausschliesslich aus banner_url (Issue #12 Acceptance)
    - c6fbe0e fix(locations): Merge-Konflikt Issue #12 aufloesen (Banner/Logo/Bild-Trennung, geo-utils, package-lock)

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage-wt-t_5c9697c9
- Branch: `fix/user-images-int-id-t_5c9697c9` · HEAD `9ef5096` · Basis `39d9500`
- letzter Commit: 2026-10-29T12:46:26+01:00 — fix(user-profile): user_images.id ist integer - DELETE/PATCH validierten UUID
- **Commits über der Baseline: 34** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  85 files changed, 7941 insertions(+), 1134 deletions(-)
    - 9ef5096 fix(user-profile): user_images.id ist integer - DELETE/PATCH validierten UUID
    - 6725151 fix(user-profile): UUID-Regex fehlte eine Segment-Gruppe (friends+images)
    - 8cbdb8a fix(follows): UUID-Regex fehlte eine Gruppe
    - 09a98ad fix(db): Migration fuer User-Profil-Assets rekonstruiert
    - 103b4f6 recovery(parity-2): Merkliste, Follows-API und UserProfileModal
    - 2058402 Merge pull request #19 from Code-TT/fix/production-build-green
    - 8eb6c26 fix(deps): Next.js 15.3.0-canary.1 auf 15.5.28 aktualisieren
    - 413f660 fix(deps): Tiptap-Versionskonflikt aufloesen (2.27.2 + 3.32.0 parallel)
    - c240728 merge(location): Location-Konfliktauflösung in den Build-Fix integrieren
    - 46d6d11 fix(build): Production-Build-Typfehler beheben (signals-ParserError + Tailwind-Source-Globs)
    - 4f4f4ad fix(locations): Banner ausschliesslich aus banner_url (Issue #12 Acceptance)
    - c6fbe0e fix(locations): Merge-Konflikt Issue #12 aufloesen (Banner/Logo/Bild-Trennung, geo-utils, package-lock)
    - c98e969 Merge pull request #18 from Code-TT/fix/remove-nfc-duplicate-design-vorlage
    - d924afa chore(repo): doppelten NFC/NFD-Indexeintrag fuer .design-vorlage/profil-vervollstaendigen.png entfernen
    - 05fa4ff chore(migrations): RUN_THIS_add_banner_url_to_cities.sql entfernen (Karte t_87ea62b5)

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage-wt-t_94b0b061
- Branch: `feat/follow-ui-wiring-t_94b0b061` · HEAD `d59742a` · Basis `39d9500`
- letzter Commit: 2026-10-29T12:55:43+01:00 — fix(follows): FollowBlock liest Event-Namen auf Top-Level (data?.name) — Helper-Zeile rendered jetzt auf Occurrences (t_94b0b061)
- **Commits über der Baseline: 34** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  89 files changed, 8024 insertions(+), 1145 deletions(-)
    - d59742a fix(follows): FollowBlock liest Event-Namen auf Top-Level (data?.name) — Helper-Zeile rendered jetzt auf Occurrences (t_94b0b061)
    - e219026 feat(follows): Follow-UI auf Detailseiten verdrahten (t_94b0b061)
    - 8cbdb8a fix(follows): UUID-Regex fehlte eine Gruppe
    - 09a98ad fix(db): Migration fuer User-Profil-Assets rekonstruiert
    - 103b4f6 recovery(parity-2): Merkliste, Follows-API und UserProfileModal
    - 2058402 Merge pull request #19 from Code-TT/fix/production-build-green
    - 8eb6c26 fix(deps): Next.js 15.3.0-canary.1 auf 15.5.28 aktualisieren
    - 413f660 fix(deps): Tiptap-Versionskonflikt aufloesen (2.27.2 + 3.32.0 parallel)
    - c240728 merge(location): Location-Konfliktauflösung in den Build-Fix integrieren
    - 46d6d11 fix(build): Production-Build-Typfehler beheben (signals-ParserError + Tailwind-Source-Globs)
    - 4f4f4ad fix(locations): Banner ausschliesslich aus banner_url (Issue #12 Acceptance)
    - c6fbe0e fix(locations): Merge-Konflikt Issue #12 aufloesen (Banner/Logo/Bild-Trennung, geo-utils, package-lock)
    - c98e969 Merge pull request #18 from Code-TT/fix/remove-nfc-duplicate-design-vorlage
    - d924afa chore(repo): doppelten NFC/NFD-Indexeintrag fuer .design-vorlage/profil-vervollstaendigen.png entfernen
    - 05fa4ff chore(migrations): RUN_THIS_add_banner_url_to_cities.sql entfernen (Karte t_87ea62b5)

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage-wt-t_04511b36
- Branch: `fix/user-profile-uuid-regex-t_04511b36` · HEAD `6725151` · Basis `39d9500`
- letzter Commit: 2026-10-29T11:44:31+01:00 — fix(user-profile): UUID-Regex fehlte eine Segment-Gruppe (friends+images)
- **Commits über der Baseline: 33** · ungepusht: 0 · uncommittet: 1 Dateien
- Umfang:  85 files changed, 7936 insertions(+), 1134 deletions(-)
    - 6725151 fix(user-profile): UUID-Regex fehlte eine Segment-Gruppe (friends+images)
    - 8cbdb8a fix(follows): UUID-Regex fehlte eine Gruppe
    - 09a98ad fix(db): Migration fuer User-Profil-Assets rekonstruiert
    - 103b4f6 recovery(parity-2): Merkliste, Follows-API und UserProfileModal
    - 2058402 Merge pull request #19 from Code-TT/fix/production-build-green
    - 8eb6c26 fix(deps): Next.js 15.3.0-canary.1 auf 15.5.28 aktualisieren
    - 413f660 fix(deps): Tiptap-Versionskonflikt aufloesen (2.27.2 + 3.32.0 parallel)
    - c240728 merge(location): Location-Konfliktauflösung in den Build-Fix integrieren
    - 46d6d11 fix(build): Production-Build-Typfehler beheben (signals-ParserError + Tailwind-Source-Globs)
    - 4f4f4ad fix(locations): Banner ausschliesslich aus banner_url (Issue #12 Acceptance)
    - c6fbe0e fix(locations): Merge-Konflikt Issue #12 aufloesen (Banner/Logo/Bild-Trennung, geo-utils, package-lock)
    - c98e969 Merge pull request #18 from Code-TT/fix/remove-nfc-duplicate-design-vorlage
    - d924afa chore(repo): doppelten NFC/NFD-Indexeintrag fuer .design-vorlage/profil-vervollstaendigen.png entfernen
    - 05fa4ff chore(migrations): RUN_THIS_add_banner_url_to_cities.sql entfernen (Karte t_87ea62b5)
    - 821b037 chore(migrations): Bootstrap-Voraussetzungen sichern (PostGIS-Schema, search_path, slug-Spalten)
    - (uncommittet) ?? mint_tokens_tmp.js

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage-wt-t_7b8c92fd
- Branch: `qa/profile-follows-t_7b8c92fd` · HEAD `8cbdb8a` · Basis `39d9500`
- letzter Commit: 2026-10-22T19:48:59+02:00 — fix(follows): UUID-Regex fehlte eine Gruppe
- **Commits über der Baseline: 32** · ungepusht: 0 · uncommittet: 3 Dateien
- Umfang:  85 files changed, 7936 insertions(+), 1134 deletions(-)
    - 8cbdb8a fix(follows): UUID-Regex fehlte eine Gruppe
    - 09a98ad fix(db): Migration fuer User-Profil-Assets rekonstruiert
    - 103b4f6 recovery(parity-2): Merkliste, Follows-API und UserProfileModal
    - 2058402 Merge pull request #19 from Code-TT/fix/production-build-green
    - 8eb6c26 fix(deps): Next.js 15.3.0-canary.1 auf 15.5.28 aktualisieren
    - 413f660 fix(deps): Tiptap-Versionskonflikt aufloesen (2.27.2 + 3.32.0 parallel)
    - c240728 merge(location): Location-Konfliktauflösung in den Build-Fix integrieren
    - 46d6d11 fix(build): Production-Build-Typfehler beheben (signals-ParserError + Tailwind-Source-Globs)
    - 4f4f4ad fix(locations): Banner ausschliesslich aus banner_url (Issue #12 Acceptance)
    - c6fbe0e fix(locations): Merge-Konflikt Issue #12 aufloesen (Banner/Logo/Bild-Trennung, geo-utils, package-lock)
    - c98e969 Merge pull request #18 from Code-TT/fix/remove-nfc-duplicate-design-vorlage
    - d924afa chore(repo): doppelten NFC/NFD-Indexeintrag fuer .design-vorlage/profil-vervollstaendigen.png entfernen
    - 05fa4ff chore(migrations): RUN_THIS_add_banner_url_to_cities.sql entfernen (Karte t_87ea62b5)
    - 821b037 chore(migrations): Bootstrap-Voraussetzungen sichern (PostGIS-Schema, search_path, slug-Spalten)
    - 326380b chore(gitignore): generierte .codegraph-Analyse-DB ignorieren (Karte t_cf11324f)
    - (uncommittet) D ".design-vorlage/profil-vervollsta\314\210ndigen.png"
    - (uncommittet) ?? .next-stale-qa/
    - (uncommittet) ?? .qa-mint-tokens.js

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage-t_a48f342b
- Branch: `recovery/signals-nearby-parity-t_a48f342b` · HEAD `23fd752` · Basis `39d9500`
- letzter Commit: 2026-10-15T02:34:50+02:00 — recovery(paritiy-1): restore signals/nearby/report routes from Hermes snapshot (t_a48f342b)
- **Commits über der Baseline: 12** · ungepusht: 0 · uncommittet: 1 Dateien
- Umfang:  51 files changed, 7422 insertions(+), 2 deletions(-)
    - 23fd752 recovery(paritiy-1): restore signals/nearby/report routes from Hermes snapshot (t_a48f342b)
    - 326380b chore(gitignore): generierte .codegraph-Analyse-DB ignorieren (Karte t_cf11324f)
    - b1cdcc5 Revert "fix(extension): search query param, album error display, upload cancel+retry, CDN host permission"
    - 3f64e36 fix(extension): search query param, album error display, upload cancel+retry, CDN host permission
    - 996a74b feat(extension): /api/extension routes + event_images_bucket migration (M1 rebuild)
    - a9fbe4d M0: Rebuild MV3 browser extension (client) from scratch
    - 7a8e809 chore(vercel): use npm install --legacy-peer-deps (pnpm registry bug on build image)
    - bbfaf68 chore: pin pnpm@10.33.2 via packageManager for Vercel build
    - 351e81e chore(vercel): force pnpm install/build to resolve dependency tree
    - bd83bd4 chore: trigger preview deploy with linked git author
    - 9720e26 fix: correct geo-utils import path to absolute @/lib/geo-utils
    - 317bf1d fix: add missing geo-utils module for signals API build
    - (uncommittet) M package-lock.json

## [portal] /Volumes/External Disk/Users/thomas/.hermes/kanban/workspaces/t_40352a89/portal
- Branch: `fix/extension-popup-qa-t_153d0509` · HEAD `ddc0c7e` · Basis `39d9500`
- letzter Commit: 2026-10-14T19:21:49+02:00 — fix(extension): search query param, album error display, upload cancel+retry, CDN host permission
- **Commits über der Baseline: 10** · ungepusht: 4 · uncommittet: 0 Dateien
- Umfang:  37 files changed, 4487 insertions(+), 2 deletions(-)
    - ddc0c7e fix(extension): search query param, album error display, upload cancel+retry, CDN host permission
    - 2550020 test(extension): cover isolated album upload contract and dedupe gap
    - f9062e5 feat(extension): /api/extension routes + event_images_bucket migration (M1 rebuild)
    - c1d144c M0: Rebuild MV3 browser extension (client) from scratch
    - 7a8e809 chore(vercel): use npm install --legacy-peer-deps (pnpm registry bug on build image)
    - bbfaf68 chore: pin pnpm@10.33.2 via packageManager for Vercel build
    - 351e81e chore(vercel): force pnpm install/build to resolve dependency tree
    - bd83bd4 chore: trigger preview deploy with linked git author
    - 9720e26 fix: correct geo-utils import path to absolute @/lib/geo-utils
    - 317bf1d fix: add missing geo-utils module for signals API build

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/recovery-worktrees/crawl-proposals-issue-7
- Branch: `recovery/crawl-proposals-issue-7` · HEAD `0ce3cf7` · Basis `39d9500`
- letzter Commit: 2026-10-13T23:16:21+02:00 — fix(admin): Proposal-Review – Parent-Felder und Bildbearbeitung
- **Commits über der Baseline: 8** · ungepusht: 8 · uncommittet: 8 Dateien
- Umfang:  6 files changed, 1029 insertions(+), 77 deletions(-)
    - 0ce3cf7 fix(admin): Proposal-Review – Parent-Felder und Bildbearbeitung
    - dfb1b16 fix: restore proposal saved-image previews and review image edits
    - 3946230 fix(crawler): preserve multiline review text and guard long-text source
    - 5f9d36d fix(crawler): avoid premature approval for new series and expose failures
    - abb0b93 feat(crawler): new series UI with name input, inherit-category checkbox, apply-new-series flow
    - ff9aa70 feat(crawler): add info_text/preis_info edit fields, langtext toggle, full-title parent search
    - fc002d4 fix(crawler): restore parent summary in all-data review
    - 270a475 fix(crawler): send selected parent in child apply
    - (uncommittet) M package-lock.json
    - (uncommittet)  M package.json
    - (uncommittet) ?? .next-stale-4/
    - (uncommittet) ?? .next-stale-5/
    - (uncommittet) ?? .next-stale-6/
    - (uncommittet) ?? node_modules-new/
    - (uncommittet) ?? node_modules-old-3/
    - (uncommittet) ?? output/

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/recovery-worktrees/location-image-issue-12
- Branch: `fix/location-image-issue-12` · HEAD `07cb1ca` · Basis `39d9500`
- letzter Commit: 2026-10-22T09:27:49+02:00 — chore(vercel): vercel.json ergaenzen (fehlte auf diesem Branch -> npm install ERESOLVE)
- **Commits über der Baseline: 7** · ungepusht: 0 · uncommittet: 2 Dateien
- Umfang:  27 files changed, 1221 insertions(+), 475 deletions(-)
    - 07cb1ca chore(vercel): vercel.json ergaenzen (fehlte auf diesem Branch -> npm install ERESOLVE)
    - 3f60c9a fix(build): resolve all remaining tsc errors blocking next build
    - 642fe80 fix(build): add missing geo-utils and fix signal-route type errors
    - 22e62e2 fix(admin): MUI-Icon-Subpfade auf ESM-Build auflösen — behebt "Element type is invalid" (#12)
    - 1e8afef fix(upload): Bild-/Logo-Upload überschreibt nicht mehr banner_url (Issue #12)
    - d94120f fix(location-detail): Banner-Fallback auf image_url wiederherstellen, Logo nie als Banner (Issue #12)
    - 181e053 fix(location-detail): Banner nur aus banner_url; Logo in Interaktionsbox; image_url als Polaroid (Issue #12)
    - (uncommittet) ?? qa-evidence/
    - (uncommittet) ?? qa-t_ab910276-evidence-gap-report.md

## [crawler] /Volumes/External Disk/Users/thomas/Documents/Development/recovery-worktrees/crawler-proposal-contract-issue-7
- Branch: `recovery/proposal-contract-issue-7` · HEAD `1a26057` · Basis `57c71a5`
- letzter Commit: 2026-10-15T01:27:49+02:00 — chore(gitignore): .env.local ignorieren (Secret-Schutz, keine Code-Aenderung)
- **Commits über der Baseline: 6** · ungepusht: 0 · uncommittet: 0 Dateien
- Umfang:  11 files changed, 1052 insertions(+), 36 deletions(-)
    - 1a26057 chore(gitignore): .env.local ignorieren (Secret-Schutz, keine Code-Aenderung)
    - e39d1bd fix(proposals): Child-Apply-Vertrag – Parent-Auflösung und Feldbindung
    - 7de081d fix(proposals): resolve child parents and lock series fields
    - 9c41746 fix(proposals): prefer saved own images during apply
    - a8c4a4b feat(schemas,proposals): parent_fields for new series, accepted_changes enforcement in merge
    - f860835 fix(proposals): preserve child apply parent and entity selections

## [crawler] /Volumes/External Disk/Users/thomas/Documents/Development/001_FB_Event_Crawler
- Branch: `docs/agents-dev-slots` · HEAD `1a434ac` · Basis `57c71a5`
- letzter Commit: 2026-10-29T17:05:37+01:00 — docs(agents): Devserver-Slots als Pflicht auf dem Entwicklungsrechner
- **Commits über der Baseline: 3** · ungepusht: 0 · uncommittet: 2 Dateien
- Umfang:  4 files changed, 257 insertions(+), 23 deletions(-)
    - 1a434ac docs(agents): Devserver-Slots als Pflicht auf dem Entwicklungsrechner
    - 7812521 fix(portal-sync): Querformat-Bilder (FB-Banner) landen in banner_image_url statt image_url; Master ohne -original-Suffix
    - 7243df6 chore(gitignore): .env.local und .env*.local ignorieren (Secret-Schutz)
    - (uncommittet) ?? .codegraph/
    - (uncommittet) ?? scripts/cleanup_crawler_cache.py

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/recovery-worktrees/location-detail-issue-10
- Branch: `recovery/location-detail-issue-10` · HEAD `be7975f` · Basis `39d9500`
- letzter Commit: 2026-10-13T23:11:38+02:00 — chore(recovery): uncommittete Arbeit sichern (Location-Detail #10)
- **Commits über der Baseline: 1** · ungepusht: 1 · uncommittet: 0 Dateien
- Umfang:  20 files changed, 2233 insertions(+), 191 deletions(-)
    - be7975f chore(recovery): uncommittete Arbeit sichern (Location-Detail #10)

## [crawler] /Volumes/External Disk/Users/thomas/Documents/Development/001_FB_Event_Crawler/.kilo/worktrees/accessible-style
- Branch: `accessible-style` · HEAD `d72bbab` · Basis `57c71a5`
- letzter Commit: 2026-10-13T23:11:41+02:00 — chore(recovery): uncommittete Arbeit sichern (Crawler, accessible-style)
- **Commits über der Baseline: 1** · ungepusht: 0 · uncommittet: 1 Dateien
- Umfang:  14 files changed, 331 insertions(+), 214 deletions(-)
    - d72bbab chore(recovery): uncommittete Arbeit sichern (Crawler, accessible-style)
    - (uncommittet) ?? profile_source.html

## [portal] /Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage/.kilo/worktrees/bold-stay
- Branch: `bold-stay` · HEAD `b31adf3` · Basis `39d9500`
- letzter Commit: 2026-06-14T19:11:01+02:00 — fix: Use correct @mui/icons-material import path
- **Commits über der Baseline: 0** · ungepusht: 0 · uncommittet: 1 Dateien
- Umfang: -
    - (uncommittet) M .kilo/package-lock.json

## Ohne eigene Arbeit

- [?] /Volumes/External Disk/Users/thomas/.hermes/kanban/workspaces/t_2d8a7cc2/wt · `None` · `None`
- [?] /Volumes/External Disk/Users/thomas/.hermes/kanban/workspaces/t_9bd03c80/release-checkout · `None` · `None`
- [?] /Volumes/External Disk/Users/thomas/.hermes/kanban/workspaces/t_9bd03c80/release-smoke · `None` · `None`
