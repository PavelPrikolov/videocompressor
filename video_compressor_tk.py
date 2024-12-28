import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog
import ffmpeg
from tkinterdnd2 import DND_FILES, TkinterDnD

class VideoCompressor:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Compressor")
        self.root.geometry("400x300")
        
        # Configure style
        style = ttk.Style()
        style.configure('TButton', padding=6)
        style.configure('TLabel', padding=6)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Drop zone
        self.drop_label = ttk.Label(
            main_frame,
            text="Drag and drop video file here\nor click Select File button",
            wraplength=300,
            justify="center"
        )
        self.drop_label.grid(row=0, column=0, pady=20, sticky=(tk.W, tk.E))
        
        # Configure drag and drop
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Target size selection
        size_frame = ttk.Frame(main_frame)
        size_frame.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Label(size_frame, text="Target Size (MB):").grid(row=0, column=0, padx=5)
        self.size_var = tk.StringVar(value="50")
        size_spinbox = ttk.Spinbox(
            size_frame,
            from_=1,
            to=2000,
            textvariable=self.size_var,
            width=10
        )
        size_spinbox.grid(row=0, column=1, padx=5)
        
        # Select file button
        self.select_button = ttk.Button(
            main_frame,
            text="Select File",
            command=self.select_file
        )
        self.select_button.grid(row=2, column=0, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate'
        )
        self.progress.grid(row=3, column=0, pady=10, sticky=(tk.W, tk.E))
        self.progress.grid_remove()
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="",
            wraplength=300,
            justify="center"
        )
        self.status_label.grid(row=4, column=0, pady=10)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

    def handle_drop(self, event):
        file_path = event.data
        if file_path:
            # Remove curly braces if present (Windows DnD peculiarity)
            file_path = file_path.strip('{}')
            if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')):
                self.compress_video(file_path)
            else:
                self.status_label["text"] = "Please drop a video file"

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.compress_video(file_path)

    def compress_video(self, input_path):
        try:
            # Get target size in bytes
            target_size_mb = int(self.size_var.get())
            target_size_bytes = target_size_mb * 1024 * 1024
            
            # Show progress
            self.progress.grid()
            self.progress.start(10)
            self.status_label["text"] = "Compressing video..."
            self.root.update()
            
            # Get input video information
            probe = ffmpeg.probe(input_path)
            duration = float(probe['format']['duration'])
            
            # Calculate target bitrate (90% of target size to ensure final size is under limit)
            target_bitrate = int((target_size_bytes * 8 * 0.9) / duration)
            
            # Prepare output filename
            filename, ext = os.path.splitext(input_path)
            output_path = f"{filename}_compressed{ext}"
            
            # Run compression
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(stream, output_path,
                                 video_bitrate=target_bitrate,
                                 acodec='aac',
                                 audio_bitrate='128k')
            ffmpeg.run(stream, overwrite_output=True)
            
            # Update UI on completion
            self.progress.stop()
            self.progress.grid_remove()
            self.status_label["text"] = f"Compression complete!\nSaved to: {output_path}"
            
        except Exception as e:
            self.progress.stop()
            self.progress.grid_remove()
            self.status_label["text"] = f"Error: {str(e)}"

def main():
    root = TkinterDnD.Tk()
    app = VideoCompressor(root)
    root.mainloop()

if __name__ == '__main__':
    main()
