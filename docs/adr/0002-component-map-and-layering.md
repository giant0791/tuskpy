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
- **The L4 components form a pipeline.** The analyzer takes the **syntax tree** from the SQL compiler, the planner takes the analyzer output, and the executor runs the plan. Each one imports the types of the one before it.
- **The WAL sits on shared memory.** The WAL buffers live in **shared memory**, so the WAL imports the shared memory component. The WAL does its own file I/O and does not use the storage manager, as in PostgreSQL.

## Packages and import contracts

Each component is one package. The package tree shows the two sides:

```
src/tuskpy/
  protocol/            wire protocol (protocol messages + wire encoding)
  client/
    api/               tuskpy API (DB-API); dialect/ holds the SQLAlchemy dialect
    cli/               tuskpy CLI
  server/
    types/  storage/  shared_memory/  wal/
    buffer/  transaction/  lock/  access/
    catalog/  recovery/
    compiler/  analyzer/  planner/  executor/
    backend/  postmaster/
```

The layers in the diagram are an overview. The precise rule is the server ladder below, top to bottom. A package imports only packages below it. Packages on one line with `|` are independent.

```
postmaster
backend
executor
planner
analyzer
compiler
catalog | recovery
access
buffer | transaction | lock
wal
storage | shared_memory
types
```

import-linter enforces four contracts, in `pyproject.toml`. It runs in pre-commit, so the CI `lint` job runs it.

1. `tuskpy.client | tuskpy.server` above `tuskpy.protocol`. The two sides never import each other, and the protocol imports neither side.
2. The server ladder above.
3. `cli` above `api`, inside `tuskpy.client`.
4. Third-party libraries stay at the edges. `tuskpy.server` and `tuskpy.protocol` do not import `prompt_toolkit`, `rich`, or `sqlalchemy`. `tuskpy.client.api` does not import `prompt_toolkit` or `rich`. Only `tuskpy.client.api.dialect` imports `sqlalchemy`.

A PR that adds a new dependency between components changes the contracts in the same PR, so the change is visible in review.

We rejected a flat tree with one top-level package for each component. It cannot state "the two sides share only the wire protocol" as one contract, and it makes the server-only types look shared by both sides.

## Build or reuse

tuskpy builds every server component from scratch. Third-party libraries appear only at the edges, and they stay there:

- tuskpy CLI: `prompt_toolkit` and `rich`.
- tuskpy API dialect: a subclass of SQLAlchemy's PostgreSQL dialect.
- Types and values: stdlib `decimal`, `datetime`, and `uuid` for Python values. tuskpy builds its own on-disk encoding.
- Storage manager, shared memory, and WAL: stdlib only.

We rejected `pglast` for the SQL compiler. It brings PostgreSQL's own C parser into the engine, and the parser is core learning.
