import os
import sys
import subprocess
import time
import shutil  # Dosya kopyalama işlemleri için
from PIL import Image, ImageDraw

def print_step(message):
    """Adımları renkli ve vurgulu gösterir"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print(f"  {message}")
    print("=" * 60)
    print()

def run_command(command, error_message="Komut çalıştırılırken hata oluştu!"):
    """Bir komutu çalıştırır ve sonucunu döndürür"""
    print(f"Çalıştırılıyor: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"HATA: {error_message}")
        print(f"Detay: {result.stderr}")
        return False
    return True

def create_icon():
    """Simge dosyası oluşturur"""
    print("İkon dosyaları oluşturuluyor...")
    try:
        # 64x64 pixel mavi arka plan ikon oluştur
        image = Image.new('RGBA', (64, 64), color=(0, 120, 220, 255))
        draw = ImageDraw.Draw(image)
        
        # Beyaz dikdörtgen çiz
        draw.rectangle([20, 20, 44, 44], fill=(255, 255, 255, 255))
        
        # ICO dosyasını kaydet
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translate.ico")
        image.save(icon_path, format='ICO')
        
        # Aynı resmi PNG formatında da kaydet (sistem tepsisi için)
        png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translate_icon.png")
        image.save(png_path, format='PNG')
        
        print(f"İkon dosyaları oluşturuldu: {icon_path} ve {png_path}")
        return icon_path
    except Exception as e:
        print(f"İkon oluşturma hatası: {e}")
        print("İkon oluşturulamadı, ikonsuz devam edilecek.")
        return None

def install_packages():
    """Gerekli Python paketlerini yükler"""
    print_step("Gerekli Python paketleri yükleniyor...")
    
    packages = [
        "pyinstaller",
        "pyperclip",
        "keyboard",
        "pystray",
        "pillow",
        "googletrans==4.0.0-rc1"
        # pyttsx3, gtts ve playsound kütüphaneleri kaldırıldı
    ]
    
    for package in packages:
        print(f"{package} yükleniyor...")
        if not run_command(f"{sys.executable} -m pip install {package}", f"{package} yüklenemedi!"):
            return False
        print(f"{package} başarıyla yüklendi.")
    
    return True

def create_executable():
    """PyInstaller ile exe dosyasını oluşturur"""
    print_step("Çalıştırılabilir dosya (exe) oluşturuluyor...")
    
    # Önce ikon oluştur ya da varsa kullan
    icon_path = None
    ico_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translate.ico")
    
    if os.path.exists(ico_file):
        print(f"Mevcut ikon dosyası kullanılıyor: {ico_file}")
        icon_path = ico_file
    else:
        icon_path = create_icon()
    
    # PyInstaller'ı doğrudan Python modülü olarak çalıştır
    if icon_path and os.path.exists(icon_path):
        # Windows yolları için ters eğik çizgileri düzelt
        icon_path = icon_path.replace('\\', '/')
        
        # Yol içinde boşluk olabileceği için tırnak işaretleri kullan
        # keyboard ve pystray için UAC bypassing etkinleştir
        pyinstaller_cmd = f'{sys.executable} -m PyInstaller --onefile --noconsole --uac-admin --icon="{icon_path}" translate.py'
    else:
        print("İkon bulunamadı, ikonsuz devam ediliyor...")
        pyinstaller_cmd = f'{sys.executable} -m PyInstaller --onefile --noconsole --uac-admin translate.py'
    
    print(f"Çalıştırılacak komut: {pyinstaller_cmd}")    
    if not run_command(pyinstaller_cmd, "PyInstaller çalıştırılamadı!"):
        return False
    
    # PNG dosyasını dist klasörüne kopyala
    png_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translate_icon.png")
    if os.path.exists(png_file):
        try:
            dist_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
            png_dest = os.path.join(dist_folder, "translate_icon.png")
            shutil.copy2(png_file, png_dest)
            print(f"PNG ikon dosyası dist klasörüne kopyalandı: {png_dest}")
        except Exception as e:
            print(f"PNG kopyalama hatası: {e}")
    
    return True

def add_to_startup():
    """Oluşturulan exe'yi Windows başlangıcına ekler"""
    print_step("Program Windows başlangıcına ekleniyor...")
    
    # Exe dosyasının tam yolu
    exe_path = os.path.abspath(os.path.join("dist", "translate.exe"))
    
    if not os.path.exists(exe_path):
        print(f"HATA: {exe_path} bulunamadı!")
        return False
    
    # Windows başlangıç klasörü
    startup_folder = os.path.join(os.environ["APPDATA"], 
                                 "Microsoft", "Windows", "Start Menu", 
                                 "Programs", "Startup")
    
    # Başlangıç klasörünü kontrol et
    if not os.path.exists(startup_folder):
        os.makedirs(startup_folder)
    
    # Kısayol oluşturmak için VBScript kullan
    shortcut_path = os.path.join(startup_folder, "TranslateApp.lnk")
    vbs_content = f"""
    Set WshShell = CreateObject("WScript.Shell")
    Set shortcut = WshShell.CreateShortcut("{shortcut_path}")
    shortcut.TargetPath = "{exe_path}"
    shortcut.WorkingDirectory = "{os.path.dirname(exe_path)}"
    shortcut.Save
    """
    
    # Geçici VBS dosyası oluştur
    vbs_path = "create_shortcut.vbs"
    with open(vbs_path, "w") as f:
        f.write(vbs_content)
    
    # VBS betiğini çalıştır
    if not run_command(f"cscript {vbs_path}", "Kısayol oluşturulamadı!"):
        return False
    
    # Geçici VBS dosyasını temizle
    os.remove(vbs_path)
    
    print(f"Kısayol oluşturuldu: {shortcut_path}")
    return True

