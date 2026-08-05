# MindRoom Architecture Map V2

Run: `graphify-v2-repair-20260728T095646`

The authoritative architecture is a layered directed multi-relationship graph. File nodes cover the entire repository; vendor internals, generated bindings, tests, build/config, packaging, migrations, documentation, and media are separated from authored runtime.

## Layer node counts

- ASSET_AND_MEDIA: 758
- AUTHORED_RUNTIME: 24720
- BUILD_AND_CONFIG: 834
- DOCUMENTATION_AND_LEGAL: 181
- EXTERNAL_DEPENDENCY: 900
- GENERATED_BINDING: 1573
- MIGRATION_AND_SCHEMA: 1642
- PACKAGING_AND_DEPLOYMENT: 97
- PLANNED_CAPABILITY: 1640
- TEST_AND_FIXTURE: 2186
- VENDOR_AND_TOOLCHAIN: 6

Runtime registrations: 643  
Directed edges: 111276
