# 🖼️ PragyanAI Image Processing Studio

## 📌 Project Overview

PragyanAI Image Processing Studio is a web-based image processing application that allows users to upload images and apply various image processing operations through a simple and user-friendly interface.

The project uses a frontend deployed on Netlify and a Python Flask backend deployed on Render.

## ✨ Features

1. **Image Blending** – Combine two images with adjustable blending intensity.
2. **Background Change** – Replace a simple image background with a selected color.
3. **Grayscale Conversion** – Convert colored images into grayscale.
4. **Pencil Sketch** – Transform images into pencil-sketch effects.
5. **Pixelation** – Create pixelated images using different pixel sizes.
6. **Image Sharpening** – Enhance image details and sharpness.
7. **Multiple Images** – Combine multiple images into a collage.
8. **Image Addition and Subtraction** – Perform pixel-level arithmetic operations on two images.
9. **Noise Addition** – Add Gaussian or salt-and-pepper noise to images.
10. **Multiple Image Operations** – Apply a sequence of image processing operations.

## 🛠️ Tech Stack

**Frontend**
- HTML5
- CSS3
- JavaScript

**Backend**
- Python
- Flask
- Flask-CORS
- Pillow
- NumPy
- Gunicorn

**Deployment**
- Netlify – Frontend hosting
- Render – Backend hosting
- GitHub – Source code management

## 🌐 Live Application

**Netlify Frontend:** [Open Image Processing Studio](https://pixelcraftimageprocessing452003.netlify.app/)

**Render Backend:** `https://YOUR-RENDER-SERVICE.onrender.com`

> Replace the placeholder URLs with your actual deployed URLs.

## 📂 Project Structure

```text
PragyanAI_Image_Processing_Studio/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── backend/
│   ├── config.json
│   ├── main.py
│   ├── requirements.txt
│   └── utils.py
└── README.md
```

## 🚀 How to Use

1. Open the live application using the Netlify link.
2. Upload an image from your device.
3. Select an image processing operation.
4. Upload a second image if the selected operation requires one.
5. Adjust the available settings.
6. Process the image.
7. Preview and download the processed result.

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone YOUR-GITHUB-REPOSITORY-URL
cd PragyanAI_Image_Processing_Studio
```

### 2. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start the backend

```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

For local development, you can alternatively use Flask's development server if configured in `main.py`.

### 4. Open the frontend

Open `frontend/index.html` in a browser after configuring `frontend/script.js` to point to your running backend.

## 🎯 Project Objectives

- Understand practical image processing techniques.
- Implement image transformations using Python.
- Build a web interface for image processing.
- Connect a JavaScript frontend to a Flask backend.
- Deploy a full-stack application using Netlify and Render.

## 📚 Learning Outcomes

- Image manipulation using Pillow and NumPy.
- Pixel-level operations and image transformations.
- REST API development using Flask.
- Frontend and backend integration.
- Cloud deployment and GitHub-based project management.

## 👨‍💻 Author

**Ajay Saware**
