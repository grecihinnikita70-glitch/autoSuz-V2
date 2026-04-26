const fileInput = document.querySelector("#document");
const fileName = document.querySelector("[data-file-name]");
const uploadForm = document.querySelector(".upload-form");

if (fileInput && fileName) {
    fileInput.addEventListener("change", () => {
        const selectedFile = fileInput.files[0];
        fileName.textContent = selectedFile ? selectedFile.name : "";
    });
}

if (uploadForm) {
    uploadForm.addEventListener("submit", () => {
        const submitButton = uploadForm.querySelector("button[type='submit']");
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Загрузка...";
        }
    });
}
