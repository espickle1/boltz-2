# CLAUDE.md — Modal Refactoring Guide

This codebase already works. You are not rewriting it. You are adapting it so that
its heavy computation runs on Modal — because the hardware to run it doesn't exist
on this machine. Your job is to find the minimal set of changes that gets this code
running on remote GPUs/CPUs while keeping it maintainable and testable locally.

Start by reading the codebase. Understand what it does and where the compute-heavy
boundaries are before you touch anything.

## Principles

**1. Wrap, don't rewrite.**
Add new files that import and call existing code — don't scatter Modal decorators
through the existing codebase. Modal is the orchestration layer. If you find
yourself rewriting business logic to fit Modal, you're going too deep.

**2. Keep business logic portable.**
Nothing in the core logic should import `modal`. If someone deleted every Modal
file from the repo, the algorithms, transformations, and business rules should
still work as plain Python. Modal decides where and how code runs. Existing code
decides what it does.

**3. Respect the execution boundary.**
Your machine and the cloud container are different computers with different
packages, files, and hardware. Every `.remote()` call is a network hop. Be
explicit about what crosses that boundary. Minimize data transfer and never
assume both sides share the same environment.

**4. Initialization is a lifecycle event.**
Expensive setup (loading models, opening connections, warming caches) happens
once when a container starts, not on every call. Use Modal's class pattern with
`@modal.enter()`. This makes the split between setup and work visible to readers,
and avoids paying startup costs on every request.

**5. One function, one job, one environment.**
Don't hold a GPU hostage while parsing CSVs. Put GPU work on GPU containers and
everything else on cheap CPU containers. Each function gets a container image
tailored to exactly what it needs — no mega-images with every dependency.

**6. State is always explicit.**
Containers vanish when they're done. Anything that must survive between calls —
model files, results, checkpoints — needs explicit storage and explicit loading.
If the existing code writes to local disk or relies on in-memory state between
requests, that's a refactoring signal.

**7. Parallelize by changing invocation, not logic.**
To go from a loop to 100 parallel containers, change how the function is called
(`.map()` instead of a for-loop), not the function itself. The processing logic
should not know or care that it's running in parallel.

**8. Preserve a local development path.**
Structure every change so that business logic can be exercised locally — on
smaller data, on CPU, with mocked inputs. Modal is the production execution
path, not the development inner loop. If the only way to test a change is
`modal run`, the feedback cycle is too slow and too expensive.

## Reference

When you need Modal API details, fetch `https://modal.com/llms.txt` — it maps
the full API surface with links to every guide page. Guide pages have `.md`
versions (e.g. `modal.com/docs/guide/images.md`) which are cleaner to read.
