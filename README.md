# Clipboard Translator - Anlık Çeviri Uygulaması

![Translator Icon](https://img.shields.io/badge/Clipboard-Translator-blue)
![Python Version](https://img.shields.io/badge/Python-3.7+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

Bu uygulama, kopyaladığınız metinleri hızlıca farklı dillere çevirmenizi sağlayan, sistem tepsisinde çalışan kullanışlı bir araçtır. Özellikle yabancı dildeki içerikleri okurken veya çalışırken, metin seçip kopyalayarak anında çeviri alabilirsiniz.

## Özellikler

- 💡 **Anlık Çeviri**: Metni kopyaladığınız anda çeviri yapabilirsiniz
- 🌐 **Çoklu Dil Desteği**: 9+ dil arasında çeviri yapabilme
- 🔄 **Çift Ctrl+CC Kısayolu**: Hızlı çeviri için çift Ctrl+CC (veya Ctrl+Alt+T)
- 🖋️ **Otomatik Dil Algılama**: Kaynak dili otomatik algılama
- 🔍 **Özel Karakter Düzeltme**: Türkçe karakterler için düzeltmeler
- 💼 **Sistem Tepsisi Entegrasyonu**: Bilgisayar kaynaklarını az kullanır
- 📋 **Kolay Kopyalama**: Çeviriyi tek tıkla kopyalayabilme

## Clipboard Translator - Kolay Kurulum Seçenekleri

Kurulum Seçenekleri
1. Exe Dosyası ile Kurulum (Python Gerektirmez)
Uygulamayı Python kurulumu yapmadan direk kullanmak için:

Releases sayfasından en son sürümü indirin
İndirdiğiniz Translator.exe dosyasını çift tıklayarak doğrudan çalıştırabilirsiniz
İsterseniz dosyayı başlangıç klasörünüze ekleyerek bilgisayarınız her açıldığında otomatik başlatabilirsiniz
Exe dosyası, tüm bağımlılıkları içinde barındırır ve Python kurulumu gerektirmez.

2. Kaynak Kod ile Kurulum
Geliştiriciler ve kodu özelleştirmek isteyenler için kaynak kodu kullanabilirsiniz:

Yukarıda belirtilen kurulum adımlarını takip edin
translate.py dosyasını herhangi bir kod editörüyle açarak kendi ihtiyaçlarınıza göre düzenleyebilirsiniz:
Desteklenen dilleri artırabilir/azaltabilir
Arayüz tasarımını değiştirebilir
Kısayol tuşlarını özelleştirebilir
Çeviri API'sini değiştirebilirsiniz
Kaynak kodu düzenleyerek, uygulamayı tamamen kendi ihtiyaçlarınıza göre uyarlayabilirsiniz.

Özelleştirme İpuçları
Kaynak kodunu düzenlerken faydalı olabilecek bazı noktalar:

Dil desteği eklemek için: supported_languages sözlüğünü düzenleyin
Farklı kısayol tuş kombinasyonları için: keyboard.add_hotkey() fonksiyonunu değiştirin
Farklı bir çeviri API'si kullanmak için: translate_text() fonksiyonunu güncelleyin

## Kurulum

### Gereksinimler

- Python 3.7 veya üzeri
- Aşağıdaki Python paketleri:
  - pystray
  - googletrans (3.1.0a0 sürümü)
  - pillow (PIL)
  - pyperclip
  - keyboard

### Kurulum Adımları

1. Bu depoyu klonlayın veya ZIP olarak indirin:
   ```
   git clone https://github.com/AIPILOT-AIPI/Translate.git
   cd translate
   ```

2. Gerekli Python paketlerini yükleyin:
   ```
   pip install pystray pillow pyperclip keyboard
   pip install googletrans==3.1.0a0
   ```

3. Uygulamayı çalıştırın:
   ```
   python translate.py
   ```

## Kullanım

Uygulama başlatıldığında sistem tepsisinde bir simge görünecektir.

### Çeviri Yapma

İki farklı yöntemle çeviri yapabilirsiniz:

1. **Hızlı Çeviri**: Herhangi bir metni seçin, `Ctrl+C` ile kopyalayın, ardından tekrar hızlıca `Ctrl+C` tuşlarına basın (0.5 saniye içinde çift basış).

2. **Manuel Çeviri**: Herhangi bir metni kopyalayın, ardından `Ctrl+Alt+T` kısayol tuşlarına basın.

### Ayarlar

Sistem tepsisindeki simgeye sağ tıklayarak:
- **Şu anki metni çevir**: Panodaki metni çevirir
- **Ayarlar**: Kaynak ve hedef dil ayarlarını değiştirebilirsiniz
- **Çıkış**: Uygulamayı kapatır

Çeviri penceresinde de dil seçimlerini anında değiştirebilirsiniz.

## Desteklenen Diller

- 🇹🇷 Türkçe (tr)
- 🇬🇧 İngilizce (en)
- 🇩🇪 Almanca (de)
- 🇫🇷 Fransızca (fr)
- 🇪🇸 İspanyolca (es)
- 🇮🇹 İtalyanca (it)
- 🇷🇺 Rusça (ru)
- 🇮🇷 Farsça (fa)
- 🇨🇳 Çince (zh-cn)
- 🔍 Otomatik Algılama (auto) - sadece kaynak dil olarak

## Sorun Giderme

### Sık Karşılaşılan Sorunlar

1. **Sistem tepsisi simgesi görünmüyor**: Uygulama, simge oluşturulamazsa minimal bir pencere açacaktır.

2. **Çeviri çalışmıyor**: 
   - İnternet bağlantınızı kontrol edin
   - Googletrans API sürümünü kontrol edin (3.1.0a0 önerilir)
   ```
   pip install googletrans==3.1.0a0
   ```

3. **Klavye kısayolları çalışmıyor**:
   - Bilgisayarınızı yönetici olarak çalıştırmayı deneyin
   - Başka bir programın bu kısayolları kullanıp kullanmadığını kontrol edin

### Debug Modu

Sorunları tespit etmek için uygulama klasöründe otomatik olarak `translate_debug.log` dosyası oluşturulur. Hata raporları için bu dosyayı inceleyebilirsiniz.

## Katkıda Bulunma

1. Bu depoyu forklayın
2. Feature branch'i oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inize push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.

## İletişim

GitHub: https://github.com/AIPILOT-AIPI/Translate

---

⭐️ Eğer bu proje işinize yaradıysa, Star vermeyi unutmayın! ⭐️ 