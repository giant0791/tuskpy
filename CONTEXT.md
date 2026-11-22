# tuskpy

A PostgreSQL-compatible database engine in Python, built for learning. This file defines the project vocabulary.

## Language

### Processes and clients

**Frontend**:
A client program that sends SQL to tuskpy and shows the results, such as the tuskpy CLI or the tuskpy API.
_Avoid_: client (when you mean a tuskpy program), UI

**Postmaster**:
The server process that accepts each new connection and starts one **backend** for it.
_Avoid_: listener, supervisor, main server

**Backend**:
The server process that serves exactly one connection, from startup to disconnect.
_Avoid_: worker, session process, child

**Shared memory**:
The memory that the **postmaster** creates before it starts any **backend**, and that all **backends** use for the state they share.
_Avoid_: global state, shared cache

### Wire protocol

**Protocol message**:
One typed message between a **frontend** and a **backend**, with the same types, fields, and flow as PostgreSQL protocol v3.
_Avoid_: packet, frame, request (when you mean one message)

**Wire encoding**:
The rule that turns a **protocol message** into bytes on the socket and back.
_Avoid_: wire protocol (when you mean only the byte format), serialization format

**tuskpy encoding**:
The first **wire encoding**, which tuskpy designs itself, for learning.
_Avoid_: custom protocol, JSON protocol

**PostgreSQL v3 encoding**:
The binary **wire encoding** of PostgreSQL protocol v3, which `psql` and `psycopg` use.
_Avoid_: Postgres format, native protocol

### SQL processing

**SQL compiler**:
The component that turns SQL text into a **syntax tree**. It covers the lexer and the parser only.
_Avoid_: SQL front end, query compiler

**Syntax tree**:
The tree that the **SQL compiler** produces from one SQL statement, before name resolution.
_Avoid_: parse tree, AST (when you mean the resolved form)

## Relationships

- A **frontend** opens one connection to the **postmaster**.
- The **postmaster** starts one **backend** for each connection.
- One **backend** serves exactly one connection.
- All **backends** share the buffer pool, the lock table, the transaction table, and the WAL buffers through **shared memory**. They share no other state.
- A **frontend** and a **backend** exchange **protocol messages**. One **wire encoding** turns each message into bytes.
- The **wire encoding** is exchangeable. tuskpy starts with the **tuskpy encoding** and later changes to the **PostgreSQL v3 encoding**. The **protocol messages** do not change.
- The **SQL compiler** produces one **syntax tree** for each SQL statement.
- Name resolution and planning take a **syntax tree** as input. They are not part of the **SQL compiler**.

## Example dialogue

> **Dev:** "Does the **SQL compiler** check that the table `users` exists?"
> **Domain expert:** "No. The **SQL compiler** only turns text into a **syntax tree**. Name resolution checks the table, later in the engine."

## Flagged ambiguities

- "Wire protocol" can mean the message set or the byte format. Resolved: the message set is the **protocol messages**, and the byte format is the **wire encoding**.
- "SQL compiler" can mean text → syntax tree, text → resolved tree, or text → plan. Resolved: it means text → **syntax tree** only.
