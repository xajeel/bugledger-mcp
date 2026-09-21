declare const preview: HTMLElement;
declare const markdown: string;

// ruleid: bugledger-innerhtml-assignment
preview.innerHTML = markdown;

// ok: bugledger-innerhtml-assignment
preview.textContent = markdown;

// ok: bugledger-innerhtml-assignment
preview.replaceChildren(document.createTextNode(markdown));
