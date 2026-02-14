# 📦 Procedural Archive CLI

A deliberately small project built to learn how to design reliable, stateful systems from scratch — not to archive files, but to understand persistence, idempotency, and safe failure.

---

## 🤔 Why This Exists

This wasn’t built to compete with existing tools.

It was built to learn:

* 🧠 How persistent state actually works
* 🔁 What idempotency really means
* 💥 How to design for safe failure
* 🗄 How databases drive behavior
* 🧱 How to build something non-trivial using only procedural Python

The constraint was intentional: no frameworks, no abstractions, no magic.

---

## ⏳ Timeline

Built in **14 days**, with strict daily gates:

* Scan → track → detect change
* Archive safely
* Induce failure
* Retry cleanly
* Verify persistent state

No progressing without passing the gate.

---

## 🧩 What It Proves

* The program runs.
* It fails safely.
* It recovers deterministically.
* It avoids duplicate archives.
* State persists across runs.

---

## 🛠 Stack

Pure Python (standard library only)
SQLite
Procedural design only

---

## 🎯 The Real Outcome

The output isn’t a zip file.

It’s a deeper understanding of how reliable systems are built.

It was about learning how to build reliable systems on purpose.
