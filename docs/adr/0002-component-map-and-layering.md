# Component map and layering

tuskpy has the components below, in layers. A component depends only on components in lower layers, or on a shared module. No component depends on a higher layer. Fixed layers keep each component testable on its own and stop dependency cycles before they start.

```
CLIENT SIDE                         SERVER SIDE
L6  tuskpy CLI                      Postmaster
L5  tuskpy API (DB-API + dialect)   Backend (message loop)
L4                                  SQL compiler → Analyzer → Planner → Executor
L3                                  Catalog        Recovery
L2                                  Access methods (heap, B-tree)
L1                                  Buffer manager   Transaction manager   Lock manager
L0                                  Storage manager   WAL   Shared memory

SHARED BY BOTH SIDES: Wire protocol (protocol messages + wire encoding)
SHARED BY THE SERVER: Types and values
```

## Decisions inside the map

- **WAL and Recovery are two components.** The buffer manager must flush the WAL before it writes a dirty page, so the buffer manager depends on the WAL. Recovery replays log records through the buffer manager and the access methods, so Recovery sits above them. One combined component would make a cycle.
- **The catalog sits above the access methods.** As in PostgreSQL, the catalog is stored in ordinary tables. The analyzer depends on the catalog.
- **The access methods depend on the transaction manager, never the reverse.** The transaction manager knows nothing about pages or tuples. The lock manager is a separate component.
- **All frontends go through the wire protocol.** tuskpy has no embedded mode. The tuskpy CLI is built on the tuskpy API. The wire protocol is a separate module under the DB-API layer, so the **wire encoding** can change without a change to the layers above.
- **`psql` and `psycopg` are reference clients for tests**, not tuskpy frontends.

## Build or reuse

tuskpy builds every server component from scratch. Third-party libraries appear only at the edges, and they stay there:

- tuskpy CLI: `prompt_toolkit` and `rich`.
- tuskpy API dialect: a subclass of SQLAlchemy's PostgreSQL dialect.
- Types and values: stdlib `decimal`, `datetime`, and `uuid` for Python values. tuskpy builds its own on-disk encoding.
- Storage manager, shared memory, and WAL: stdlib only.

We rejected `pglast` for the SQL compiler. It brings PostgreSQL's own C parser into the engine, and the parser is core learning.
