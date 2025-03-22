import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageTk
import pyperclip
import keyboard
import threading
import json
import pystray
import time
from googletrans import Translator  # Translator sınıfını import et

# Pystray için backend seçimi
import pystray._win32 as pystray_backend
pystray.Icon._default_icon = pystray_backend.Icon

# Pystray importlarından önce
import os
import sys
import tkinter as tk
from PIL import Image, ImageDraw

# Pystray için özel backend seçimi
try:
    import pystray
    from pystray import MenuItem
    
    # PIL/Pillow ikonu pystray'e uygun formata dönüştür
    def _prepare_icon(icon):
        with open("debug_icon.log", "a") as f:
            f.write(f"Pystray icon prepare çağrıldı\n")
            f.write(f"Icon: {icon}\n")
        
        if icon.mode != 'RGBA':
            icon = icon.convert('RGBA')
        
        # Windows için icon boyutlarını ayarla
        if icon.size != (64, 64):
            icon = icon.resize((64, 64))
        
        with open("debug_icon.log", "a") as f:
            f.write(f"Modified Icon: {icon.size} {icon.mode}\n")
        
        return icon
    
    # Pystray'in ikon hazırlama fonksiyonunu override et
    import pystray._base
    pystray._base.Icon._prepare_icon = _prepare_icon
    
except Exception as e:
    print(f"Pystray yüklenirken hata: {e}")

