# Issue ve PR çalışma akışı

Ana takip [#1](https://github.com/mathissdupont/NLP-Project/issues/1); bütün görevler, sorumlular ve ilk bağımlılık haritası [ISSUE_INDEX.md](ISSUE_INDEX.md) içindedir. Bilimsel plan [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md), iş paylaşımı [TEAM_PLAN.md](TEAM_PLAN.md) ile birlikte kullanılır.

## İş ve blocker tanımı

Her teslimin bir issue'su, tek bir ana sorumlusu, bir çapraz inceleyeni, milestone'u ve kontrol edilebilir kabul ölçütleri vardır. Bir issue'nun sağındaki **Relationships → Blocked by / Blocking** alanları gerçek bağımlılık kaydıdır. Açıklamadaki referans tek başına native ilişki oluşturmaz; yeni blocker eklerken bu alanı da güncelleyin.

Blocker **işin kapanmasını** engeller. Örneğin Samet #12 probe kodunu sentetik vektörlerle hemen geliştirebilir; #13 gerçek pilotunu ise #6 veri, #9 temsil ve #10–12 uygulama teslimleri olmadan kapatamaz. İlerlemek için gerçek veri gerektirmeyen hazırlıkları issue açıklamasında ayrı yazın.

Bir ön koşulu yalnızca engeli kaldırmak için kapatmayın. Kapsam dışı bırakılacaksa gerekçesini ve etkilediği protokolü kaydedip dependency ilişkisini bilinçli olarak güncelleyin. Tamamlanan bir issue yeniden açıldığında bağımlı işler tekrar blocked olur.

## Etiketler ve güncel görünümler

- `owner:halil`, `owner:fatmanur`, `owner:samet`: ana sorumlunun kaydı. Tek bir owner etiketi kullanın; assignee alanı bununla senkronize edilir.
- `area:*`: veri, modeller, değerlendirme, makale veya workflow.
- `priority:high` / `priority:normal`: başlangıç önceliği.
- `workflow:ready`: açık hard blocker yok; bu etiket henüz işe başlandığını söylemez.
- `workflow:blocked`: kapanmadan önce bitmesi gereken açık native dependency var.
- `state:in-progress`: sorumlu işe başladı; elle eklenir.
- `state:review`: teslim/PR çapraz incelemeye hazır; elle eklenir.
- `type:tracking`: ana takip kaydı; ready/blocked senkronizasyonundan muaftır.

Issue sync, issue açılma/düzenlenme/kapanma/yeniden açılma olaylarında ve altı saatte bir çalışır; **Actions → Issue sync → Run workflow** ile de tetiklenebilir. GitHub zamanlanmış işleri geciktirebilir. Native dependency değişikliğinin kendisi bu workflow'u doğrudan tetiklemediğinden anında etiket yenilemek için elle çalıştırın. Kapanan işlerin ready/blocked etiketlerini kaldırır. Yeni bir sahibi atamak için owner etiketini ve eski assignee'yi bilinçli güncelleyin; otomasyon başka assignee'leri silmez.

GitHub filtreleri:

```text
is:issue is:open label:owner:samet
is:issue is:open label:owner:halil
is:issue is:open label:owner:fatmanur
is:issue is:open label:workflow:ready
is:issue is:open label:workflow:blocked
```

## Issue → branch → PR → inceleme → merge

1. Issue'yu seç; sorumlu, giriş/çıkış sözleşmesi ve blocker'ları kontrol et. Başladıysan `state:in-progress` ekle.
2. Güncel `main` üzerinden issue numaralı bir dal aç: örneğin `eval/11-character-baseline`.
3. İşi küçük, incelenebilir değişiklikler halinde tamamla. Hazırlık halindeyken **Draft PR** açabilirsin.
4. PR açıklamasında gerçekten tamamladığın yerel issue için `Closes #11` yaz. İlişkili fakat tamamlanmayan işler için `Refs #13` kullan.
5. PR şablonuna davranış değişikliğini, doğrulama komut/çıktılarını ve ilgili dataset/config/model/run kimliklerini ekle. CODEOWNERS dosya bazında inceleme isteyebilir; TEAM_PLAN'deki çapraz inceleyeni **Reviewers** alanından kontrol ederek seç. Kendi PR'ına onay veremezsin.
6. **Research CI** foundation testlerini Python 3.11/3.14 üzerinde çalıştırır. `issue-dependencies` kontrolü, hazır PR'ın kapatacağı issue'ların açık blocker'larını sorgular. İlgili yerel issue yoksa veya dışarıda açık blocker varsa başarısız olur. Aynı PR hem blocker'ı hem bağımlı işi gerçekten tamamlıyorsa ikisini de `Closes` ile bağlayabilir.
7. Draft'tan hazır duruma geçince kontroller yeniden çalışır. Bir blocker sonradan kapandığında başarısız PR kontrolü kendiliğinden yenilenmeyebilir; PR'da **Re-run jobs** ile kontrolü tekrar çalıştır. Etiket senkronizasyonu tek başına PR check sonucunu değiştirmez.
8. Bir ekip arkadaşının onayı, başarılı gerekli kontroller ve çözülmüş review konuşmaları sonrasında **squash merge** yap. Issue otomatik kapanır; tamamlanan katkıyı kanıtıyla CONTRIBUTIONS.md dosyasına ekle.

## Main koruması

Kurulum PR'ı doğrulandıktan sonra hedeflenen kural: bir approving review, güncel branch üzerinde iki foundation check ve `issue-dependencies`, yeni commit'te eski onayın düşmesi, konuşmaların çözülmesi, force-push ve branch silmenin kapalı olması. CODEOWNERS bir yönlendirme aracıdır; onayın yalnızca tek bir dosya sahibinden gelmesi zorunlu değildir. Repo sahibinin yönetici bypass yetkisi korunur; günlük ekip çalışması PR akışını izler.

İlk workflow kurulum PR'ı, bu korumalar devreye alınmadan önce CI ile doğrulanan bootstrap değişikliğidir; bağımsız insan onayı alınmış gibi kaydedilmez. Sonraki PR'lar normal akışı kullanır.

CI; gerçek veri incelemesi, GPU deneyleri, ana test izolasyonu, makale derleme veya bilimsel yorumun yerini tutmaz. Issue kabul ölçütleri ve insan incelemesi bu kontrolleri ayrıca kapsar.

## Kilometre taşları

| Milestone | Bitiş ölçütü |
| --- | --- |
| M0 — Collaboration workflow | Issue/PR/dependency akışı ve CI doğrulanmış. |
| M1 — BERTurk pilot | İncelenmiş pilot verisi, baseline/probe uygulamaları ve ölçülmüş uçtan uca BERTurk pilotu. |
| M2 — Main experiments | Dondurulmuş ana veri/holdoutlar, üç model ve kontrol deneyleri, izlenebilir analiz. |
| M3 — Research paper | İncelenmiş yöntem/sonuç bölümleri, derlenmiş makale ve yeniden üretilebilir teslim. |

Teslim tarihi bilinmediği için milestone'lara uydurma son tarih atanmamıştır.
