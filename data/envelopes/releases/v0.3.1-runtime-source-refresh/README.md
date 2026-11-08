# Native runtime-source refresh — 0.3.1

This separately authored current cohort was registered on 2026-11-08.
`manifest.json` records actual public producer commits, source trees, source
byte-manifest digests, exact exported-byte hashes, and the existing native
export recipes. All seven public exports were recomputed from those sources.
Golden 0.6.1 at `5a10c8799c1097b7b7e2876932307bcce676df66` was run with
Python 3.10.22; its export was measured byte-identical to the preceding
Golden 0.6.0 export, SHA-256
`92b6461c399a6a1c6a8c39e70e5a12ec89a703b25b7b51b0adaddff35d980fd0`.
The other six public exports were also measured byte-identical to their prior
exports. These are new source-bound production observations, not rewritten
producer claims in historical manifests and not changed native findings.

Native fixture review dates and eight distinct subjects remain unchanged.
Registration produces two states, explicitly retains `CANNOT_COMPARE` and
`RETURN_DUE`, and projects zero for the declared transport use. It does not
make the fixtures fresh or establish shared-subject correspondence.

Violet contributes only its exact approved synthetic public common envelope
and unchanged disclosure review. Its exported source references remain empty.
No private producer identity, implementation, native assessment, history, or
release custody is included or inferred.

Replay with the existing generic builder:

```bash
uv run python scripts/build_release_cohort.py data/envelopes/releases/v0.3.1-runtime-source-refresh
```

The builder checks exact exported bytes, common-envelope admission, attribution,
and the register chain. It does not verify producer commits, fetch native
reports, or interpret native verdicts. Source custody and actual native API
execution are separate evidence, not capabilities added to that builder.
Every prior cohort and historical release packet remains byte-for-byte intact.