class TranslateApp:
    def __init__(self):
        try:
            # Konfigürasyon dosyası yolunu tanımla
            self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
            
            # Debug log'u etkinleştir
            self.enable_debug_logging()
            
            # Yapılandırma dosyasını yükle
            self.load_config()
            
            # Çevirici nesnesini oluştur
            try:
                from googletrans import Translator
                self.translator = Translator()
            except ImportError as e:
                print(f"Googletrans modülü yüklenemedi: {e}")
                print("Alternatif çevirici kullanılıyor...")
                # Alternatif çevirici kullanabilirsiniz veya hata mesajı gösterebilirsiniz
                raise
            
            # Diğer başlangıç ayarları
            self.running = True
            self.previous_text = ""
            self.popup_window = None
            self.last_clipboard_check = time.time()
            self.ctrl_c_time = 0  # Son Ctrl+C basma zamanı
            
            # Klavye olaylarını dinlemeyi başlat
            self.setup_keyboard_listener()
            
            # Sistem tepsisi simgesi oluştur
            self.create_system_tray()
        except Exception as e:
            import traceback
            print(f"Uygulama başlatılırken hata oluştu: {e}")
            print(traceback.format_exc())
            sys.exit(1)

    def load_config(self):
        # Varsayılan değerler
        self.target_language = "en"
        self.source_language = "auto"
        self.popup_position = {"x": 100, "y": 100}
        self.popup_size = {"width": 400, "height": 300}
        
        # Varsa yapılandırma dosyasından yükle
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.target_language = config.get('target_language', "en")
                    self.source_language = config.get('source_language', "auto")
                    self.popup_position = config.get('popup_position', {"x": 100, "y": 100})
                    self.popup_size = config.get('popup_size', {"width": 400, "height": 300})
        except Exception as e:
            print(f"Yapılandırma dosyasını yüklerken hata: {e}")
    
    def save_config(self):
        try:
            config = {
                'target_language': self.target_language,
                'source_language': self.source_language,
                'popup_position': self.popup_position,
                'popup_size': self.popup_size
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Yapılandırma dosyasını kaydederken hata: {e}")
        
    def create_system_tray(self):
        try:
            # Önce normal şekilde pystray ile dene
            icon_image = self.create_icon_image()
            menu = (
                pystray.MenuItem('Şu anki metni çevir', self.manual_trigger),
                pystray.MenuItem('Ayarlar', self.show_settings),
                pystray.MenuItem('Çıkış', self.quit_app)
            )
            
            self.icon = pystray.Icon("TranslateApp", icon_image, "Çeviri Uygulaması", menu)
            threading.Thread(target=self.icon.run, daemon=True).start()
            print("Sistem tepsisi ikonu başarıyla oluşturuldu")
        except Exception as e:
            print(f"Sistem tepsisi ikonu oluşturma hatası: {e}")
            print("Alternatif tkinter penceresine geçiliyor...")
            self.create_alt_system_tray()

    def create_alt_system_tray(self):
        """Pystray başarısız olursa alternatif olarak tkinter penceresi kullan"""
        try:
            # Minimal tkinter penceresi oluştur
            root = tk.Tk()
            root.title("Çeviri Uygulaması")
            root.geometry("1x1+0+0")  # Çok küçük bir pencere
            root.withdraw()  # Görünmez yap
            
            # Küçültme durumunda görünecek ikon
            self.set_window_icon(root)
            
            # Menü oluştur
            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label="Şu anki metni çevir", command=self.manual_trigger)
            menu.add_command(label="Ayarlar", command=self.show_settings)
            menu.add_separator()
            menu.add_command(label="Çıkış", command=self.quit_app)
            
            # Sağ tık menüsünü ayarla
            def show_menu(event):
                menu.post(event.x_root, event.y_root)
            
            root.bind("<Button-3>", show_menu)
            
            # Pencereyi göster butonu
            show_btn = tk.Button(root, text="Çeviri Uygulaması", command=self.show_settings)
            show_btn.pack(padx=10, pady=10)
            
            # Görüntülenecek simüle edilmiş sistem tepsisi nesnesi
            class FakeIcon:
                def __init__(self, root):
                    self.root = root
                    
                def stop(self):
                    self.root.quit()
                    self.root.destroy()
                    
                def run_detached(self):
                    pass
            
            self.icon = FakeIcon(root)
            
            # Pencereyi görünür yap
            root.deiconify()
            # Pencereyi hemen simge durumuna küçült
            root.iconify()
            
            # Ana döngüyü başlat
            root.mainloop()
        except Exception as e:
            print(f"Alternatif sistem tepsisi oluşturma hatası: {e}")
        
    def create_icon_image(self):
        """Sistem tepsisi için ikon oluştur"""
        try:
            # Her zaman programatik olarak ikon oluştur (dosya hatalarından kaçınmak için)
            print("Programatik ikon oluşturuluyor...")
            image = Image.new('RGBA', (64, 64), color=(0, 120, 220, 255))
            draw = ImageDraw.Draw(image)
            draw.rectangle((20, 20, 44, 44), fill=(255, 255, 255, 255))
            
            # Programatik olarak oluşturulan ikonun bilgilerini yazdır
            print(f"Oluşturulan ikon: Boyut={image.size}, Mod={image.mode}")
            
            return image
        except Exception as e:
            print(f"İkon oluşturma hatası: {e}")
            # Son çare olarak minimum bir ikon 
            return Image.new('RGBA', (16, 16), color=(0, 120, 220, 255))
        
    def show_settings(self):
        # Ayarlar penceresini göster
        def save_settings():
            self.source_language = source_var.get()
            self.target_language = target_var.get()
            self.save_config()
            messagebox.showinfo("Bilgi", "Ayarlar kaydedildi!")
            settings_window.destroy()
        
        # Yeni bir toplevel penceresi oluştur (bağımsız olmayan bir pencere)
        settings_window = tk.Toplevel()
        settings_window.title("Çeviri Ayarları")
        settings_window.geometry("300x200")
        settings_window.resizable(False, False)
        settings_window.transient(self.popup_window)  # Ana pencereye bağımlı yap
        settings_window.grab_set()  # Odağı bu pencereye ver
        
        # Pencere ikonu ayarla
        self.set_window_icon(settings_window)
        
        # Kaynak dil seçimi
        ttk.Label(settings_window, text="Kaynak Dil:").pack(pady=5)
        source_var = tk.StringVar(value=self.source_language)
        source_combo = ttk.Combobox(settings_window, textvariable=source_var)
        source_combo['values'] = ('auto', 'tr', 'en', 'de', 'fr', 'es', 'it', 'ru', 'fa', 'zh-cn')
        source_combo.pack(pady=5)
        
        # Hedef dil seçimi
        ttk.Label(settings_window, text="Hedef Dil:").pack(pady=5)
        target_var = tk.StringVar(value=self.target_language)
        target_combo = ttk.Combobox(settings_window, textvariable=target_var)
        target_combo['values'] = ('tr', 'en', 'de', 'fr', 'es', 'it', 'ru', 'fa', 'zh-cn')
        target_combo.pack(pady=5)
        
        # Kaydet butonu
        ttk.Button(settings_window, text="Kaydet", command=save_settings).pack(pady=20)
        
        # Kapatma olayını işle
        def on_close():
            settings_window.destroy()
            
        settings_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Pencereyi merkeze yerleştir
        settings_window.update_idletasks()
        width = settings_window.winfo_width()
        height = settings_window.winfo_height()
        x = (settings_window.winfo_screenwidth() // 2) - (width // 2)
        y = (settings_window.winfo_screenheight() // 2) - (height // 2)
        settings_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Eğer ana pencere varsa bağımlı yap
        if self.popup_window and self.popup_window.winfo_exists():
            settings_window.transient(self.popup_window)
        
        # Pencere modalını ayarla (ana pencereye odaklanılmadan önce bu pencere kapatılmalı)
        settings_window.focus_set()
        
        # Tk.Tk yerine Toplevel kullanıldığında mainloop gereksizdir
        # settings_window.mainloop() olmamalı
    
    def quit_app(self):
        self.running = False
        self.icon.stop()
        sys.exit()
        
    def translate_text(self, text):
        try:
            # Metni çeviri için hazırla
            prepared_text = text
            
            # Eğer Türkçe'den İngilizce'ye çeviriyorsak, Türkçe kelimeleri normalize edelim
            if self.source_language == 'tr' and self.target_language == 'en':
                # Türkçe'den İngilizce'ye çevirirken, önce özel karakterleri normalleştirelim
                tr_to_en_mapping = {
                    'ğ': 'g', 'Ğ': 'G',
                    'ü': 'u', 'Ü': 'U',
                    'ş': 's', 'Ş': 'S',
                    'ı': 'i', 'İ': 'I',
                    'ö': 'o', 'Ö': 'O',
                    'ç': 'c', 'Ç': 'C'
                }
                
                # Özel Türkçe karakterleri İngilizce karşılıklarıyla değiştir
                for tr_char, en_char in tr_to_en_mapping.items():
                    prepared_text = prepared_text.replace(tr_char, en_char)
            
            # Çevirinin daha iyi sonuç vermesi için metin boyutunu kontrol et
            if len(prepared_text) > 5000:
                # Çok uzun metinleri parçalara böl (her 5000 karakter için)
                chunks = [prepared_text[i:i+5000] for i in range(0, len(prepared_text), 5000)]
                translated_chunks = []
                
                for chunk in chunks:
                    # Her parçayı ayrı ayrı çevir
                    result = self.translator.translate(chunk, src=self.source_language, dest=self.target_language)
                    translated_chunks.append(result.text)
                
                # Çevirilen parçaları birleştir
                translated_text = ' '.join(translated_chunks)
            else:
                # Standart çeviri işlemi
                result = self.translator.translate(prepared_text, src=self.source_language, dest=self.target_language)
                translated_text = result.text
            
            # Eğer hedef dil Türkçe ise ve özel karakterler eksikse düzeltme yap
            if self.target_language == 'tr':
                # Türkçe karakterler için düzeltmeler
                corrections = {
                    'Turkiye': 'Türkiye',
                    'turkiye': 'türkiye',
                    'Izmir': 'İzmir',
                    'Istanbul': 'İstanbul',
                    'Ankara': 'Ankara',  # Zaten doğru ama listeye ekledik
                    'Antalya': 'Antalya',  # Zaten doğru ama listeye ekledik
                    'Adana': 'Adana',  # Zaten doğru ama listeye ekledik
                    'guzel': 'güzel',
                    'Guzel': 'Güzel',
                    'gunes': 'güneş',
                    'Gunes': 'Güneş',
                    'ogrenci': 'öğrenci',
                    'Ogrenci': 'Öğrenci',
                    'ogretmen': 'öğretmen',
                    'Ogretmen': 'Öğretmen',
                    'universite': 'üniversite',
                    'Universite': 'Üniversite',
                    'kultur': 'kültür',
                    'Kultur': 'Kültür',
                    'gun': 'gün',
                    'Gun': 'Gün',
                    'kucuk': 'küçük',
                    'Kucuk': 'Küçük',
                    'buyuk': 'büyük',
                    'Buyuk': 'Büyük',
                    'gosteri': 'gösteri',
                    'Gosteri': 'Gösteri',
                    'donusum': 'dönüşüm',
                    'Donusum': 'Dönüşüm'
                }
                
                # Metindeki düzeltilmesi gereken kelimeleri ara ve düzelt
                for incorrect, correct in corrections.items():
                    # Tam kelime eşleşmesi için sınır kontrolü yap (örn: "gun" -> "gün" ama "gundem" -> "gündem")
                    translated_text = translated_text.replace(f" {incorrect} ", f" {correct} ")
                    translated_text = translated_text.replace(f"{incorrect} ", f"{correct} ")
                    translated_text = translated_text.replace(f" {incorrect}", f" {correct}")
                    
                    # Metin başında veya sonunda olabilecek durumlar için
                    if translated_text == incorrect:
                        translated_text = correct
                    
                    # Noktalama işaretleriyle birlikte
                    for punct in ['.', ',', '!', '?', ':', ';', ')', ']', '}', '"', "'"]:
                        translated_text = translated_text.replace(f"{incorrect}{punct}", f"{correct}{punct}")
            
            # İngilizce çevirilerde Türkçe özel isimlerini düzeltme
            if self.target_language == 'en':
                # İngilizce olması gereken fakat Türkçe olarak kalan özel isimler için düzeltmeler
                corrections = {
                    'Türkiye': 'Turkiye',
                    'İstanbul': 'Istanbul',
                    'İzmir': 'Izmir',
                    'Çanakkale': 'Canakkale',
                    'Ankara': 'Ankara'  # Değişiklik gerekmez ama listede tutalım
                }
                
                for tr_name, en_name in corrections.items():
                    # Özel isimleri düzelt
                    translated_text = translated_text.replace(tr_name, en_name)
            
            return translated_text
        except Exception as e:
            print(f"Çeviri hatası: {e}")
            return "Çeviri hatası!"
    
    def show_translate_popup(self, original_text, translated_text):
        # Eğer zaten bir popup açıksa onu kapat
        if self.popup_window is not None:
            try:
                self.popup_window.destroy()
            except:
                pass
        
        # Yeni bir popup penceresi oluştur
        self.popup_window = tk.Tk()
        self.popup_window.title("Çeviri")  # Başlık ekleyerek çerçeveyi gösterelim
        self.popup_window.attributes('-topmost', True)  # Her zaman üstte göster
        
        # Pencere ikonu ayarla
        self.set_window_icon(self.popup_window)
        
        # Pencerenin konumunu ve boyutunu ayarla
        self.popup_window.geometry(f"{self.popup_size['width']}x{self.popup_size['height']}+{self.popup_position['x']}+{self.popup_position['y']}")
        
        # Pencere kapatıldığında konum ve boyut bilgilerini kaydet
        def on_close():
            # Pencerenin son konumunu ve boyutunu al
            geo = self.popup_window.geometry()
            # geometry formatı: "widthxheight+x+y"
            parts = geo.replace("+", "x").split("x")
            if len(parts) >= 4:
                self.popup_size['width'] = int(parts[0])
                self.popup_size['height'] = int(parts[1])
                self.popup_position['x'] = int(parts[2])
                self.popup_position['y'] = int(parts[3])
                self.save_config()
            self.popup_window.destroy()
            
        self.popup_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Ana çerçeve
        main_frame = ttk.Frame(self.popup_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Dil seçim çerçevesi
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(fill="x", pady=(0, 10))
        
        # Kaynak dil seçimi
        ttk.Label(lang_frame, text="Kaynak:").pack(side="left", padx=(0, 5))
        source_var = tk.StringVar(value=self.source_language)
        source_combo = ttk.Combobox(lang_frame, textvariable=source_var, width=6)
        source_combo['values'] = ('auto', 'tr', 'en', 'de', 'fr', 'es', 'it', 'ru', 'fa', 'zh-cn')
        source_combo.pack(side="left", padx=(0, 10))
        
        # Hedef dil seçimi
        ttk.Label(lang_frame, text="Hedef:").pack(side="left", padx=(0, 5))
        target_var = tk.StringVar(value=self.target_language)
        target_combo = ttk.Combobox(lang_frame, textvariable=target_var, width=6)
        target_combo['values'] = ('tr', 'en', 'de', 'fr', 'es', 'it', 'ru', 'fa', 'zh-cn')
        target_combo.pack(side="left")
        
        # Dil değişikliğinde tetiklenecek fonksiyon
        def on_language_change(*args):
            self.source_language = source_var.get()
            self.target_language = target_var.get()
            # Dil değişikliğini kaydet
            self.save_config()
            # Yeni dil ile tekrar çevir
            new_translated_text = self.translate_text(original_text)
            translated_text_box.config(state="normal")
            translated_text_box.delete(1.0, tk.END)
            translated_text_box.insert(tk.END, new_translated_text)
            translated_text_box.config(state="disabled")
            
        source_var.trace_add("write", on_language_change)
        target_var.trace_add("write", on_language_change)
        
        # Orijinal metin
        ttk.Label(main_frame, text="Orijinal Metin:", font=('Arial', 10, 'bold')).pack(anchor="w")
        original_text_box = tk.Text(main_frame, wrap="word", height=3, font=('Arial', 9))
        original_text_box.insert(tk.END, original_text)
        original_text_box.config(state="disabled")
        original_text_box.pack(fill="both", expand=True, pady=(0, 10))
        
        # Çevirilen metin
        ttk.Label(main_frame, text="Çeviri:", font=('Arial', 10, 'bold')).pack(anchor="w")
        translated_text_box = tk.Text(main_frame, wrap="word", height=5, font=('Arial', 9))
        translated_text_box.insert(tk.END, translated_text)
        translated_text_box.config(state="disabled")
        translated_text_box.pack(fill="both", expand=True, pady=(0, 10))
        
        # Butonlar için çerçeve
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(0, 5))
        
        # Kopyala butonu
        def copy_translation():
            pyperclip.copy(translated_text_box.get(1.0, tk.END).strip())
            copy_button.config(text="Kopyalandı!")
            self.popup_window.after(1000, lambda: copy_button.config(text="Çeviriyi Kopyala"))
            
        copy_button = ttk.Button(button_frame, text="Çeviriyi Kopyala", command=copy_translation)
        copy_button.pack(side="left", padx=(0, 10))
        
        # Kapat butonu
        ttk.Button(button_frame, text="Kapat", command=on_close).pack(side="right")
        
        # Pencereyi göster
        self.popup_window.mainloop()
    
    def check_clipboard(self):
        """Panoyu kontrol eder ve içeriği çevirir"""
        try:
            current_text = pyperclip.paste()
            
            # Boş değilse ve son metinden farklıysa
            if current_text and current_text != self.previous_text and current_text.strip() != "":
                print(f"Yeni metin kopyalandı: {current_text[:30]}...")
                self.previous_text = current_text
                
                # Metni çevir
                translated_text = self.translate_text(current_text)
                
                # Çeviri penceresini göster
                threading.Thread(
                    target=self.show_translate_popup,
                    args=(current_text, translated_text)
                ).start()
            else:
                if not current_text or current_text.strip() == "":
                    print("Panoda hiç metin yok veya boş")
                else:
                    print("Aynı metin zaten çevrildi")
        except Exception as e:
            print(f"Pano kontrolünde hata: {e}")

    def prepare_text_for_translation(self, text):
        """Çeviri için metni hazırla: cümleleri daha iyi ayırt et, bağlamı koru"""
        # Gereksiz boşlukları temizle
        text = ' '.join(text.split())
        
        # Cümle sonlarına doğru noktalama işaretleri ekle
        # Bu, çevirinin cümleleri daha iyi anlamasına yardımcı olabilir
        if text and not text.endswith(('.', '!', '?', ':', ';')):
            text = text + '.'
            
        return text
    
    def handle_c_key(self):
        # Eğer ctrl+cc kombinasyonu algılanırsa (hızlı art arda iki c tuşuna basılma)
        current_time = time.time()
        if current_time - self.last_c_press_time < 0.5:  # 0.5 saniye içinde iki kez c tuşuna basılırsa
            self.check_clipboard()
        self.last_c_press_time = current_time
    
    def monitor_clipboard(self):
        # ctrl+c tuşuna basıldığında handle_c_key fonksiyonunu çağır
        keyboard.add_hotkey('ctrl+c', self.handle_c_key)
        
    def run(self):
        # Pano izleme işlemini başlat
        self.monitor_clipboard()
        
        # Sistem tepsisinde uygulamayı başlat
        self.icon.run()

    def set_window_icon(self, window):
        """Tkinter penceresine ikon ayarla"""
        try:
            # Exe dosyasının bulunduğu dizinde ikon ara
            exe_dir = os.path.dirname(os.path.abspath(sys.executable))
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Olası ikon dosya yolları
            icon_paths = [
                os.path.join(exe_dir, "translate_icon.png"),
                os.path.join(script_dir, "translate_icon.png"),
                os.path.join(exe_dir, "translate.ico"),
                os.path.join(script_dir, "translate.ico"),
                "translate_icon.png",
                "translate.ico"
            ]
            
            icon_found = False
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    try:
                        # Windows'ta ico dosyası doğrudan kullanılabilir
                        if icon_path.lower().endswith('.ico'):
                            window.iconbitmap(icon_path)
                            print(f"Pencere ikonu ayarlandı (ICO): {icon_path}")
                            icon_found = True
                            break
                        
                        # PNG dosyası için PhotoImage kullan
                        elif icon_path.lower().endswith('.png'):
                            from PIL import ImageTk
                            icon_image = Image.open(icon_path)
                            photo = ImageTk.PhotoImage(icon_image)
                            window.iconphoto(True, photo)
                            # Referansı tut, aksi halde garbage collector tarafından silinebilir
                            window._icon_photo = photo
                            print(f"Pencere ikonu ayarlandı (PNG): {icon_path}")
                            icon_found = True
                            break
                    except Exception as e:
                        print(f"İkon yükleme hatası ({icon_path}): {e}")
            
            if not icon_found:
                print("Hiçbir ikon dosyası bulunamadı veya yüklenemedi.")
        
        except Exception as e:
            print(f"Pencere ikonu ayarlanamadı: {e}")

    def setup_keyboard_listener(self):
        """Klavye olaylarını dinleme işlemini kur"""
        try:
            # Global hook olarak Ctrl+C olaylarını yakala
            # Alternatif kısayol olarak Ctrl+Alt+T ekle
            keyboard.add_hotkey('ctrl+c', self.handle_ctrl_c, suppress=False)
            keyboard.add_hotkey('ctrl+alt+t', self.check_clipboard_direct, suppress=False)
            
            print("Klavye dinleyicileri başlatıldı: Ctrl+C ve Ctrl+Alt+T")
        except Exception as e:
            print(f"Klavye dinleyicisi başlatılamadı: {e}")
            print("Alternatif klavye kısayollarını kullanabilirsiniz: Ctrl+Alt+T")

    def handle_ctrl_c(self):
        """Ctrl+C basıldığında çağrılır"""
        try:
            current_time = time.time()
            # Eğer son 0.5 saniye içinde Ctrl+C'ye basıldıysa
            if current_time - self.ctrl_c_time < 0.5:
                print("Çift Ctrl+C algılandı, çeviri yapılıyor...")
                # Biraz bekleyelim ki panoya metin kopyalansın
                threading.Timer(0.1, self.check_clipboard).start()
            
            # Son Ctrl+C zamanını güncelle
            self.ctrl_c_time = current_time
        except Exception as e:
            print(f"Ctrl+C işlenirken hata: {e}")

    def check_clipboard_direct(self):
        """Doğrudan panodaki metni kontrol eder (Ctrl+Alt+T için)"""
        try:
            print("Ctrl+Alt+T algılandı, pano kontrol ediliyor...")
            self.check_clipboard()
        except Exception as e:
            print(f"Doğrudan pano kontrolünde hata: {e}")

    def on_key_event(self, event):
        """Tüm klavye olaylarını dinler, Ctrl+C kombinasyonunu algılar"""
        try:
            # Eğer olay Ctrl+C ise
            if event.name == 'c' and keyboard.is_pressed('ctrl'):
                self.handle_ctrl_c()
        except Exception as e:
            print(f"Klavye olayı işlenirken hata: {e}")

    def enable_debug_logging(self):
        """Debug log dosyası oluştur"""
        try:
            log_file = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "translate_debug.log")
            
            # Log dosyasını aç
            with open(log_file, "w") as f:
                f.write(f"Translate Debug Log - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Python Version: {sys.version}\n")
                f.write(f"Executable: {sys.executable}\n")
                f.write(f"Working Directory: {os.getcwd()}\n")
                f.write(f"Platform: {sys.platform}\n\n")
            
            # Global hata yakalayıcı ekle
            def global_exception_handler(exctype, value, traceback_obj):
                with open(log_file, "a") as f:
                    f.write(f"\nUncaught Exception: {exctype.__name__}: {value}\n")
                    import traceback
                    traceback.print_exception(exctype, value, traceback_obj, file=f)
            
            sys.excepthook = global_exception_handler
            
            # Debug fonksiyonu
            def debug_log(message):
                with open(log_file, "a") as f:
                    f.write(f"{time.strftime('%H:%M:%S')} - {message}\n")
            
            # Sınıfa fonksiyonu ekle
            self.debug_log = debug_log
            self.debug_log("Debug logging başlatıldı")
            
        except Exception as e:
            print(f"Debug logging başlatılamadı: {e}")

    def manual_trigger(self):
        """Klavye olayı tetiklemek için manuel bir fonksiyon"""
        print("Manuel tetikleme - pano kontrol ediliyor...")
        self.check_clipboard()

if __name__ == "__main__":
    app = TranslateApp()
    
    # Ana thread'i canlı tut
    try:
        # Uygulamanın çalıştığı süre boyunca ana thread'i beklet
        while app.running:
            time.sleep(1)
    except KeyboardInterrupt:
        app.quit_app()