document.addEventListener("DOMContentLoaded", function () {
    const startBtn = document.getElementById("enter-fullscreen-btn");
    const examContainer = document.getElementById("exam-container");
    const fullscreenPrompt = document.getElementById("fullscreen-prompt");
    const form = document.getElementById("exam_form");

    let alreadySubmitted = false;

    let allowTemporaryBlur = false;

    // When camera or file input is triggered, mark blur as safe
    document.addEventListener("click", (e) => {
        const tag = e.target.tagName.toLowerCase();
        const isSafeClick = tag === "input" || tag === "button";

        if (isSafeClick && (
            e.target.classList.contains("open-camera-btn") ||
            e.target.classList.contains("capture-btn") ||
            e.target.type === "file"
        )) {
            allowTemporaryBlur = true;
            setTimeout(() => allowTemporaryBlur = false, 2000);
        }
    });


    function submitIfNeeded(reason) {
        if (alreadySubmitted) return;
        alreadySubmitted = true;
        //alert(`Exam automatically submitted due to: ${reason}`);
        form.submit();
    }

    // Enter fullscreen on button click
    startBtn.addEventListener("click", async () => {
        const docEl = document.documentElement;
        try {
            if (docEl.requestFullscreen) {
                await docEl.requestFullscreen();
            } else if (docEl.webkitRequestFullscreen) {
                await docEl.webkitRequestFullscreen();
            } else {
                alert("Fullscreen not supported on your browser.");
                return;
            }

            fullscreenPrompt.style.display = "none";
            examContainer.style.display = "block";

        } catch (err) {
            alert("Failed to enter fullscreen: " + err.message);
        }
    });

    // Disable right-click
    document.addEventListener("contextmenu", e => e.preventDefault());

    // Disable copy-paste
    document.addEventListener("copy", e => e.preventDefault());
    document.addEventListener("paste", e => e.preventDefault());
    document.addEventListener("cut", e => e.preventDefault());

    // Disable Ctrl+U, F12, Ctrl+Shift+I, etc.
    document.addEventListener("keydown", function (e) {
        if (
            (e.ctrlKey && (e.key === 'u' || e.key === 'U' || e.key === 'c' || e.key === 'v')) ||
            (e.key === 'F12') ||
            (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i'))
        ) {
            e.preventDefault();
        }
    });

    // Auto-submit on tab switch or minimize or resize
    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState !== "visible") {
            submitIfNeeded("tab switch or browser minimize");
        }
    });

    window.addEventListener("blur", () => {
        if (!allowTemporaryBlur) {
            submitIfNeeded("window unfocused");
        }
    });
    
    let resizeCount = 0;

    window.addEventListener("resize", () => {
        resizeCount++;
        // Allow first resize caused by fullscreen
        if (resizeCount > 1) {
            submitIfNeeded("window resized");
        }
    });
});
