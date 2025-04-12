const form = document.querySelector("#upload-form"),
    fileInput = form.querySelector(".file-input"),
    progressArea = document.querySelector(".upload-progress"),
    uploadedArea = document.querySelector(".uploaded-area");
const generateBtn = document.querySelector("#generate-btn");

form.addEventListener("click", () => {
    fileInput.click();
});
fileInput.onchange = ({ target }) => {
    let file = target.files[0];
    if (file) {
        uploadFile(file);
    }
}
function uploadFile(file) {
    let xhr = new XMLHttpRequest();
    let formData = new FormData();
    formData.append("file", file);
    formData.append("csrfmiddlewaretoken", document.querySelector("[name=csrfmiddlewaretoken]").value);

    xhr.open("POST", "/flashcards/upload/", true);

    xhr.upload.onprogress = (event) => {
        let percent = Math.round((event.loaded / event.total) * 100);
        progressArea.innerHTML = `<li class="row">
                <i class="fas fa-file-alt"></i>
                <div class="upload-content">
                    <div class="upload-details">
                        <span class="name">${file.name}</span>
                        <span class="percent">${percent}%</span>
                    </div>
                    <div class="upload-progress-bar">
                        <div class="progress" style="width: ${percent}%"></div>
                    </div>
                </div>
            </li>`;
    };

    xhr.onload = () => {
        if (xhr.status === 200) {
            let response = JSON.parse(xhr.responseText);
            progressArea.innerHTML = "";
            uploadedArea.innerHTML += `<li class="row">
                <i class="fas fa-file-alt"></i>
                <div class="upload-content">
                    <div class="upload-details">
                        <span class="name">${file.name}* Uploaded</span>
                        <span class="size">${(file.size/1024).toFixed(1)}KB</span>
                    </div>
                </div>
                <i class="fas fa-check"></i>
            </li>`;
            generateBtn.style.display = "block";
        }
        else{
            alert("File upload failed");
        }
    };

    xhr.send(formData);
    generateBtn.addEventListener("click", () => {
        fetch("/flashcards/process-flashcards/")
            .then(response => response.text())
            .then(file_id => {
                window.location.href = `/flashcards/show-flashcards/${file_id}/`;
            });
    });
    
}
document.addEventListener("DOMContentLoaded", function () {
    let flashcards = document.querySelectorAll(".flashcard");
    let currentIndex = 0;

    function showFlashcard(index) {
        flashcards.forEach((card, i) => {
            card.style.display = i === index ? "block" : "none";
        });
    }

    if (flashcards.length > 0) {
        showFlashcard(currentIndex);
    }

    document.addEventListener("keydown", function (event) {
        if (event.key === "ArrowRight") {
            if (currentIndex < flashcards.length - 1) {
                currentIndex++;
                showFlashcard(currentIndex);
            }
        } else if (event.key === "ArrowLeft") {
            if (currentIndex > 0) {
                currentIndex--;
                showFlashcard(currentIndex);
            }
        }
    });
});