def uninstall_previous():
    """Önceki kurulumu kaldırır"""
    print_step("Önceki kurulum kontrol ediliyor...")
    
    # Başlangıç klasöründeki kısayolu sil
    startup_folder = os.path.join(os.environ["APPDATA"], 
                                 "Microsoft", "Windows", "Start Menu", 
                                 "Programs", "Startup")
    shortcut_path = os.path.join(startup_folder, "TranslateApp.lnk")
    
    if os.path.exists(shortcut_path):
        try:
            print(f"Önceki kısayol bulundu, kaldırılıyor: {shortcut_path}")
            os.remove(shortcut_path)
            print("Kısayol başarıyla kaldırıldı.")
        except Exception as e:
            print(f"Kısayol kaldırma hatası: {e}")
    
    # Önceki build ve dist klasörlerini temizle
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            print(f"Önceki {folder} klasörü temizleniyor...")
            try:
                # Klasörü silme işlemi
                # Windows'ta rmdir veya rd komutu
                run_command(f"rmdir /S /Q {folder}", f"{folder} klasörü silinemedi!")
                print(f"{folder} klasörü başarıyla silindi.")
            except Exception as e:
                print(f"{folder} klasörü silme hatası: {e}")
    
    # spec dosyasını sil
    spec_file = "translate.spec"
    if os.path.exists(spec_file):
        try:
            os.remove(spec_file)
            print(f"{spec_file} dosyası silindi.")
        except Exception as e:
            print(f"{spec_file} silme hatası: {e}")
    
    return True

def main():
    """Ana kurulum fonksiyonu"""
    print_step("Translate App Kurulumu Başlıyor")
    print("Bu script gereken paketleri yükleyecek ve uygulamayı kuracak.")
    print("İşlem birkaç dakika sürebilir.\n")
    
    input("Devam etmek için Enter tuşuna basın...")
    
    # Önceki kurulumu kaldır
    uninstall_previous()
    
    if not install_packages():
        print("\nKurulum başarısız oldu: Paket yükleme hatası.")
        input("\nÇıkmak için Enter tuşuna basın...")
        return
    
    if not create_executable():
        print("\nKurulum başarısız oldu: Exe oluşturma hatası.")
        input("\nÇıkmak için Enter tuşuna basın...")
        return
    
    if not add_to_startup():
        print("\nUyarı: Program başlangıca eklenemedi.")
        print("Exe dosyası oluşturuldu ancak başlangıça eklenemedi.")
        print(f"Exe dosyası: {os.path.abspath(os.path.join('dist', 'translate.exe'))}")
        input("\nDevam etmek için Enter tuşuna basın...")
    
    print_step("Kurulum Tamamlandı!")
    print("Çeviri uygulaması başarıyla kuruldu.")
    print("Bilgisayarınızı her açtığınızda otomatik olarak başlayacaktır.")
    print("\nKullanım: ")
    print("1. Herhangi bir metni seçin")
    print("2. Ctrl+C tuşlarına hızlıca iki kez basın (0.5 saniye içinde)")
    print("3. Çeviri penceresi görünecektir")
    
    # Programı şimdi başlatmak ister misiniz?
    print("\nProgramı şimdi başlatmak istiyor musunuz? (E/H)")
    response = input().strip().lower()
    if response == 'e':
        try:
            exe_path = os.path.abspath(os.path.join("dist", "translate.exe"))
            print(f"Uygulama başlatılıyor: {exe_path}")
            
            # Daha güvenli başlatma yöntemi
            if os.path.exists(exe_path):
                # Komut istemcisi aracılığıyla başlat
                os.system(f'start "" "{exe_path}"')
                print("Program başlatıldı!")
            else:
                print(f"HATA: Exe dosyası bulunamadı: {exe_path}")
        except Exception as e:
            print(f"Uygulama başlatılırken hata oluştu: {e}")
            print("Uygulamayı manuel olarak başlatabilirsiniz.")
    
    print("\nKurulum tamamlandı! Pencereyi kapatabilirsiniz.")
    input("\nÇıkmak için Enter tuşuna basın...")

if __name__ == "__main__":
    main()

