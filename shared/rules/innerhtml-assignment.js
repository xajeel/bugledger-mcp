// ruleid: bugledger-innerhtml-assignment
container.innerHTML = userMarkup;

// ruleid: bugledger-innerhtml-assignment
document.querySelector("main").innerHTML = `<h1>${title}</h1>`;

// ok: bugledger-innerhtml-assignment
container.textContent = userText;

// ok: bugledger-innerhtml-assignment
container.innerHTML = DOMPurify.sanitize(userMarkup);

// ok: bugledger-innerhtml-assignment
container.innerHTML = sanitizeHtml(userMarkup);
