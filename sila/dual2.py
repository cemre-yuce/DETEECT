import paramiko
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import cv2
import numpy as np
import os
import threading
import traceback
from datetime import datetime


class RemoteStreamLauncher:
    def __init__(self, host, username, password, camera_configs):
        """
        Initialize with connection details and camera configurations
        
        Args:
        - host: IP address of the Raspberry Pi
        - username: SSH username
        - password: SSH password
        - camera_configs: List of dictionaries containing camera configurations
          Each config should have: script_path, port, save_dir
        """
        self.host = host
        self.username = username
        self.password = password
        self.camera_configs = camera_configs
        self.ssh = None
        self.start_time = None
        self.main_timings = {}  # Only store main timing components
        
        # Create directories for saving frames
        for config in camera_configs:
            save_dir = config.get('save_dir', 'captured_frames')
            os.makedirs(save_dir, exist_ok=True)

    def log_main_timing(self, phase, duration):
        """Log only main timing phases"""
        self.main_timings[phase] = duration
        print(f"MAIN PHASE: {phase} completed in {duration:.2f} seconds")

    def connect(self):
        """Establish SSH connection"""
        start_time = time.time()
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print(f"Connecting to {self.host}...")
            self.ssh.connect(self.host, username=self.username, password=self.password)
            print("SSH Connection established")
            success = True
        except Exception as e:
            print(f"SSH Connection Error: {e}")
            success = False
        
        duration = time.time() - start_time
        self.log_main_timing("SSH Connection", duration)
        return success

    def start_streams(self):
        """Start all camera stream scripts remotely"""
        if not self.ssh:
            if not self.connect():
                return False
        
        start_time = time.time()
        
        for config in self.camera_configs:
            script_path = config.get('script_path')
            if not script_path:
                continue
                
            try:
                # Kill any existing stream processes for this script
                kill_cmd = f'pkill -f "python3 {script_path}"'
                stdin, stdout, stderr = self.ssh.exec_command(kill_cmd)
                stderr_output = stderr.read().decode('utf-8').strip()
                if stderr_output:
                    print(f"Warning during kill command: {stderr_output}")
                time.sleep(1)  # Wait a bit longer to ensure processes are killed
                
                # Check if port is already in use
                port = config.get('port', 5000)
                check_port_cmd = f'netstat -tuln | grep :{port}'
                stdin, stdout, stderr = self.ssh.exec_command(check_port_cmd)
                port_in_use = stdout.read().decode('utf-8').strip()
                if port_in_use:
                    print(f"Warning: Port {port} appears to be in use already:")
                    print(port_in_use)
                    # Force kill any process on that port
                    self.ssh.exec_command(f'fuser -k {port}/tcp')
                    time.sleep(1)
                
                # Start the stream script in the background with output logging
                print(f"Starting stream: {script_path}")
                log_file = f"/tmp/stream_{port}.log"
                command = f'nohup python3 {script_path} > {log_file} 2>&1 &'
                stdin, stdout, stderr = self.ssh.exec_command(command)
                stderr_output = stderr.read().decode('utf-8').strip()
                if stderr_output:
                    print(f"Warning starting script: {stderr_output}")
                
                # Check if script started successfully by checking for errors in the log
                time.sleep(2)  # Give time for script to start and write to log
                stdin, stdout, stderr = self.ssh.exec_command(f'cat {log_file}')
                log_content = stdout.read().decode('utf-8').strip()
                if "Error" in log_content or "error" in log_content:
                    print(f"Warning: Possible error in script startup: {log_content}")
                
            except Exception as e:
                print(f"Error starting stream {script_path}: {e}")
                return False
        
        duration = time.time() - start_time
        self.log_main_timing("Remote Stream Launch", duration)
        return True

    def process_stream(self, config, stop_event, camera_timings):
        """
        Process a single remote stream with frame capture
        
        Args:
        - config: Dictionary with stream configuration
        - stop_event: Threading event to signal when to stop
        - camera_timings: Dictionary to store camera-specific timings
        """
        port = config.get('port', 5000)
        save_dir = config.get('save_dir', 'captured_frames')
        save_interval = config.get('save_interval', 0.01)  # More frequent saves
        max_frames = config.get('max_frames', 50000)
        camera_name = config.get('name', f'camera_{port}')
        
        stream_url = f'http://{self.host}:{port}/video_feed'
        print(f"[{camera_name}] Connecting to {stream_url}")
        
        # Track camera-specific timing
        connection_start = time.time()
        
        # Create a session with retry capability
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        
        try:
            # First try a quick HEAD request to check connectivity
            try:
                head_response = session.head(stream_url, timeout=2)
                print(f"[{camera_name}] HEAD request status: {head_response.status_code}")
            except Exception as e:
                print(f"[{camera_name}] HEAD request failed (this is often normal): {e}")
            
            # Connect to stream with increased timeout
            stream = session.get(stream_url, stream=True, timeout=5)
            
            connect_duration = time.time() - connection_start
            camera_timings["connection"] = connect_duration
            
            if stream.status_code != 200:
                print(f"[{camera_name}] Error: Status code {stream.status_code}")
                return
                
            print(f"[{camera_name}] Connected to stream")
            
            # Start processing timer
            processing_start = time.time()
            
            bytes_data = bytes()
            frame_count = 0
            last_save_time = time.time()
            
            window_name = f'Stream - {camera_name}'
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

            # Use a chunk iterator with a timeout
            chunk_iter = stream.iter_content(chunk_size=4096)
            
            while not stop_event.is_set():
                current_time = time.time()
                
                # Check if 6 seconds have elapsed since program start
                if self.start_time and (current_time - self.start_time >= 6.0):
                    print(f"[{camera_name}] 6 second time limit reached")
                    break
                
                try:
                    # Set a timeout for getting the next chunk
                    chunk = next(chunk_iter)
                except StopIteration:
                    print(f"[{camera_name}] End of stream")
                    break
                except requests.exceptions.RequestException as e:
                    print(f"[{camera_name}] Stream connection error: {e}")
                    break
                except Exception as e:
                    print(f"[{camera_name}] Error reading stream: {e}")
                    break
                    
                if not chunk:
                    continue
                    
                bytes_data += chunk
                a = bytes_data.find(b'\xff\xd8')
                b = bytes_data.find(b'\xff\xd9')
                
                if a != -1 and b != -1:
                    jpg_data = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]
                    
                    # Decode frame
                    try:
                        frame = cv2.imdecode(np.frombuffer(jpg_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            # Display frame
                            cv2.imshow(window_name, frame)
                            
                            # Frame capture logic
                            if current_time - last_save_time >= save_interval:
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                                filename = os.path.join(save_dir, f'frame_{timestamp}.jpg')
                                
                                cv2.imwrite(filename, frame)
                                last_save_time = current_time
                                frame_count += 1
                            
                            # Process key events faster
                            key = cv2.waitKey(1) & 0xFF
                            if key == ord('q'):
                                stop_event.set()
                                break
                    except Exception as e:
                        print(f"[{camera_name}] Error processing frame: {e}")
            
            # Record processing time
            processing_duration = time.time() - processing_start
            camera_timings["processing"] = processing_duration
            camera_timings["frames_captured"] = frame_count
            
        except requests.exceptions.ConnectionError as e:
            print(f"[{camera_name}] Stream connection error: {e}")
        except Exception as e:
            print(f"[{camera_name}] Stream error: {e}")
            traceback.print_exc()  # Print the full traceback for debugging
        finally:
            try:
                cv2.destroyWindow(window_name)
            except:
                pass
            print(f"[{camera_name}] Stream stopped")

    def process_all_streams(self):
        """Process all streams concurrently using threads"""
        threads = []
        stop_event = threading.Event()
        camera_timings = {}
        
        # Set the start time for the 6-second timer
        self.start_time = time.time()
        stream_connection_start = time.time()
        
        try:
            # Start threads for each stream
            for config in self.camera_configs:
                camera_name = config.get('name', f'camera_{config.get("port", 5000)}')
                camera_timings[camera_name] = {}
                
                thread = threading.Thread(
                    target=self.process_stream,
                    args=(config, stop_event, camera_timings[camera_name]),
                    name=f"Thread-{camera_name}"
                )
                thread.daemon = True
                threads.append(thread)
                thread.start()
                
                # Add a bit more delay between thread starts to avoid overwhelming connections
                time.sleep(0.5)
            
            # Add timed stop after 6 seconds
            threading.Timer(6.0, lambda: stop_event.set()).start()
            
            # Wait for all threads to complete or timeout
            main_end_time = time.time() + 7.0  # Add 1 second buffer
            while any(thread.is_alive() for thread in threads):
                if time.time() >= main_end_time:
                    print("Hard timeout reached, forcing exit")
                    break
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nProgram interrupted")
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()  # Print the full traceback for debugging
        finally:
            # Signal all threads to stop
            stop_event.set()
            
            # Give threads a short time to finish
            for thread in threads:
                if thread.is_alive():
                    thread.join(timeout=1.0)
                    
            cv2.destroyAllWindows()
            
            # Log video streaming phase timing
            stream_duration = time.time() - stream_connection_start
            self.log_main_timing("Video Streaming and Processing", stream_duration)
            
            # Log camera-specific timing
            for camera_name, timing in camera_timings.items():
                conn_time = timing.get("connection", 0)
                proc_time = timing.get("processing", 0)
                frames = timing.get("frames_captured", 0)
                print(f"{camera_name}: Connection: {conn_time:.2f}s, Processing: {proc_time:.2f}s, Frames: {frames}")
            
            print("All streams stopped.")
            self.print_timing_summary()
    
    def print_timing_summary(self):
        """Print a summary of all main timing components"""
        print("\n===== MAIN TIMING COMPONENTS =====")
        total = 0
        for phase, duration in self.main_timings.items():
            print(f"{phase}: {duration:.2f} seconds")
            total += duration
        
        program_duration = time.time() - self.start_time + self.main_timings.get("SSH Connection", 0) + self.main_timings.get("Remote Stream Launch", 0)
        print(f"Total Program Duration: {program_duration:.2f} seconds")
        print("=================================\n")
    
    def check_stream_status(self):
        """Check status of the stream servers on the RPi"""
        if not self.ssh:
            if not self.connect():
                return False
                
        print("\nChecking stream server status...")
        
        for config in self.camera_configs:
            port = config.get('port', 5000)
            camera_name = config.get('name', f'camera_{port}')
            
            # Check if process is running
            script_path = config.get('script_path')
            stdin, stdout, stderr = self.ssh.exec_command(f'pgrep -f "python3 {script_path}"')
            pid = stdout.read().decode('utf-8').strip()
            
            if pid:
                print(f"[{camera_name}] Process is running with PID: {pid}")
            else:
                print(f"[{camera_name}] Process is NOT running")
            
            # Check if port is open
            stdin, stdout, stderr = self.ssh.exec_command(f'netstat -tuln | grep :{port}')
            port_info = stdout.read().decode('utf-8').strip()
            
            if port_info:
                print(f"[{camera_name}] Port {port} is OPEN: {port_info}")
            else:
                print(f"[{camera_name}] Port {port} is NOT listening")
                
        return True


def main():
    # Replace with your specific details
    RPI_IP = '169.254.91.42'
    USERNAME = 'talha'
    PASSWORD = 'talha'
    
    # Define camera configurations with faster intervals
    camera_configs = [
        {
            'name': 'camera',
            'script_path': '/home/talha/Desktop/stream.py',
            'port': 5000,
            'save_dir': 'captured_frames',
            'save_interval': 0.01,  # Faster saving
            'max_frames': 50000
        },
        {
            'name': 'camera1',
            'script_path': '/home/talha/Desktop/stream1.py',
            'port': 5001,
            'save_dir': 'captured_frames1',
            'save_interval': 0.01,  # Faster saving
            'max_frames': 50000
        }
    ]
    
    # Create stream launcher
    launcher = RemoteStreamLauncher(RPI_IP, USERNAME, PASSWORD, camera_configs)
    
    try:
        # Start all stream scripts remotely
        if launcher.start_streams():
            # Add a delay to ensure streams are fully started
            print("Waiting for streams to initialize...")
            time.sleep(3)
            
            # Check stream status to verify they're running
            launcher.check_stream_status()
            
            print("Processing streams for 6 seconds...")
            launcher.process_all_streams()
        else:
            print("Failed to start stream scripts")
    
    except KeyboardInterrupt:
        print("Program terminated by user")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()