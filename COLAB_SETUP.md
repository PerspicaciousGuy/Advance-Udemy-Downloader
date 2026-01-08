# 🚀 Google Colab Setup Guide

This guide will help you use the Udemy Downloader on Google Colab to download courses directly to your Google Drive.

## 📋 Quick Start

### Step 1: Upload Notebook to Google Colab

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click **File** → **Upload notebook**
3. Upload the `Udemy_Downloader_Colab.ipynb` file from this repository

**OR**

1. Upload `Udemy_Downloader_Colab.ipynb` to your Google Drive
2. Right-click it → **Open with** → **Google Colaboratory**

### Step 2: Prepare Required Files

Before running the notebook, you need two files:

#### 📝 `cookie.txt` - Udemy Authentication

1. Install [Cookies Editor](https://cookie-editor.com/) browser extension
2. Log in to your Udemy account
3. Click the Cookies Editor extension icon
4. Click **Export** → Select **Netscape** format
5. Copy all the text and save it as `cookie.txt`

#### 🔑 `keyfile.json` - DRM Decryption Keys

1. Install [Widevine L3 Decrypter](https://addons.mozilla.org/en-US/firefox/addon/widevine-l3-decrypter/) on **Firefox** (Chrome doesn't work properly)
2. Log in to Udemy on Firefox
3. Navigate to the course you want to download
4. Play any video lecture
5. While playing, click the Widevine L3 Decrypter extension
6. Click **Guess** and wait
7. Copy the **Key ID** and **Key** values
8. Create a file called `keyfile.json` with this format:

```json
{
  "KEY_ID_HERE": "KEY_HERE"
}
```

Example:
```json
{
  "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4": "0123456789abcdef0123456789abcdef"
}
```

#### ✅ Inline Auth Config (No Upload)

Prefer not to upload files? Use the inline auth section in the notebook:

- Edit `COOKIE_NETSCAPE` and `KEY_JSON` in section "6.1️⃣ Inline Cookie & Keys (No Upload)".
- The notebook writes `cookie.txt` and `keyfile.json` automatically.
- If these files already exist, the upload prompts will be skipped.

#### ✅ Auth Folder on Google Drive (Optional)

You can instead keep credentials in a Drive folder named `Udemy_Auth` (or any folder you choose) containing only `cookie.txt` and `keyfile.json`.

- Set `AUTH_FROM_DRIVE = True` and `AUTH_DRIVE_FOLDER = '/content/drive/MyDrive/Udemy_Auth'` in the "6.1️⃣ Inline Cookie & Keys" cell.
- The notebook will copy `cookie.txt` and `keyfile.json` from that Drive folder into the working project directory automatically.
- Use `AUTH_OVERWRITE = True` to force Drive files to replace inline values or existing files.

### Step 3: Run the Notebook

1. Open the notebook in Google Colab
2. Run each cell in order (Shift + Enter)
3. Upload `cookie.txt` when prompted (skipped if you used inline auth)
4. Upload `keyfile.json` when prompted (skipped if you used inline auth)
5. Configure the download settings in the configuration cell
6. Run the download cell

## 🎯 Alternative: Upload Project Files to Google Drive

If you prefer not to clone/upload every time, you can set up a permanent structure:

### One-Time Setup:

1. Create a folder in your Google Drive: `Udemy_Downloader`
2. Upload all `.py` files from this project to that folder
3. Create a `cookie.txt` and `keyfile.json` in that folder

### Modified Notebook Approach:

Use this code in a new Colab cell:

```python
from google.colab import drive
import os

# Idempotent Google Drive mount
if not os.path.isdir('/content/drive/MyDrive'):
   drive.mount('/content/drive', force_remount=False)
   print("✅ Google Drive mounted!")
else:
   print("✅ Google Drive already mounted.")

# Change to your project directory in Google Drive
PROJECT_DIR = '/content/drive/MyDrive/Udemy_Downloader'
os.chdir(PROJECT_DIR)

# Set output directory
OUTPUT_DIR = '/content/drive/MyDrive/Udemy_Courses'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"✅ Using project from: {PROJECT_DIR}")
print(f"📁 Output directory: {OUTPUT_DIR}")
```

Then install dependencies and run as normal.

## ⚙️ Configuration Options

Edit the configuration cell in the notebook:

```python
# Required
COURSE_URL = "https://www.udemy.com/course/YOUR-COURSE/learn"

# Optional
DOWNLOAD_CAPTIONS = True          # Download subtitles
DOWNLOAD_ASSETS = True            # Download PDFs, files, etc.
DOWNLOAD_QUIZZES = True           # Download quiz questions
VIDEO_QUALITY = "1080"            # "720", "1080", or "" for best
CAPTION_LANGUAGE = "en"           # "en" or "all"
CONCURRENT_DOWNLOADS = 15         # 1-30
CHAPTERS = "1,3-5,7"              # Specific chapters or "" for all
```

## 🔄 Download Multiple Courses

Use the "Download Multiple Courses" cell and add your course URLs:

```python
COURSES = [
    "https://www.udemy.com/course/python-bootcamp/learn",
    "https://www.udemy.com/course/web-development/learn",
    "https://www.udemy.com/course/data-science/learn",
]
```

## ⚠️ Important Limitations

### Google Colab Restrictions:

1. **Session Duration**: 
   - Maximum ~12 hours of runtime
   - Sessions disconnect after ~90 minutes of inactivity
   - Keep the browser tab open during downloads

2. **Storage**:
   - Check your Google Drive storage before starting
   - Large courses may require 10-50GB per course

3. **Speed**:
   - Download speed varies based on Colab's network
   - Typically 5-20 MB/s

4. **GPU Not Needed**:
   - You don't need GPU runtime for this
   - Use standard runtime to save resources

### Best Practices:

1. **Large Courses**: Download in batches using `--chapter "1-5"`
2. **Keep Alive**: Install [Colab Auto Refresh](https://chrome.google.com/webstore/detail/colab-auto-refresh/jpjppneklgjakgdpgobpddopmmbmbbff) extension
3. **Monitor Progress**: Check the output regularly
4. **Backup Keys**: Keep your `keyfile.json` safe, you'll need it for each course

## 🐛 Troubleshooting

### "Module not found" errors
- Re-run the dependency installation cells
- Restart runtime: **Runtime** → **Restart runtime**

### "Cookie.txt not found"
- Make sure you uploaded the file when prompted
- Check the file is named exactly `cookie.txt`

### "Could not find course data"
- Verify your cookies are fresh (re-export from browser)
- Make sure you're logged in to Udemy in your browser
- Ensure course URL ends with `/learn`

### "Key not found for [KEY_ID]"
- Extract Widevine keys using the browser extension
- Verify `keyfile.json` format is correct
- Keys must be added for each course separately

### Session disconnected
- Colab has idle timeout (~90 minutes)
- Keep browser tab active
- Use chapter filtering for very large courses

### Out of storage
- Check Google Drive storage: [drive.google.com/settings/storage](https://drive.google.com/settings/storage)
- Delete old files or upgrade storage
- Download one course at a time

## 📚 Example Workflow

1. Open Colab notebook
2. Mount Google Drive (Cell 1)
3. Install dependencies (Cells 2-3)
4. Upload cookie.txt and keyfile.json (Cell 4-5)
5. Configure settings:
```python
COURSE_URL = "https://www.udemy.com/course/python-complete/learn"
DOWNLOAD_CAPTIONS = True
DOWNLOAD_ASSETS = True
VIDEO_QUALITY = "1080"
```
6. Run download cell
7. Wait for completion (check progress in output)
8. Find your course in Google Drive: `Udemy_Courses/[Course Name]/`

## 💡 Advanced Tips

### Download Only Specific Lectures
```python
CHAPTERS = "1,3,5"  # Only chapters 1, 3, and 5
```

### Save Bandwidth with Lower Quality
```python
VIDEO_QUALITY = "720"  # Instead of 1080p
SKIP_HLS = True        # Skip some high-quality streams
```

### Get Course Info First
Run the "View Course Info Only" cell to see:
- Total chapters
- Total lectures
- Estimated size

### Batch Processing
For very large courses, process in parts:
```python
# Session 1
CHAPTERS = "1-10"

# Session 2
CHAPTERS = "11-20"

# And so on...
```

## 🔗 Useful Links

- [Google Colab](https://colab.research.google.com/)
- [Cookies Editor Extension](https://cookie-editor.com/)
- [Widevine L3 Decrypter (Firefox)](https://addons.mozilla.org/en-US/firefox/addon/widevine-l3-decrypter/)
- [Google Drive Storage](https://drive.google.com/settings/storage)

## ⚖️ Legal Disclaimer

This tool is provided for **educational purposes only**. Downloading courses from Udemy may violate their Terms of Service. Use at your own risk. Only download courses you have legally purchased.

---

**Happy Learning! 📚**
