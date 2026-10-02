# postgres-alt — the discarded path

This is the first attempt: PostgreSQL 17 in Docker, port 55432.

**Discarded in favour of SQLite.** Reasons, in order of weight:

1. **Engram — the ecosystem's own memory system — is SQLite + FTS5 with
   `tokenize='trigram'`.** And Engram's own architecture splits local (SQLite,
   "the absolute authority") from cloud (Postgres). This store is local.
2. 20 MB, one writer, no concurrent access. A server buys nothing.
3. A file cannot have the three failure modes this approach produced: a
   root-owned bind mount, a stale mount inode, and a non-idempotent init script
   that only runs on an empty volume.

`load-postgres.sh` is kept for reference. The original Postgres `schema.sql` was
superseded by the SQLite one at `../schema.sql` and is not preserved here.

Docker remains the right answer **if** this ever needs to be shared by several
people — which is exactly the split Engram already made.
