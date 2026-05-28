# VcSynk - Official HubSynk Video Converter Tool
# Developed by Saulomg2 (HubSynk Team)
# This tool is part of the HubSynk ecosystem.
# Website: https://hubsynk.pages.dev

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import threading
import time
from pathlib import Path
import shutil
import re 
import webbrowser

# --- Style Configuration ---
BG_DARK = "#1e1e1e"
BG_MEDIUM = "#2b2b2b"
FG_LIGHT = "#ffffff"
COLOR_PRIMARY = "#2196F3"
COLOR_SUCCESS = "#4CAF50"
COLOR_ERROR = "#f44336"
COLOR_ACCENT = "#FFC107" # Yellow for accent

# --- Text Strings (English) ---
TITLE_WINDOW = "VcSynk version 1.0"
TITLE_MAIN = "VcSynk - Video Converter"
SELECT_FILE_BUTTON = "📁 Select File(s)"
SELECT_OUTPUT_BUTTON = "📂 Select Output Folder"
NO_FILE_SELECTED = "No file selected"
CONVERSION_OPTIONS = "Conversion Options"
OUTPUT_FORMAT = "Output Format:"
COMPRESSION_PROFILE = "Compression Profile:"
AUDIO_CODEC = "Audio Codec:"
START_CONVERSION_BUTTON = "Start Conversion"
STOP_CONVERSION_BUTTON = "🔴 Stop Conversion"
CONVERTING_BUTTON = "Converting..."
WAITING_SELECTION = "Waiting for file selection..."
READY_TO_CONVERT = "Ready to convert. Select Compression Profile."
PROGRESS = "Progress:"
INFO_MP4 = "MP4 (H.264) is the most compatible format. CRF (Constant Rate Factor) controls quality: lower CRF = higher quality/size."
INFO_MKV = "MKV (H.265/HEVC) offers superior compression (smaller size) with similar quality to H.264, but requires more processing power."
INFO_WEBM = "WebM (VP9) is ideal for web. Offers good compression and is royalty-free. Compression is slower than H.264. Requires libvpx-vp9 codec."
INFO_WEBM_VP9_MISSING = "WebM (VP9) is ideal for web. **WARNING:** libvpx-vp9 codec was not detected in your FFmpeg. VP9 profiles have been disabled. Install FFmpeg with VP9 support to enable them."
INFO_MOV = "MOV (ProRes) is a high-quality editing codec. File size will be LARGER, but quality is preserved for editing."
CONVERSION_COMPLETE = "Conversion complete! Size reduction of"
CONVERSION_SUCCESS = "Video converted successfully!"
SAVED_TO = "Saved to:"
ORIGINAL_SIZE = "Original Size:"
FINAL_SIZE = "Final Size:"
SIZE_REDUCTION = "Reduction:"
ERROR_FFMPEG = "FFmpeg not found. Please install and add it to system PATH."
ERROR_TITLE = "Error - FFmpeg Required"
ERROR_CONVERSION = "Conversion failed. Return code:"
ERROR_UNEXPECTED = "Unexpected error:"
ERROR_CONVERSION_TITLE = "Conversion Error"
SUCCESS_TITLE = "Success"
READY_AGAIN = "Ready to convert again."
HW_CODEC_NVIDIA_H264 = "NVIDIA (NVENC H.264)"
HW_CODEC_NVIDIA_H265 = "NVIDIA (NVENC H.265)"
HW_CODEC_INTEL_H264 = "Intel (QSV H.264)"
HW_CODEC_INTEL_H265 = "Intel (QSV H.265)"
HW_CODEC_AMD_H264 = "AMD (AMF H.264)"
HW_CODEC_AMD_H265 = "AMD (AMF H.265)"
PROFILE_H264_BALANCED = "H.264 (Balanced - CRF 23)"
PROFILE_H264_QUALITY = "H.264 (Quality - CRF 18)"
PROFILE_H264_FAST = "H.264 (Fast - CRF 28)"
PROFILE_H265_BALANCED = "H.265/HEVC (Balanced - CRF 28)"
PROFILE_H265_QUALITY = "H.265/HEVC (Quality - CRF 23)"
PROFILE_H265_FAST = "H.265/HEVC (Fast - CRF 33)"
PROFILE_VP9_BALANCED = "VP9 (Balanced - CRF 30)"
PROFILE_VP9_QUALITY = "VP9 (Quality - CRF 20)"
PROFILE_VP9_FAST = "VP9 (Fast - CRF 40)"
PROFILE_VP9_MISSING = "VP9 (Codec not installed)"
PROFILE_PRORES_LT = "ProRes LT (Low Compression)"
PROFILE_PRORES_STANDARD = "ProRes Standard (Standard Quality)"
PROFILE_GPU = "GPU:"
FOOTER_TEXT = "VcSynk is part of the HubSynk ecosystem."
HUB_LINK_TEXT = "Official HubSynk Tool - Visit our website"
HUB_LINK_URL = "https://hubsynk.pages.dev"
LOG_FILENAME = "Hubsynk_converter.txt"

