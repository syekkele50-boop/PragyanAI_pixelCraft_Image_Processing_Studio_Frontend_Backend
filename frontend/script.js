
const API_URL = "https://pragyanai-pixelcraft-image-processing.onrender.com";

const imageInput = document.getElementById("imageInput");
const image2Input = document.getElementById("image2Input");
const multipleInput = document.getElementById("multipleInput");
const operation = document.getElementById("operation");
const processButton = document.getElementById("processButton");
const message = document.getElementById("message");
const fileStatus = document.getElementById("fileStatus");

const originalPreview = document.getElementById("originalPreview");
const originalEmpty = document.getElementById("originalEmpty");
const resultPreview = document.getElementById("resultPreview");
const resultEmpty = document.getElementById("resultEmpty");
const downloadButton = document.getElementById("downloadButton");

const pixelSize = document.getElementById("pixelSize");
const blendAlpha = document.getElementById("blendAlpha");
const blendValue = document.getElementById("blendValue");
const backgroundColor = document.getElementById("backgroundColor");
const noiseStrength = document.getElementById("noiseStrength");
const noiseValue = document.getElementById("noiseValue");

const MAX_FILE_SIZE = 15 * 1024 * 1024;
const ALLOWED_TYPES = ["image/png", "image/jpeg", "image/webp"];

let originalUrl = null;
let resultUrl = null;

function showMessage(text, type = "info") {
  message.textContent = text;
  message.className = "message " + type;
}

function isValidFile(file) {
  return file &&
    ALLOWED_TYPES.includes(file.type) &&
    file.size <= MAX_FILE_SIZE;
}

function clearResult() {
  if (resultUrl) URL.revokeObjectURL(resultUrl);

  resultUrl = null;
  resultPreview.removeAttribute("src");
  resultPreview.hidden = true;
  resultEmpty.hidden = false;
  downloadButton.hidden = true;
  downloadButton.removeAttribute("href");
}

function updateControls() {
  const selected = operation.value;

  document.getElementById("sizeOption").hidden =
    !["pixelate", "sharpen_resize", "pipeline"].includes(selected);

  document.getElementById("blendOption").hidden = selected !== "blend";
  document.getElementById("backgroundOption").hidden = selected !== "background";
  document.getElementById("noiseOption").hidden =
    !["noise", "pipeline"].includes(selected);
  document.getElementById("pipelineOption").hidden = selected !== "pipeline";

  blendValue.textContent = blendAlpha.value + "%";
  noiseValue.textContent = noiseStrength.value;
}

operation.addEventListener("change", updateControls);

blendAlpha.addEventListener("input", () => {
  blendValue.textContent = blendAlpha.value + "%";
});

noiseStrength.addEventListener("input", () => {
  noiseValue.textContent = noiseStrength.value;
});

imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];

  clearResult();

  if (!file) {
    fileStatus.textContent = "No images selected.";
    processButton.disabled = true;
    return;
  }

  if (!isValidFile(file)) {
    imageInput.value = "";
    processButton.disabled = true;
    showMessage("Choose a valid PNG, JPG, or WEBP image up to 15 MB.", "error");
    return;
  }

  if (originalUrl) URL.revokeObjectURL(originalUrl);

  originalUrl = URL.createObjectURL(file);
  originalPreview.src = originalUrl;
  originalPreview.hidden = false;
  originalEmpty.hidden = true;

  fileStatus.textContent = "Primary image: " + file.name;
  processButton.disabled = false;
  showMessage("Image ready. Choose an operation.", "success");
});

image2Input.addEventListener("change", () => {
  const file = image2Input.files[0];

  if (file && !isValidFile(file)) {
    image2Input.value = "";
    showMessage("The second image must be PNG, JPG, or WEBP and no larger than 15 MB.", "error");
  }
});

multipleInput.addEventListener("change", () => {
  const files = Array.from(multipleInput.files);

  if (files.some(file => !isValidFile(file))) {
    multipleInput.value = "";
    showMessage("Every collage image must be a supported image up to 15 MB.", "error");
    return;
  }

  if (files.length) {
    fileStatus.textContent =
      files.length + " collage image(s) selected.";
  }
});

function collectOptions() {
  const selected = operation.value;

  const options = {
    size: Number(pixelSize.value),
    alpha: Number(blendAlpha.value) / 100,
    background_color: backgroundColor.value,
    strength: Number(noiseStrength.value),
    noise_type: document.getElementById("noiseType").value
  };

  if (selected === "pipeline") {
    options.operations = Array.from(
      document.querySelectorAll('input[name="pipeline"]:checked')
    ).map(input => input.value);
  }

  return options;
}

processButton.addEventListener("click", async () => {
  const selectedOperation = operation.value;
  const primary = imageInput.files[0];
  const second = image2Input.files[0];
  const collageFiles = Array.from(multipleInput.files);

  if (selectedOperation === "collage") {
    if (!collageFiles.length && !primary) {
      showMessage("Select one or more images for the collage.", "error");
      return;
    }
  } else if (!primary) {
    showMessage("Upload a primary image first.", "error");
    return;
  }

  if (["blend", "add", "subtract"].includes(selectedOperation) && !second) {
    showMessage("This operation requires a second image.", "error");
    return;
  }

  if (
    selectedOperation === "pipeline" &&
    !collectOptions().operations.length
  ) {
    showMessage("Select at least one operation for the pipeline.", "error");
    return;
  }

  const formData = new FormData();
  formData.append("operation", selectedOperation);
  formData.append("options", JSON.stringify(collectOptions()));

  if (primary) formData.append("image", primary);
  if (second) formData.append("image2", second);

  if (selectedOperation === "collage") {
    const files = collageFiles.length ? collageFiles : [primary];
    files.forEach(file => formData.append("images", file));
  }

  processButton.disabled = true;
  processButton.textContent = "Processing...";
  clearResult();
  showMessage("Processing your image. Please wait...", "info");

  try {
    const response = await fetch(API_URL + "/api/process", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      let errorText = "Image processing failed.";

      try {
        const data = await response.json();
        if (data.error) errorText = data.error;
      } catch (_) {}

      throw new Error(errorText);
    }

    const blob = await response.blob();

    if (!blob.type.startsWith("image/")) {
      throw new Error("The server did not return an image.");
    }

    resultUrl = URL.createObjectURL(blob);
    resultPreview.src = resultUrl;
    resultPreview.hidden = false;
    resultEmpty.hidden = true;

    downloadButton.href = resultUrl;
    downloadButton.hidden = false;

    showMessage("Image processed successfully!", "success");
  } catch (error) {
    console.error(error);

    if (error instanceof TypeError) {
      showMessage(
        "Could not connect to the backend. Check the Render URL and service status.",
        "error"
      );
    } else {
      showMessage(error.message || "Something went wrong.", "error");
    }
  } finally {
    processButton.disabled = false;
    processButton.textContent = "Process image";
  }
});

window.addEventListener("beforeunload", () => {
  if (originalUrl) URL.revokeObjectURL(originalUrl);
  if (resultUrl) URL.revokeObjectURL(resultUrl);
});

updateControls();
