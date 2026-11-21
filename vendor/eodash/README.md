# eodash classroom package

This is **eodash 5.10.0**, EOX and contributors, **MIT**, from the official npm release. The archive retains upstream source files and its LICENSE. `scripts/vendor_eodash.py` verifies npm's SHA-512 integrity before applying these packaging changes:

- Remove the optional `animated-details` import and customized built-in `is` attribute from the source and compiled widget container. Standard HTML `<details>` panels remain operable; their extra animation is omitted.
- Remove that Git-only dependency from `package.json`. Standard `npm ci` needs no expanded Git dependency permission.
- Pin `@eodash/stac` to 0.2.0, which exports the functions imported by the 5.10.0 frontend. The original manifest incorrectly requests 0.1.x.
- Omit the monorepo `prepare` lifecycle script: the archive already contains the upstream built frontend, so consumers do not need its workspace build tooling.

See `provenance.json` for source integrity, adapted checksum and exact changed files. These are course packaging adaptations, not an upstream release or endorsement. Original eodash documentation and source: <https://github.com/eodash/eodash>. Upstream MIT notice: `licenses/eodash-LICENSE.txt` in the course repository and `package/LICENSE` inside the archive.
