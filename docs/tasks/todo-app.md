# Task: Mac todo app and logo

Build in `rigs/workspace/todo-app/` (the shared workspace). Target: macOS 27.0.1 on Apple
silicon, Swift 6.4, Command Line Tools only (no Xcode: no `xcodebuild`, no asset
catalogs). Use SwiftPM (`swift build`) and assemble the `.app` bundle yourself.

## Deliverables

1. A small native todo app (SwiftUI): add, complete, delete, persist to disk, keyboard
   friendly. Smallest version that does the job; no extras.
2. An app icon / logo that suits the current macOS look. Produce an `AppIcon.icns`
   (`iconutil`) from a 1024px source. Models here are text-only coders: draw it as SVG
   or generate it with code (CoreGraphics/Swift script); do not fake it.
3. A working `TodoApp.app` bundle that launches, plus a test target with at least one
   passing test of the todo logic (`swift test`).

## How to work

- Lead (you): split the work, delegate to `builders-pi-1`, `builders-pi-2` and
  `builders-opencode` (use `rig send`), keep builders in separate subdirectories or
  files so they do not collide, then have `review-pi` review before you accept.
- Builders and reviewer run a local 30B open model: give them small, concrete,
  verifiable tasks.
- Done means: `swift build` and `swift test` pass and the app launches. Report what
  you ran and its output, not a claim.
- Keep a short log in `rigs/workspace/todo-app/WORKLOG.md`: who did what, what failed,
  what you had to retry. This is used for analysis afterwards.
