# The tuskpy encoding comes before the PostgreSQL v3 encoding

The **protocol messages** follow PostgreSQL protocol v3: the same message types, fields, and flow. But the first **wire encoding** is the **tuskpy encoding**, which tuskpy designs itself, because marshalling is the part of the project that the author knows least. tuskpy changes to the **PostgreSQL v3 encoding** later. The wire encoding is an exchangeable layer, so the change does not touch the DB-API layer or the backend message loop.

## Consequences

- `psql` and `psycopg` cannot connect until the PostgreSQL v3 encoding lands. Until then, the tuskpy API is the only test client.
- gRPC is out of scope. It brings its own transport and an RPC call model, which does not fit under a message stream.
