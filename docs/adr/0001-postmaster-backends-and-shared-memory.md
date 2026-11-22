# Postmaster, one backend per connection, and shared memory

tuskpy uses the PostgreSQL process model. One **postmaster** process accepts each connection and forks one **backend** process for it. All backends share the buffer pool, the lock table, the transaction table, and the WAL buffers through **shared memory**, which the postmaster creates before it forks. We chose this model for fidelity to PostgreSQL and for what it teaches about operating systems, and we accept its cost. Shared state must be laid out as raw bytes, not Python objects, and the server runs only on POSIX systems.

## Considered options

- **Shared memory (chosen).** The PostgreSQL model.
- **Forked backends with one central shared-state process.** Simpler data structures, but every page access costs an IPC round trip, and PostgreSQL does not work this way.
- **Threads first, processes later.** Fast to start, but the move to processes later changes the buffer manager, the lock manager, and the WAL.

## Why `os.fork()` and not `multiprocessing.Process`

The postmaster starts backends with `os.fork()` and reaps them with `os.waitpid()`. tuskpy does not use `multiprocessing.Process`.

1. **Socket inheritance.** The postmaster accepts a connection and then forks. The backend inherits the open socket as a file descriptor at no cost. Since Python 3.14, the default `multiprocessing` start method on Linux is `forkserver`. With `forkserver` or `spawn`, the child does not inherit the socket, and the parent must send the file descriptor to it. With the `fork` start method forced, `multiprocessing.Process` is only a wrapper around `os.fork()`.
2. **Fidelity and learning.** The PostgreSQL postmaster calls `fork()`, reaps dead children with `waitpid()` on `SIGCHLD`, and resets shared memory after a backend crash. With `os.fork()`, tuskpy writes these steps itself. `multiprocessing` hides them.
3. **The resource tracker.** By default, `multiprocessing` registers each shared memory segment with a resource tracker process. The tracker can unlink a segment when the process that created it exits. That is wrong for memory that the postmaster owns.
4. **One explicit rule.** Fork is unsafe in a process that runs threads, and Python 3.12+ warns about it. The postmaster stays single-threaded.

## Consequences

- Shared memory segments use `multiprocessing.shared_memory.SharedMemory(..., track=False)`.
- The postmaster runs no threads.
- The server does not run on Windows, because Windows has no `fork`. The **frontends** (tuskpy CLI and tuskpy API) can still run on Windows.
