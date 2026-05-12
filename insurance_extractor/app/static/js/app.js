function copyText(text) {
    if (navigator.clipboard) {
        return navigator.clipboard.writeText(text);
    }

    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
    return Promise.resolve();
}

function escapeHtml(text) {
    const replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
    };

    return text.replace(/[&<>"']/g, (character) => replacements[character]);
}

function escapeRegExp(text) {
    return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function findSourceRange(fullText, sourceText) {
    const exactIndex = fullText.indexOf(sourceText);
    if (exactIndex !== -1) {
        return {
            start: exactIndex,
            end: exactIndex + sourceText.length,
        };
    }

    // Extractors store source_text as readable one-line snippets. The document
    // text can contain line breaks in the same place, so whitespace is matched
    // flexibly here.
    const flexiblePattern = escapeRegExp(sourceText.trim()).replace(/\s+/g, "\\s+");
    if (!flexiblePattern) {
        return null;
    }

    const match = fullText.match(new RegExp(flexiblePattern, "i"));
    if (!match || match.index === undefined) {
        return null;
    }

    return {
        start: match.index,
        end: match.index + match[0].length,
    };
}

function showSourceWarning(message) {
    const warning = document.querySelector("[data-source-warning]");
    if (!warning) {
        return;
    }

    warning.textContent = message;
    warning.hidden = false;
}

function hideSourceWarning() {
    const warning = document.querySelector("[data-source-warning]");
    if (warning) {
        warning.hidden = true;
        warning.textContent = "";
    }
}

function resetSourceText(sourcePreview, fullText) {
    sourcePreview.innerHTML = escapeHtml(fullText);
}

function highlightSourceText(sourceText) {
    const sourcePreview = document.querySelector("[data-document-text]");
    if (!sourcePreview) {
        return;
    }

    const fullText = sourcePreview.dataset.fullText || sourcePreview.textContent;
    sourcePreview.dataset.fullText = fullText;

    if (!sourceText) {
        resetSourceText(sourcePreview, fullText);
        showSourceWarning("Для этого поля нет source_text.");
        return;
    }

    const range = findSourceRange(fullText, sourceText);
    if (!range) {
        resetSourceText(sourcePreview, fullText);
        showSourceWarning("source_text не найден в тексте документа.");
        return;
    }

    hideSourceWarning();

    const before = fullText.slice(0, range.start);
    const highlighted = fullText.slice(range.start, range.end);
    const after = fullText.slice(range.end);

    sourcePreview.innerHTML = [
        escapeHtml(before),
        '<mark class="source-highlight active-source-highlight">',
        escapeHtml(highlighted),
        "</mark>",
        escapeHtml(after),
    ].join("");

    const highlight = sourcePreview.querySelector(".active-source-highlight");
    if (highlight) {
        highlight.scrollIntoView({
            behavior: "smooth",
            block: "center",
        });
    }
}

document.querySelectorAll(".upload-form").forEach((uploadForm) => {
    const fileInput = uploadForm.querySelector("input[type='file']");
    const fileName = uploadForm.querySelector("[data-file-name]");

    if (fileInput && fileName) {
        fileInput.addEventListener("change", () => {
            const selectedFile = fileInput.files[0];
            fileName.textContent = selectedFile ? selectedFile.name : "";
        });
    }

    uploadForm.addEventListener("submit", () => {
        const submitButton = uploadForm.querySelector("button[type='submit']");
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Загрузка...";
        }
    });
});

document.querySelectorAll("[data-copy-value]").forEach((button) => {
    button.addEventListener("click", (event) => {
        event.stopPropagation();

        copyText(button.dataset.copyValue || "").then(() => {
            const originalText = button.textContent;
            button.textContent = "Скопировано";
            setTimeout(() => {
                button.textContent = originalText;
            }, 1200);
        });
    });
});

document.querySelectorAll(".source-row").forEach((row) => {
    row.addEventListener("click", () => {
        document.querySelectorAll(".source-row.is-source-active").forEach((activeRow) => {
            activeRow.classList.remove("is-source-active");
        });

        row.classList.add("is-source-active");
        highlightSourceText(row.dataset.sourceText || "");
    });
});

const copyAllButton = document.querySelector("[data-copy-all]");
const copyAllText = document.querySelector("#copy-all-text");

if (copyAllButton && copyAllText) {
    copyAllButton.addEventListener("click", () => {
        copyText(copyAllText.value).then(() => {
            const originalText = copyAllButton.textContent;
            copyAllButton.textContent = "Скопировано";
            setTimeout(() => {
                copyAllButton.textContent = originalText;
            }, 1200);
        });
    });
}
