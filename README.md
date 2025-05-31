# QuantM -  Estimation of SCC in milk Web App (Flask + OpenCV)

This Flask-based web application allows users to capture or upload microscope images, process them using OpenCV, and estimate cell concentration based on pixel analysis.

## 📷 Key Features

- Upload or capture AVM images
- OpenCV-based pixel analysis and thresholding
- Real-time concentration estimation (cells/mL)
- Image thumbnail generation with annotated results
- Web interface built with Flask and Bootstrap
- Compatible with Raspberry Pi

## 📁 Project Structure

```
.
├── app.py               # Main Flask app with full functionality
├── demoapp.py           # Simplified variant of app.py
├── originlal.py         # Alternate approach for analysis and UI
├── requirements.txt     # Python dependencies
├── .gitignore
├── zyx.java             # (Unrelated Java file included in repo)
├── data/                # Folder for uploaded files
└── data/thumbnail/      # Folder for storing result thumbnails
```

## 🚀 Setup Instructions for Raspberry Pi

### 1. Update & Install System Packages

```bash
sudo apt update && sudo apt upgrade
sudo apt install python3 python3-pip libatlas-base-dev libjasper-dev libqtgui4 python3-pyqt5 libqt4-test
```

### 2. Install Python Dependencies

```bash
pip3 install -r requirements.txt
pip3 install opencv-python-headless
```

> ⚠️ Note: We use `opencv-python-headless` to avoid GUI conflicts on Raspberry Pi.

### 3. Clone the Repository

```bash
git clone https://github.com/Yathi123/QuantM.git
cd QuantM
```

### 4. Create Data Directories

```bash
mkdir -p data/thumbnail
```

### 5. Run the Flask App

```bash
python3 app.py
```

Access the app via your browser at:

- `http://127.0.0.1:5000/` (local)

## 🧠 How It Works

- The captured or uploaded image is thresholded using OpenCV.
- Black pixels are counted and interpreted as cells.
- Cell concentration (cells/mL) is calculated using a defined formula.
- Thumbnail images are created with overlaid results.

## 🗂 Multiple Versions Included

- `app.py` – Main and most complete application.
- `demoapp.py` – Simplified variant for demonstrations.
- `originlal.py` – Experimental version with alternate thresholding logic.

## 🌐 GitHub Repository

View the full project on GitHub: [https://github.com/Yathi123/QuantM](https://github.com/Yathi123/QuantM)

## 🧾 License

MIT License. See `LICENSE` file for details.