class VideoConverterApp:
    def __init__(self, root):
        self.conversion_errors = [] # List to store batch conversion errors
        self.root = root
        self.root.title(TITLE_WINDOW)
        self.root.geometry("750x820")  # Increased height for footer space
        self.root.configure(bg=BG_DARK)
        
        # Set window icon (.ico file)
        try:
            icon_path = Path(__file__).parent / "logo.ico"
            if icon_path.exists():
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Variable to control conversion stop
        self.stop_conversion_flag = threading.Event()
        
        # Try to set the icon (requires logo.png to be in the same directory or accessible)
        try:
            icon_path_png = Path(__file__).parent / "logo.png"
            if icon_path_png.exists():
                self.root.iconphoto(True, tk.PhotoImage(file=icon_path_png))
        except Exception:
            pass # Use default icon if logo.png is not found or fails to load

        self.current_files = [] # Changed to list for batch conversion
        self.output_format = tk.StringVar(value="mp4")
        self.compression_profile = tk.StringVar(value="h264_balanced")
        self.audio_codec = tk.StringVar(value="aac")  # CORREÇÃO: AAC ativo por padrão
        self.is_converting = False
        self.output_dir = tk.StringVar(value=str(Path.home() / "Videos" / "VcSynk_Output")) # Default output folder
        
        if not self.check_ffmpeg():
            messagebox.showerror(ERROR_TITLE, ERROR_FFMPEG)
            self.root.destroy()
            return
        
        self.available_hw_codecs = self.detect_hw_codecs()
        self.vp9_available = self.check_vp9_codec() # New: Check if VP9 is available
        
        self.setup_ui()
        
    def check_ffmpeg(self):
        return shutil.which('ffmpeg') is not None

    def check_vp9_codec(self):
        "Checks if libvpx-vp9 encoder is available in FFmpeg."
        try:
            result = subprocess.run(['ffmpeg', '-encoders'], capture_output=True, text=True, encoding='utf-8')
            return 'libvpx-vp9' in result.stdout
        except Exception:
            return False

    def detect_hw_codecs(self):
        "Detects available hardware codecs in FFmpeg."
        codecs = {}
        try:
            result = subprocess.run(['ffmpeg', '-codecs'], capture_output=True, text=True, encoding='utf-8')
            output = result.stdout
            
            if 'h264_nvenc' in output:
                codecs['h264_nvenc'] = HW_CODEC_NVIDIA_H264
            if 'hevc_nvenc' in output:
                codecs['hevc_nvenc'] = HW_CODEC_NVIDIA_H265
            if 'h264_qsv' in output:
                codecs['h264_qsv'] = HW_CODEC_INTEL_H264
            if 'hevc_qsv' in output:
                codecs['hevc_qsv'] = HW_CODEC_INTEL_H265
            if 'h264_amf' in output:
                codecs['h264_amf'] = HW_CODEC_AMD_H264
            if 'hevc_amf' in output:
                codecs['hevc_amf'] = HW_CODEC_AMD_H265
                
        except Exception as e:
            print(f"Could not detect hardware codecs: {e}")
        return codecs

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        # Style configurations
        style.configure('TFrame', background=BG_MEDIUM)
        style.configure('TLabel', background=BG_MEDIUM, foreground=FG_LIGHT)
        style.configure('TButton', background=COLOR_PRIMARY, foreground=FG_LIGHT, font=('Arial', 10, 'bold'))
        style.map('TButton', background=[('active', COLOR_PRIMARY)])
        style.configure('TProgressbar', background=COLOR_SUCCESS, troughcolor=BG_DARK)
        style.configure('TRadiobutton', background=BG_MEDIUM, foreground=FG_LIGHT)
        style.map('TRadiobutton', background=[('active', BG_MEDIUM)])
        style.configure('TCombobox', fieldbackground=BG_DARK, foreground=FG_LIGHT, selectbackground=COLOR_PRIMARY, selectforeground=FG_LIGHT)

        # FIX: Simple main frame without Canvas
        self.main_frame = tk.Frame(self.root, bg=BG_MEDIUM, padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        title = tk.Label(self.main_frame, text=TITLE_MAIN, 
                         font=("Arial", 18, "bold"), bg=BG_MEDIUM, fg=FG_LIGHT)
        title.pack(pady=(0, 20))
        
        # 1. File Selection (Batch Enabled)
        file_frame = tk.Frame(self.main_frame, bg=BG_MEDIUM)
        file_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(file_frame, text=SELECT_FILE_BUTTON, 
                  command=self.select_files, font=("Arial", 11, "bold"),
                  bg=COLOR_PRIMARY, fg=FG_LIGHT, padx=10, pady=5,
                  cursor="hand2", relief=tk.FLAT).pack(side=tk.LEFT)
        
        self.file_info_label = tk.Label(file_frame, text=NO_FILE_SELECTED,
                                        font=("Arial", 10), bg=BG_MEDIUM, fg="#cccccc")
        self.file_info_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # 1.5 Output Folder Selection
        output_frame = tk.Frame(self.main_frame, bg=BG_MEDIUM)
        output_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(output_frame, text=SELECT_OUTPUT_BUTTON, 
                  command=self.select_output_folder, font=("Arial", 11, "bold"),
                  bg=COLOR_ACCENT, fg=BG_DARK, padx=10, pady=5,
                  cursor="hand2", relief=tk.FLAT).pack(side=tk.LEFT)
        
        self.output_info_label = tk.Label(output_frame, textvariable=self.output_dir,
                                        font=("Arial", 10), bg=BG_MEDIUM, fg=FG_LIGHT, anchor='w')
        self.output_info_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # 2. Conversion Options (Format, Profile, and Audio)
        options_frame = tk.Frame(self.main_frame, bg=BG_MEDIUM)
        options_frame.pack(fill=tk.X, pady=10)

        # Output Format
        tk.Label(options_frame, text=OUTPUT_FORMAT, 
                 font=("Arial", 11, "bold"), bg=BG_MEDIUM, fg=FG_LIGHT).pack(side=tk.LEFT, padx=(0, 10))
        
        self.formats = ["mp4", "mkv", "webm", "mov"]
        format_combobox = ttk.Combobox(options_frame, textvariable=self.output_format, 
                                       values=self.formats, state="readonly", width=8)
        format_combobox.pack(side=tk.LEFT)
        format_combobox.bind("<<ComboboxSelected>>", self.update_profile_options)

        # Audio Codec Selection (New)
        audio_frame = tk.Frame(self.main_frame, bg=BG_MEDIUM)
        audio_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(audio_frame, text=AUDIO_CODEC, 
                 font=("Arial", 11, "bold"), bg=BG_MEDIUM, fg=FG_LIGHT).pack(side=tk.LEFT, padx=(0, 10))
        
        # AAC Option (Now default)
        ttk.Radiobutton(audio_frame, text="AAC (Compatible)", variable=self.audio_codec, value="aac").pack(side=tk.LEFT, padx=5)
        
        # Opus Option
        ttk.Radiobutton(audio_frame, text="Opus (Quality/Size)", variable=self.audio_codec, value="opus").pack(side=tk.LEFT, padx=5)

        # Compression Profile
        tk.Label(self.main_frame, text=COMPRESSION_PROFILE, 
                 font=("Arial", 11, "bold"), bg=BG_MEDIUM, fg=FG_LIGHT).pack(anchor='w', pady=(10, 5))
        
        self.profile_frame = tk.Frame(self.main_frame, bg=BG_MEDIUM)
        self.profile_frame.pack(fill=tk.X, expand=True)

        # 3. Convert/Stop Button Frame (New)
        button_frame = tk.Frame(self.main_frame, bg=BG_MEDIUM)
        button_frame.pack(pady=20)
        
        self.convert_button = tk.Button(button_frame, text=START_CONVERSION_BUTTON, 
                                        command=self.start_conversion_thread, 
                                        font=("Arial", 12, "bold"),
                                        bg=COLOR_SUCCESS, fg=FG_LIGHT, padx=20, pady=8,
                                        cursor="hand2", relief=tk.FLAT, state=tk.DISABLED)
        self.convert_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(button_frame, text=STOP_CONVERSION_BUTTON, 
                                     command=self.stop_conversion, 
                                     font=("Arial", 12, "bold"),
                                     bg=COLOR_ERROR, fg=FG_LIGHT, padx=20, pady=8,
                                     cursor="hand2", relief=tk.FLAT, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # 4. Progress
        self.progress_label = tk.Label(self.main_frame, text=WAITING_SELECTION,
                                       font=("Arial", 10), bg=BG_MEDIUM, fg="#cccccc")
        self.progress_label.pack(fill=tk.X, pady=(10, 5))
        
        self.progress_bar = ttk.Progressbar(self.main_frame, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.pack(fill=tk.X)
        
        # 5. Additional Information (Profile Info)
        self.info_label = tk.Label(self.main_frame, text="", font=("Arial", 9, "italic"), bg=BG_MEDIUM, fg=COLOR_ACCENT, wraplength=700, justify=tk.LEFT)
        self.info_label.pack(fill=tk.X, pady=(10, 0))

        # 6. HubSynk Disclaimer and Link (New Section) - With more space
        hub_frame = tk.Frame(self.main_frame, bg=BG_MEDIUM)
        hub_frame.pack(fill=tk.X, pady=(30, 10))  # Increased vertical padding

        # Footer Text
        footer_label = tk.Label(hub_frame, text=FOOTER_TEXT, 
                                font=("Arial", 10, "italic"), bg=BG_MEDIUM, fg="#999999")
        footer_label.pack(side=tk.LEFT, padx=(0, 10))

        # HubSynk Link Button (Disguised)
        hub_link_button = tk.Button(hub_frame, text=HUB_LINK_TEXT, 
                                    command=self.open_hubsynk_link, 
                                    font=("Arial", 10, "bold", "underline"),
                                    bg=BG_MEDIUM, fg=COLOR_PRIMARY, bd=0, 
                                    cursor="hand2", relief=tk.FLAT, activebackground=BG_MEDIUM, activeforeground=COLOR_PRIMARY)
        hub_link_button.pack(side=tk.LEFT)
        
        # Extra space at the bottom to ensure footer is not cut off
        spacer_frame = tk.Frame(self.main_frame, bg=BG_MEDIUM, height=10)
        spacer_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Initial profile update
        self.update_profile_options()


    def update_profile_options(self, event=None):
        "Updates compression profile options based on the output format."
        for widget in self.profile_frame.winfo_children():
            widget.destroy()
            
        output_ext = self.output_format.get()
        
        profiles = {}
        info_text = ""
        
        if output_ext == "mp4":
            profiles = {
                "h264_balanced": PROFILE_H264_BALANCED,
                "h264_quality": PROFILE_H264_QUALITY,
                "h264_fast": PROFILE_H264_FAST,
            }
            info_text = INFO_MP4
        elif output_ext == "mkv":
            profiles = {
                "h265_balanced": PROFILE_H265_BALANCED,
                "h265_quality": PROFILE_H265_QUALITY,
                "h265_fast": PROFILE_H265_FAST,
            }
            info_text = INFO_MKV
        elif output_ext == "webm":
            if self.vp9_available:
                profiles = {
                    "vp9_balanced": PROFILE_VP9_BALANCED,
                    "vp9_quality": PROFILE_VP9_QUALITY,
                    "vp9_fast": PROFILE_VP9_FAST,
                }
                info_text = INFO_WEBM
            else:
                profiles = {
                    "vp9_missing": PROFILE_VP9_MISSING,
                }
                info_text = INFO_WEBM_VP9_MISSING
        elif output_ext == "mov":
            profiles = {
                "prores_lt": PROFILE_PRORES_LT,
                "prores_standard": PROFILE_PRORES_STANDARD,
            }
            info_text = INFO_MOV
        
        # Add hardware acceleration options
        for value, name in self.available_hw_codecs.items():
            profiles[value] = f"{PROFILE_GPU} {name}"
            
        # Ensure the selected profile is still valid
        if self.compression_profile.get() not in profiles or self.compression_profile.get() == "vp9_missing":
            self.compression_profile.set(list(profiles.keys())[0] if profiles else "")

        # Create Radio Buttons
        for value, text in profiles.items():
            state = tk.DISABLED if value == "vp9_missing" else tk.NORMAL
            ttk.Radiobutton(self.profile_frame, text=text, variable=self.compression_profile, value=value, state=state).pack(anchor='w', padx=5, pady=2)
            
        self.info_label.config(text=info_text)

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=self.output_dir.get()
        )
        if folder_path:
            self.output_dir.set(folder_path)

    def select_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Video File(s) for Batch Conversion",
            filetypes=[("Video Files", "*.mp4 *.webm *.avi *.mov *.mkv *.flv *.wmv"), ("All Files", "*.*")]
        )
        if file_paths:
            self.current_files = [Path(p) for p in file_paths]
            
            # Create default output folder if it doesn't exist
            default_output = Path.home() / "Videos" / "VcSynk_Output"
            if not default_output.exists():
                default_output.mkdir(parents=True, exist_ok=True)
            self.output_dir.set(str(default_output))

            if len(self.current_files) == 1:
                file_path = self.current_files[0]
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                info_text = f"{file_path.name} ({file_size_mb:.2f} MB)"
            else:
                info_text = f"{len(self.current_files)} files selected for batch conversion."
                
            self.file_info_label.config(text=info_text, fg=FG_LIGHT)
            self.progress_label.config(text=READY_TO_CONVERT)
            self.convert_button.config(state=tk.NORMAL)
            self.progress_bar['value'] = 0
            self.update_profile_options()

    def get_video_duration(self, filepath):
        try:
            ffprobe_path = shutil.which('ffprobe') or 'ffprobe'
            cmd = [ffprobe_path, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(filepath)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
            return float(result.stdout.strip())
        except Exception:
            return 0.0

    def start_conversion_thread(self):
        if not self.current_files:
            messagebox.showwarning("Warning", "Please select one or more files first.")
            return

        if self.is_converting:
            return

        # Check for VP9 profile selection when codec is missing
        if self.output_format.get() == "webm" and not self.vp9_available:
             if self.compression_profile.get() == "vp9_missing":
                 messagebox.showerror("Codec Error", "VP9 codec (libvpx-vp9) is not installed in your FFmpeg. Please select another format or install the codec.")
                 return
        
        # Reset stop flag and error list
        self.stop_conversion_flag.clear()
        self.conversion_errors = []
        self.is_converting = True
        
        # Update buttons
        self.convert_button.config(state=tk.DISABLED, text=CONVERTING_BUTTON)
        self.stop_button.config(state=tk.NORMAL)
        
        self.progress_label.config(text="Starting conversion...")
        self.progress_bar['value'] = 0
        
        # Start the batch conversion in a separate thread
        threading.Thread(target=self.batch_convert_videos, daemon=True).start()

    def stop_conversion(self):
        """Sets the flag to stop the current conversion process."""
        if self.is_converting:
            self.stop_conversion_flag.set()
            self.root.after(0, self.progress_label.config, {'text': "Conversion stopped. Finishing process..."})
            self.stop_button.config(state=tk.DISABLED)

    def batch_convert_videos(self):
        total_files = len(self.current_files)
        successful_conversions = 0
        
        for i, input_file_path in enumerate(self.current_files):
            if self.stop_conversion_flag.is_set():
                break # Exit loop if stop flag is active

            # Update UI for current file
            self.root.after(0, self.progress_label.config, {'text': f"File {i+1}/{total_files}: Converting {input_file_path.name}..."})
            self.root.after(0, self.progress_bar.config, {'value': 0, 'mode': 'determinate'})
            
            try:
                if self._convert_single_video(input_file_path, i, total_files):
                    successful_conversions += 1
            except Exception as e:
                # Only log error, no pop-up
                self.conversion_errors.append(f"File {input_file_path.name}: {ERROR_UNEXPECTED} {e}")
                
        # Final UI update after batch completion
        self.root.after(0, self.batch_conversion_complete, successful_conversions, total_files)


    def _convert_single_video(self, input_path: Path, file_index: int, total_files: int):
        if self.stop_conversion_flag.is_set():
            return False # Stop current file conversion

        if not input_path.exists():
            self.conversion_errors.append(f"File {input_path.name}: Input file not found.")
            return False
            
        output_ext = self.output_format.get()
        compression_profile = self.compression_profile.get()
        audio_codec_choice = self.audio_codec.get() # New: Audio codec choice
        output_dir = Path(self.output_dir.get())
        
        # Define the output file name
        output_name = f"{input_path.stem}_VcSynk.{output_ext}"
        output_path = output_dir / output_name

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        duration = self.get_video_duration(input_path)
        
        # --- Logic to build the FFmpeg command based on the Profile ---
        ffmpeg_cmd = ['ffmpeg', '-i', str(input_path)]
        
        # Audio Parameters (New: Based on user choice)
        if audio_codec_choice == "opus":
            audio_codec = ['-c:a', 'libopus', '-b:a', '96k'] # Opus with reasonable bitrate
        else: # Default to AAC (safer and more compatible)
            audio_codec = ['-c:a', 'aac', '-b:a', '128k']
        
        # Codec and Parameters Logic
        if compression_profile.startswith("h264_"):
            # MP4 (H.264)
            crf = {'h264_balanced': '23', 'h264_quality': '18', 'h264_fast': '28'}[compression_profile]
            ffmpeg_cmd.extend(['-c:v', 'libx264', '-preset', 'medium', '-crf', crf])
            
        elif compression_profile.startswith("h265_"):
            # MKV (H.265/HEVC)
            crf = {'h265_balanced': '28', 'h265_quality': '23', 'h265_fast': '33'}[compression_profile]
            ffmpeg_cmd.extend(['-c:v', 'libx265', '-preset', 'medium', '-crf', crf])
            
        elif compression_profile.startswith("vp9_"):
            # WebM (VP9)
            crf = {'vp9_balanced': '30', 'vp9_quality': '20', 'vp9_fast': '40'}[compression_profile]
            ffmpeg_cmd.extend(['-c:v', 'libvpx-vp9', '-crf', crf, '-b:v', '0'])
            
        elif compression_profile.startswith("prores_"):
            # MOV (ProRes)
            profile = {'prores_lt': 'prores_ks', 'prores_standard': 'prores_ks'}[compression_profile]
            vprofile = {'prores_lt': 'lt', 'prores_standard': 'standard'}[compression_profile]
            ffmpeg_cmd.extend(['-c:v', profile, '-profile:v', vprofile])
            # ProRes uses pcm_s16le for editing audio
            audio_codec = ['-c:a', 'pcm_s16le']
            
        elif compression_profile in self.available_hw_codecs:
            # Hardware Acceleration (GPU)
            codec = compression_profile
            ffmpeg_cmd.extend(['-c:v', codec])
            
            if 'nvenc' in codec:
                ffmpeg_cmd.extend(['-preset', 'p5', '-cq', '23']) 
            elif 'qsv' in codec:
                ffmpeg_cmd.extend(['-global_quality', '23'])
            elif 'amf' in codec:
                ffmpeg_cmd.extend(['-quality', 'balanced'])
        
        # If profile is "vp9_missing", do nothing (check prevents reaching here)
        if compression_profile == "vp9_missing":
            self.conversion_errors.append(f"File {input_path.name}: VP9 conversion attempt without installed codec.")
            return False

        # Add audio and progress commands
        ffmpeg_cmd.extend(audio_codec)
        ffmpeg_cmd.extend([
            '-progress', 'pipe:1',         # Progress
            '-y',                          # Overwrite
            str(output_path)
        ])
        
        print(f"--- FFmpeg Command for File {file_index+1}/{total_files} ---")
        print(" ".join(f'"{arg}"' if " " in arg else arg for arg in ffmpeg_cmd))
        print("---------------------------------")

        process = None
        try:
            process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1, encoding='utf-8', errors='ignore')
            
            while process.poll() is None:
                if self.stop_conversion_flag.is_set():
                    process.terminate() # Try to terminate FFmpeg process
                    time.sleep(0.5)
                    if process.poll() is None:
                        process.kill() # If not terminated, kill it
                    return False # Return False to indicate failure/interruption
                    
                line = process.stdout.readline()
                if not line:
                    break
                    
                # Use regex to find time=XX:XX:XX.XX
                time_match = re.search(r'time=(\d{2}:\d{2}:\d{2}\.\d{2})', line)
                
                if time_match:
                    time_str = time_match.group(1)
                    # Convert time string to seconds
                    h, m, s = map(float, time_str.split(':'))
                    current_time = h * 3600 + m * 60 + s
                    
                    if duration > 0:
                        progress_percent = (current_time / duration) * 100
                        # Update UI on the main thread
                        self.root.after(0, self.update_progress, progress_percent, current_time, duration, file_index, total_files)
                
                # Capture error/warning messages
                elif "error" in line.lower() or "failed" in line.lower():
                    print(f"FFmpeg Output: {line.strip()}")
            
            process.wait()
            if process.returncode == 0:
                return True
            else:
                # Read remaining output for error details
                error_output = process.stdout.read() if process.stdout else ""
                error_message = f"{ERROR_CONVERSION} {process.returncode}. Output: {error_output.strip()}"
                self.conversion_errors.append(f"File {input_path.name}: {error_message}")
                return False
                
        except FileNotFoundError:
            error_message = ERROR_FFMPEG
            self.conversion_errors.append(f"File {input_path.name}: {error_message}")
            return False
        except Exception as e:
            error_message = f"{ERROR_UNEXPECTED} {e}"
            self.conversion_errors.append(f"File {input_path.name}: {error_message}")
            return False
        finally:
            if process and process.poll() is None:
                process.terminate()
                
    def update_progress(self, percent, current_time, duration, file_index, total_files):
        self.progress_bar['value'] = percent
        
        # Format time
        time_elapsed = time.strftime('%H:%M:%S', time.gmtime(current_time))
        time_total = time.strftime('%H:%M:%S', time.gmtime(duration))
        
        # Update label
        self.progress_label.config(text=f"File {file_index+1}/{total_files}: {percent:.1f}% completed. Time: {time_elapsed} / {time_total}")

    def batch_conversion_complete(self, successful_conversions, total_files):
        self.is_converting = False
        self.convert_button.config(state=tk.NORMAL, text=START_CONVERSION_BUTTON)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 100
        
        # Conversion summary
        if self.stop_conversion_flag.is_set():
            # Conversion stopped by user
            messagebox.showinfo("Warning", f"Conversion stopped by user. {successful_conversions} of {total_files} files were completed.")
            self.progress_label.config(text=f"Conversion stopped. {successful_conversions} of {total_files} files completed.", fg=COLOR_ACCENT)
        elif successful_conversions == total_files:
            # Total success
            messagebox.showinfo(SUCCESS_TITLE, f"Batch conversion completed! All {total_files} files were converted successfully.")
            self.progress_label.config(text=f"Batch conversion completed. {successful_conversions}/{total_files} files converted successfully.", fg=COLOR_SUCCESS)
        else:
            # Partial success or total failure
            messagebox.showwarning("Warning", f"Batch conversion completed with {successful_conversions} of {total_files} files converted. {len(self.conversion_errors)} failures.")
            self.progress_label.config(text=f"Batch conversion completed. {successful_conversions}/{total_files} files converted. {len(self.conversion_errors)} failures.", fg=COLOR_ERROR)
            
        # Error log (New)
        if self.conversion_errors:
            self.ask_to_save_log()
            
        # If single file conversion and success, show details (kept)
        if total_files == 1 and successful_conversions == 1:
            input_path = self.current_files[0]
            output_path = Path(self.output_dir.get()) / f"{input_path.stem}_VcSynk.{self.output_format.get()}"
            
            original_size = os.path.getsize(input_path)
            final_size = os.path.getsize(output_path)
            
            reduction_percent = 100 - (final_size / original_size) * 100
            
            info_text = (
                f"{CONVERSION_COMPLETE} {reduction_percent:.2f}%.\n"
                f"{ORIGINAL_SIZE} {original_size / (1024 * 1024):.2f} MB\n"
                f"{FINAL_SIZE} {final_size / (1024 * 1024):.2f} MB\n"
                f"{SAVED_TO} {output_path.parent}"
            )
            self.progress_label.config(text=info_text, fg=COLOR_SUCCESS)
        
        # If conversion was stopped, state should be READY_TO_CONVERT if files are selected
        if not self.stop_conversion_flag.is_set():
            self.progress_label.config(text=READY_AGAIN, fg="#cccccc")
        else:
            self.progress_label.config(text=READY_TO_CONVERT, fg="#cccccc")


    def ask_to_save_log(self):
        """Asks the user if they want to save a log of failed conversions."""
        if messagebox.askyesno("Save Error Log", f"Do you want to save a log of the {len(self.conversion_errors)} files that failed conversion? The file will be saved as '{LOG_FILENAME}' in the output folder."):
            self.save_error_log()

    def save_error_log(self):
        """Saves the error log to the output directory."""
        log_path = Path(self.output_dir.get()) / LOG_FILENAME
        
        log_content = f"--- VcSynk Conversion Error Log - {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n\n"
        log_content += f"Total failures: {len(self.conversion_errors)}\n\n"
        
        for error in self.conversion_errors:
            log_content += f"{error}\n"
            
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
            messagebox.showinfo("Log Saved", f"Error log saved successfully at:\n{log_path}")
        except Exception as e:
            messagebox.showerror("Error Saving Log", f"Could not save error log:\n{e}")

    def show_error(self, message):
        # This function will no longer be called for batch conversion errors, only for critical initialization errors
        messagebox.showerror(ERROR_CONVERSION_TITLE, message)
        self.progress_label.config(text=READY_AGAIN, fg=COLOR_ERROR)
        self.is_converting = False
        self.convert_button.config(state=tk.NORMAL, text=START_CONVERSION_BUTTON)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        
    def open_hubsynk_link(self):
        webbrowser.open(HUB_LINK_URL)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverterApp(root)
    root.mainloop()