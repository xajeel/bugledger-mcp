// ruleid: bugledger-empty-catch-js
try { doSomething(); } catch (e) { }

// ok: bugledger-empty-catch-js
try {
  doSomething();
} catch (e) {
  console.error("failed:", e);
}
