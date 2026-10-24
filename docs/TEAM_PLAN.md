# Görev paylaşımı ve ilk çalışma planı

Bu dağılım başlangıç önerisidir; kişilerin mevcut uzmanlığına ilişkin bir varsayım içermez. İş yükü veya ilgi alanları değişirse sorumluluklar birlikte güncellenir. README, bilimsel protokol ve makale İngilizce; ekip içi bu çalışma planı Türkçedir.

## Ana sorumluluklar

| Üye | Ana iş paketi | Somut teslimler | Çapraz inceleyen |
| --- | --- | --- | --- |
| **Halil Abacı** | Veri ve Türkçe morfoloji | Kaynak envanteri, gerçek/yapay kök listeleri, nonce tarama kayıtları, ekleme kuralları, etiketleme yönergesi, doğrulanmış veri ve split manifestleri | Fatmanur |
| **Fatmanur Bulut** | Modeller, tokenizasyon ve temsiller | Sabitlenmiş checkpoint/tokenizer sürümleri, token-parça hizalama, katman temsili çıkarımı, pooling karşılaştırması, parçalanma istatistikleri ve önbellek metaverisi | Samet |
| **Samet Ünsal** | Probing, değerlendirme ve entegrasyon | Linear probe, majority/character baselineları, geliştirme kümesinde ayar seçimi, metrikler, bootstrap, karşılaştırma grafikleri ve uçtan uca çalıştırma akışı | Halil |

Sorumlu kişi işin ilerlemesini ve teslimini takip eder; her satır yalnızca o kişinin çalışacağı anlamına gelmez. Morfolojik doğrulamayı en az iki kişi yapar; anlaşmazlıklar ortak oturumda çözülür. Samet entegrasyon takibini yürütür, makalenin tamamını tek başına yazmaz.

## Makale ve literatür paylaşımı

| Üye | İlk yazım sorumluluğu | Okuma odağı |
| --- | --- | --- |
| Halil | Dataset, Annotation, Morphological Validation | Türkçe morfoloji, nonce üretimi, veri kaynakları |
| Fatmanur | Models, Representation Extraction, Tokenization Analysis | BERTurk/mBERT/XLM-R, katman temsilleri ve tokenizasyon |
| Samet | Probing Protocol, Evaluation, Results | Probing kontrolleri, genelleme splitleri, istatistiksel değerlendirme |
| Üç kişi birlikte | Introduction, Related Work, Discussion, Limitations, Conclusion | Katkı iddiası, bulguların yorumu ve son metnin kontrolü |

Herkes kendi bölümünü yazarken en az üç ilgili çalışmayı literatür matrisine ekler. Aynı temel makaleleri ortak okumak serbesttir; üç kez aynı özeti üretmek yerine farklı yöntem/varsayımları karşılaştırın. Yazarlık sırası gerçek katkılar görüldükten sonra birlikte kararlaştırılır.

## İlk 7 çalışma günü için önerilen sprint

Bu bir takvim taahhüdü değildir; teslim tarihi bilinmediği için göreli çalışma günleri kullanılır.

| Zaman | Halil | Fatmanur | Samet | Ortak çıktı |
| --- | --- | --- | --- | --- |
| Gün 1–2 | Kaynak adayları ve ilk etiketleme kararları | Checkpoint/tokenizer incelemesi ve donanım envanteri | Çalışma ortamı, baseline/probe arayüz taslağı | Kapsam, veri sözleşmesi ve protokolün ekipçe incelenmesi |
| Gün 3–4 | En az 10 gerçek/yapay kök çifti için aday liste ve bağımsız inceleme | Aynı örneklerde gerçek tokenizasyon ve hedef kelime hizalama kontrolü | Veri sızıntısı kontrolleri ve ilk character/majority baseline uygulaması | Küçük entegrasyon verisi; ana deney verisi olarak kullanılmaz |
| Gün 5–6 | Etiket ve biçim hatalarını çözme, kapsam tablosu | BERTurk için küçük örneklerde katman çıkarımı ve maliyet ölçümü | Temsiller üzerinde ilk linear probe ve metrik doğrulaması | BERTurk pilotunun uçtan uca denenmesi |
| Gün 7 | Veri doğrulama özeti | Süre/bellek ve tokenizasyon özeti | Baseline/probe sonuçları ve sorun listesi | Pilot değerlendirmesi; veri büyüklüğü ve ana deney planı kararı |

İlk 10 çift yalnızca entegrasyon hedefidir; bilimsel karşılaştırma için yeterli örneklem olduğu iddia edilmez. Ana test kümesi pilot kararlarından sonra oluşturulur ve dondurulur.

## Teslim ve bağımlılıklar

1. **Veri → temsiller:** Halil veri sürümünü, SHA-256 özetini, kaynak kayıtlarını, etiket yönergesini ve örnek ID listesini verir. Fatmanur örnek sırasını korur ve tokenizasyon sorunlarını geri bildirir.
2. **Temsiller → probing:** Fatmanur örnek ID'leriyle hizalı vektörleri; model/tokenizer revision, katman, pooling ve parçalanma metaverisiyle teslim eder. Samet ID/sıra kontrolü yapmadan probe eğitmez.
3. **Probing → analiz:** Samet tahminleri ve metrikleri model/katman/özellik/seed/koşul kimlikleriyle kaydeder. Halil etiket ve morfolojik hata örneklerini, Fatmanur tokenizasyon kaynaklı örnekleri inceler.
4. **Analiz → makale:** Herkes kendi yöntem ve sonuç bölümünü gerçek çıktı dosyalarına referansla günceller. Başarılamayan kontroller ve olumsuz bulgular da kayda girer.

## Haftalık çalışma düzeni

- Haftada bir kısa ortak toplantı: tamamlanan teslim, engel, sıradaki somut iş.
- Toplantı notu için `docs/meetings/TEMPLATE.md` kopyalanır; henüz yapılmamış toplantı için karar yazılmaz.
- Kritik protokol değişikliği `docs/DECISIONS.md` dosyasına işlenir.
- Tamamlanan katkılar `docs/CONTRIBUTIONS.md` dosyasına kanıt dosyalarıyla eklenir.
- Bir işi kapatırken sorumlu kişi ve çapraz inceleyen, kabul ölçütlerini birlikte kontrol eder.

## İlk kilometre taşının kabul ölçütü

Üç üye projeyi kendi ortamında kurabiliyor; örnek veri doğrulanıyor; hatalı kök/çift/surface sızıntısı reddediliyor; BERTurk pilotunun gerçek maliyeti ölçülüyor; en az bir baseline ile bir probe aynı veri sürümünde çalışıyor. Son iki madde henüz uygulanacak iş paketleridir.
