# tuskpy

A PostgreSQL-compatible database engine, built from scratch in Python, for learning.

> "What I cannot create, I do not understand." — Richard Feynman

## Why

I like building things as a way to understand them. If I can build it, I understand it.

I have loved relational database systems since my university days as an electrical engineer. A database is where many fields of computer science meet: compilers and parsers, operating system concepts, data structures, concurrency, and the theory of how to store data and keep it correct. I want to understand how these pieces fit together, and the best way I know is to write them myself.

## Goals

- **Learn by building.** Understanding comes first, and every component is written to be read.
- **Design and implement it properly.** The aim is production-grade quality: tests, clear architecture, and attention to correctness and durability.
- **Stay close to PostgreSQL's behavior.** Postgres is the reference for what a good relational database does, and tuskpy follows its SQL dialect and semantics where practical.
- **Learn with an AI guide.** The project is built with AI assistance, but I write the implementation myself, guided by the teach-tdd loop described below.
- **Test the teach-tdd workflow at scale.** A database engine is large and complex enough to show whether the loop holds up on a real project.

## How it's built: the teach-tdd loop

This project is also a large-scale test of my adapted version of [Matt Pocock's](https://github.com/mattpocock) skills. I modified a subset of them to create a teaching loop, which I call **teach-tdd**.

1. I tell the agent what I want to build.
2. The agent guides me through it and proposes the next test.
3. I implement the minimal code that makes the test green.
4. Repeat.

The agent teaches and sets the direction, and I write the code. That keeps the goal of the project intact: I build every piece myself, so I understand it.

## Non-goals

- This is not reverse engineering. I am not copying PostgreSQL's source code, and the design comes from first principles and public documentation.
- This is not a drop-in replacement for PostgreSQL, at least not yet.

## Planned building blocks

- SQL lexer, parser and planner
- Query executor
- Storage engine: pages, heap files and indexes
- Buffer manager
- Transactions, MVCC and write-ahead logging
- Network layer speaking the PostgreSQL wire protocol

## Status

Early days. Nothing runs yet.

## Name

The tusk is a nod to the PostgreSQL elephant, and `py` is for Python. tuskpy is an independent project and is not affiliated with the PostgreSQL project.

## License

MIT. See [`LICENSE`](LICENSE).
