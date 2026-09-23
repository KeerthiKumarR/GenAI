# LinkedIn QR Code Generator App 📱

A Python utility to generate high-resolution, customized QR codes for your LinkedIn profile with terminal scanning preview support.

---

## 🚀 Quick Start

### 1. Setup & Activate Virtual Environment

```bash
cd qr_app

# Create virtual environment (if not already created)
python3 -m venv venv

# Activate virtual environment
# On macOS / Linux:
source venv/bin/activate

# On Windows (Command Prompt):
# venv\Scripts\activate.bat
# On Windows (PowerShell):
# .\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 💻 Usage

### Interactive Mode
Simply run the script and enter your username or full URL when prompted:
```bash
python generate_qr.py
```

### CLI Arguments Mode
Pass the URL or LinkedIn username directly:
```bash
# Using username
python generate_qr.py --url keerthikumar

# Using full profile URL
python generate_qr.py --url "https://www.linkedin.com/in/keerthikumar"

# Custom output file name
python generate_qr.py -u keerthikumar -o my_linkedin_qr.png

# Custom colors (Classic Black & White)
python generate_qr.py -u keerthikumar --fill-color black --back-color white

# High-res print quality
python generate_qr.py -u keerthikumar --box-size 20 --border 6 -o print_qr.png
```

---

## ⚙️ Options & Flags

| Flag | Description | Default |
|---|---|---|
| `-u`, `--url` | LinkedIn profile URL or username | Interactive prompt |
| `-o`, `--output` | Output filename/path for the PNG | `linkedin_qr.png` |
| `--fill-color` | Color for the QR code modules | `#0A66C2` (LinkedIn Blue) |
| `--back-color` | Background color | `white` |
| `--box-size` | Pixel size of each QR box | `10` |
| `--border` | Thickness of border (boxes) | `4` |
| `--no-preview` | Disable ASCII preview in terminal | False |

---

## 📦 Project Structure

```
qr_app/
├── generate_qr.py    # Main script
├── requirements.txt  # Project dependencies (qrcode, pillow)
├── README.md         # Documentation
├── .gitignore        # Git ignore rules
└── venv/             # Python virtual environment (isolated)
```
