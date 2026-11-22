# tuskpy

A PostgreSQL-compatible database engine in Python, built for learning. This file defines the project vocabulary.

## Language

**SQL compiler**:
The component that turns SQL text into a **syntax tree**. It covers the lexer and the parser only.
_Avoid_: SQL front end, query compiler

**Syntax tree**:
The tree that the **SQL compiler** produces from one SQL statement, before name resolution.
_Avoid_: parse tree, AST (when you mean the resolved form)

## Relationships

- The **SQL compiler** produces one **syntax tree** for each SQL statement.
- Name resolution and planning take a **syntax tree** as input. They are not part of the **SQL compiler**.

## Example dialogue

> **Dev:** "Does the **SQL compiler** check that the table `users` exists?"
> **Domain expert:** "No. The **SQL compiler** only turns text into a **syntax tree**. Name resolution checks the table, later in the engine."

## Flagged ambiguities

- "SQL compiler" can mean text → syntax tree, text → resolved tree, or text → plan. Resolved: it means text → **syntax tree** only.
