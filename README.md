# Video Compressor

A simple desktop application for compressing video files with a drag-and-drop interface.

## Features
- Drag and drop video files directly onto the application
- Choose target file size in megabytes
- Support for common video formats (MP4, AVI, MOV, MKV, WMV)
- Simple and intuitive interface
- Progress indication during compression

## Requirements (for video_compressor.py)
- Python 3.8 or higher
- FFmpeg installed on your system
- PyQt6
- ffmpeg-python

## Installation

1. Install FFmpeg on your system if not already installed
2. Install the required Python packages:
```
pip install -r requirements.txt
```

## Usage

1. Run the application:
```
python video_compressor.py
```


## Compiling a Python file into an executable

Do compilation in any way you like, I personally did it through auto-py-to-exe and I will write how at the bottom:

```
python -m venv venv
pip install -r requirements.txt
cmd /c venv\Scripts\activate.bat && pip install wxPython ffmpeg-python auto-py-to-exe
cmd /c venv\Scripts\activate.bat && auto-py-to-exe
```
1. Script Location: Select video_compressor_wx.py
2. Onefile: Select "One File"
3. Console Window: Select "Window Based (hide the console)"
4. Additional Files: Make sure to add any icon file if you have one
5. Advanced:
Enable the following options:
--clean
--uac-admin (to ensure proper file access permissions)
6. After configuring these settings, click "Convert .py to .exe". The executable will be created in the "output" directory.


## Supported Formats
- MP4
- AVI
- MOV
- MKV
- WMV
