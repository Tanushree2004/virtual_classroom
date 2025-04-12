document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("whiteboard");
    const ctx = canvas.getContext("2d");
    let drawColor = "#000000";
    let lineWidth = 3;
    let textSize = 20;
    let currentShape = null;
    let isDrawingShape = false;

    // Function to change line width
    function changeLineWidth(width) {
        lineWidth = width;
        ctx.lineWidth = width;
    }
    window.changeLineWidth = changeLineWidth;  // Expose to global scope

    // Function to change text size
    function changeTextSize(size) {
        textSize = size;
    }
    window.changeTextSize = changeTextSize;

    // Function to set shape type
    function setShape(shape) {
        currentShape = shape;
        isDrawingShape = true;
    }
    window.setShape = setShape;

    // Add text when clicking the canvas
    function addText() {
        let text = prompt("Enter text:");
        if (!text) return;

        canvas.addEventListener("click", function textHandler(e) {
            ctx.font = `${textSize}px Arial`;
            ctx.fillStyle = drawColor;
            ctx.fillText(text, e.offsetX, e.offsetY);
            canvas.removeEventListener("click", textHandler);
        });
    }
    window.addText = addText;

    // Handle shape drawing
    canvas.addEventListener("mousedown", function (e) {
        if (isDrawingShape && currentShape) {
            let x = e.offsetX;
            let y = e.offsetY;
            ctx.strokeStyle = drawColor;
            ctx.lineWidth = lineWidth;

            if (currentShape === "rectangle") {
                ctx.strokeRect(x, y, 100, 60);
            } else if (currentShape === "circle") {
                ctx.beginPath();
                ctx.arc(x, y, 40, 0, Math.PI * 2);
                ctx.stroke();
            }

            isDrawingShape = false;
            currentShape = null;
        }
    });

    // Image Upload Feature
    function uploadImage(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function (e) {
            let img = new Image();
            img.src = e.target.result;
            img.onload = function () {
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            };
        };
        reader.readAsDataURL(file);
    }
    document.getElementById("imageUpload").addEventListener("change", uploadImage);
});
