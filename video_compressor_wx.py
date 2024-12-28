import os
import sys
import wx
import ffmpeg

class DragDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        if len(filenames) == 1:
            file_path = filenames[0]
            if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')):
                self.window.compress_video(file_path)
            else:
                self.window.status_text.SetLabel("Please drop a video file")
        return True

class VideoCompressor(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Video Compressor', size=(400, 400))
        self.init_ui()

    def init_ui(self):
        # Create main panel
        panel = wx.Panel(self)
        
        # Create vertical box sizer
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Drop zone
        self.drop_zone = wx.StaticText(
            panel,
            label="Drag and drop video file here\nor click Select File button",
            style=wx.ALIGN_CENTER_HORIZONTAL | wx.ST_NO_AUTORESIZE
        )
        self.drop_zone.SetMinSize((380, 100))
        self.drop_zone.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        # Enable drag and drop
        dt = DragDropTarget(self)
        self.drop_zone.SetDropTarget(dt)
        
        # Target size selection
        size_box = wx.BoxSizer(wx.HORIZONTAL)
        size_label = wx.StaticText(panel, label="Target Size (MB):")
        self.size_spin = wx.SpinCtrl(panel, value="10")  # Default to 10MB
        self.size_spin.SetRange(1, 2000)
        size_box.Add(size_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        size_box.Add(self.size_spin, 0, wx.EXPAND)
        
        # Select file button
        self.select_button = wx.Button(panel, label="Select File")
        self.select_button.Bind(wx.EVT_BUTTON, self.on_select_file)
        
        # Progress bar
        self.progress = wx.Gauge(panel, range=100, style=wx.GA_HORIZONTAL)
        self.progress.Hide()
        
        # Status text
        self.status_text = wx.StaticText(panel, label="")
        self.status_text.Wrap(380)
        
        # Add widgets to vertical sizer
        vbox.AddSpacer(20)
        vbox.Add(self.drop_zone, 0, wx.EXPAND | wx.ALL, 10)
        vbox.Add(size_box, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        vbox.Add(self.select_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        vbox.Add(self.progress, 0, wx.EXPAND | wx.ALL, 10)
        vbox.Add(self.status_text, 0, wx.EXPAND | wx.ALL, 10)
        
        # Set sizer for panel
        panel.SetSizer(vbox)
        
        # Center window
        self.Center()

        # Process command line arguments if any
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if os.path.isfile(file_path) and file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')):
                self.compress_video(file_path)

    def on_select_file(self, event):
        with wx.FileDialog(
            self,
            "Select Video File",
            wildcard="Video files (*.mp4;*.avi;*.mov;*.mkv;*.wmv)|*.mp4;*.avi;*.mov;*.mkv;*.wmv",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return
            file_path = file_dialog.GetPath()
            self.compress_video(file_path)

    def compress_video(self, input_path):
        try:
            # Get target size in bytes (fixed at 10MB)
            target_size_mb = 10  # Force 10MB target size
            target_size_bytes = target_size_mb * 1024 * 1024
            
            # Show progress
            self.progress.Show()
            self.progress.Pulse()
            self.status_text.SetLabel("Compressing video...")
            wx.GetApp().Yield()
            
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
            self.progress.Hide()
            self.status_text.SetLabel(f"Compression complete!\nSaved to: {output_path}")
            
            # If launched with command line argument, close after completion
            if len(sys.argv) > 1:
                wx.CallAfter(self.Close)
            
        except Exception as e:
            self.progress.Hide()
            self.status_text.SetLabel(f"Error: {str(e)}")
            # If launched with command line argument, close after error
            if len(sys.argv) > 1:
                wx.CallAfter(self.Close)

def main():
    app = wx.App()
    frame = VideoCompressor()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
