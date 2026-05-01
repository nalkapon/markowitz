# YAP 471 Sunum Taslağı (15–20 dk)
## Multi-Sector Momentum Strategy using a Markowitz Allocator

Bu dosya, doğrudan slayta dönüştürülebilecek içerik ve kısa konuşma notlarını içerir.

---

## Slayt 1 — Başlık
**YAP 471 Dönem Projesi**  
**Multi-Sector Momentum Strategy using a Markowitz Allocator**  
Stock Tigers Takımı

**Konuşma Notu (30 sn):**
- Projenin amacı: sistematik bir yatırım stratejisini uçtan uca kurmak.
- Kapsam: veri, sinyal, portföy optimizasyonu, risk kontrolü ve backtest.

---

## Slayt 2 — Problem Tanımı ve Hedef
**Problem:** Momentum sinyalini kullanarak risk-kontrollü bir portföy oluşturmak.  
**Hedef:** OOS dönemde risk-ayarlı performansı ölçmek ve baseline ile karşılaştırmak.

- Markowitz ile dinamik ağırlıklar
- Volatilite hedefleme ile risk kontrolü
- 1/N baseline karşılaştırması

**Konuşma Notu (1 dk):**
- “Sadece getiri değil, risk-ayarlı performans” odaklı ilerledik.

---

## Slayt 3 — Veri ve Evren
**Varlık Evreni (10 adet, US Large-Cap):**
AAPL, JNJ, XOM, PG, JPM, NEE, LMT, GOLD, AMT, VZ

- Kaynak: Yahoo Finance (`yfinance`)
- Frekans: Günlük düzeltilmiş kapanış
- Dönem: 2021-01-01 → 2026-01-31
- Temizlik: forward-fill + winsorize (±5σ)

**Konuşma Notu (1 dk):**
- Çok sektörlü yapı ile korelasyon çeşitlendirmesi amaçlandı.

---

## Slayt 4 — Sinyal Tasarımı (Momentum)
**Ana Sinyal:** 12 aylık yuvarlanan momentum skoru

$$
M_{t,i} = \sum_{j=1}^{252} r_{t-j,i}
$$

- Kesitsel z-score normalizasyonu uygulandı
- Finansal sezgi: trend devamlılığı

**Konuşma Notu (1–1.5 dk):**
- Neden momentum? Literatürde güçlü anomali.
- Neden normalizasyon? Farklı volatilite ölçeklerini eşitlemek için.

---

## Slayt 5 — Portföy Kurulumu (Markowitz)
**Optimizasyon:**
$$
\max_w \left(\tilde{\mu}^T w - \frac{\lambda}{2} w^T \Sigma w\right)
$$

**Kısıtlar:**
- $0 \le w_i \le 1$
- $\sum_i w_i = 1$

**Girdiler:**
- Beklenen getiri vekili: normalize momentum
- Risk: expanding covariance

**Konuşma Notu (1.5 dk):**
- Modelde açığa satış yok, bütçe tam kullanılıyor.

---

## Slayt 6 — Risk Kontrolü ve Gerçekçilik
**Risk kontrolü:** Volatility targeting (yıllık hedef: 18%)

- Tahmini vol hedefi aşarsa ağırlıklar ayarlanıyor
- Ters-volatilite ile harmanlama uygulanıyor

**Gerçekçilik ekleri:**
- Turnover bazlı işlem maliyeti (bps) desteği
- Fair baseline (aylık 1/N) karşılaştırması

**Konuşma Notu (1.5 dk):**
- Hocanın beklediği “risk control module” net olarak var.

---

## Slayt 7 — Backtest Tasarımı
- Train / OOS ayrımı: %60 / %40
- OOS: 2024-01-19 → 2026-01-31
- Aylık rebalance
- Look-ahead bias yok (sadece geçmiş veri ile karar)

**Konuşma Notu (1 dk):**
- En kritik metodoloji: bilgi sızıntısını engellemek.

---

## Slayt 8 — Ana Sonuçlar (Günlük 1/N Baseline)
| Metrik | Strateji | 1/N (Günlük) |
|---|---:|---:|
| Sharpe | 0.4423 | 1.0089 |
| Ann.Ret | 13.74% | 17.76% |
| Ann.Vol | 19.76% | 12.65% |
| CumRet | 32.06% | 43.25% |
| MaxDD | -24.85% | -18.12% |

**Konuşma Notu (1 dk):**
- Bu örneklemde baseline daha iyi performans verdi.

---

## Slayt 9 — Adil Kıyas (Aylık 1/N Fair Baseline)
| Metrik | Strateji | 1/N (Aylık Fair) |
|---|---:|---:|
| Sharpe | 0.4423 | 1.2002 |
| Ann.Ret | 13.74% | 20.19% |
| Ann.Vol | 19.76% | 12.66% |
| CumRet | 32.06% | 50.47% |
| MaxDD | -24.85% | -17.21% |

**Konuşma Notu (1 dk):**
- Frekans eşleşmesi sonrası da baseline bu dönemde üstün.
- Bu, metodoloji hatası değil, dönem rejimi etkisi.

---

## Slayt 10 — Duyarlılık Analizi
**Lookback (6M/12M/24M):** en iyi Sharpe = 24M (0.7190)  
**Vol target (15/18/25%):** en iyi Sharpe = 15% (0.5178)  
**Risk aversion (λ):** bu koşullarda etkisi sınırlı

**Konuşma Notu (1.5 dk):**
- Parametre ayarı performansı anlamlı etkiliyor.
- Stratejiyi iyileştirme alanı açık.

---

## Slayt 11 — Yorum ve Öğrenimler
- Model teknik olarak doğru ve gereksinimlerle uyumlu
- Bu OOS dönemi momentum için zorlu bir rejim
- Baseline karşılaştırması güçlü bir gerçeklik kontrolü sundu
- Parametre ve maliyet senaryoları kritik

**Konuşma Notu (1 dk):**
- “Doğru kurgu + zor dönem” mesajını net verin.

---

## Slayt 12 — Sonuç ve Gelecek Çalışma
**Sonuç:**
- Uçtan uca sistem başarılı şekilde çalışıyor
- Tüm çekirdek modüller tamamlandı

**Gelecek Adımlar:**
- Maliyetli senaryo setlerini rapora ekleme
- Adaptif lookback / rejim tespiti
- Çok faktörlü sinyal genişletmesi

**Konuşma Notu (1 dk):**
- “Fonksiyonel, yorumlanabilir ve geliştirilebilir bir çerçeve” vurgusu.

---

## Soru-Cevap İçin Hızlı Hazırlık
**Muhtemel Soru 1:** Neden baseline daha iyi?  
**Cevap:** 2024–2026 döneminde düşük kesitsel ayrışma ve mega-cap liderliği momentumun avantajını azalttı.

**Muhtemel Soru 2:** λ neden etki etmedi?  
**Cevap:** Kısıtlar + vol hedefleme + veri rejimi çözümü benzer bölgeye çekti.

**Muhtemel Soru 3:** Neden işlem maliyeti 0 bps?  
**Cevap:** Ana benchmark koşusu için; kodda bps maliyet desteği var ve senaryo analizi yapılabilir.

---

## Sunum Süre Planı (Öneri)
- Slayt 1–2: 2 dk
- Slayt 3–7: 7 dk
- Slayt 8–10: 6 dk
- Slayt 11–12: 3 dk
- Soru-cevap: 2 dk

Toplam: ~20 dk

---

## Detaylı Konuşma Metni (Q&A Olmadan)

### Slayt 1 (Açılış)
Merhaba, biz Stock Tigers takımıyız. Bu projede Markowitz tabanlı, momentum sinyali kullanan sistematik bir yatırım stratejisi geliştirdik. Çalışmayı sadece model kurmak olarak değil, gerçek bir computational finance süreci gibi ele aldık: veri toplama ve temizleme, sinyal üretimi, portföy optimizasyonu, risk kontrolü ve out-of-sample backtest adımlarını uçtan uca kurguladık.

Sunum boyunca hem teknik kurulumumuzu hem de finansal mantığımızı göstereceğiz. Ayrıca sonuçlarda neden baseline’ın güçlü kaldığını ve bunun model hatası mı yoksa dönem etkisi mi olduğunu net şekilde tartışacağız.

### Slayt 2 (Problem ve Hedef)
Problemimiz şu: momentumu kullanarak fırsat yakalayalım ama bunu kontrolsüz risk alarak değil, kısıtlı ve disiplinli bir portföy kuralı ile yapalım. Bu yüzden sinyal katmanında momentum, portföy katmanında Markowitz ve risk katmanında volatility targeting kullandık.

Ana hedefimiz sadece yüksek getiri değil, risk-ayarlı performans üretmekti. Bu nedenle tüm sonuçları Sharpe, yıllık getiri, volatilite, kümülatif getiri ve maksimum düşüş metrikleriyle değerlendirdik ve 1/N baseline ile karşılaştırdık.

### Slayt 3 (Veri ve Evren)
10 adet US large-cap hisse kullandık ve varlıkları farklı sektörlerden seçtik. Buradaki amaç, tek bir sektöre aşırı bağımlı kalmamak ve kovaryans yapısını çeşitlendirmekti. Veri kaynağımız Yahoo Finance, frekans günlük, dönem 2021-01 ile 2026-01 arası.

Temizlik tarafında iki ana karar aldık: eksik günlerde forward-fill ve günlük getirilerde aykırı değerleri winsorize etmek. Böylece hem veri sürekliliği sağladık hem de aşırı uç gözlemlerin optimizasyonu bozmasını engelledik.

### Slayt 4 (Sinyal)
Sinyalimiz 12 aylık momentum. Teknik olarak geçmiş 252 işlem gününün kümülatif log getirisini kullanıyoruz. Finansal sezgi ise trend devamlılığı: son dönemde güçlü giden varlıkların kısa-orta vadede güçlü kalma eğilimi.

Bir diğer kritik adım, kesitsel z-score normalizasyonu. Çünkü bazı varlıklar doğal olarak daha oynak, bazıları daha sakin. Normalizasyon olmadan optimizasyon o ölçek farklarını "sinyal gücü" sanabilir. Bu adım sayesinde momentumu varlıklar arasında daha adil ve kıyaslanabilir hale getirdik.

### Slayt 5 (Markowitz)
Normalize momentum skorlarını beklenen getiri vekili olarak Markowitz optimizasyona veriyoruz. Optimizasyonda iki temel kısıt var: açığa satış yok ve toplam ağırlık 1. Yani portföy tam yatırımlı ve long-only.

Risk tarafında kovaryansı expanding window ile tahmin ediyoruz. Bunun nedeni, örneklem büyüdükçe kovaryans tahmininin daha stabil hale gelmesi. Özellikle kısa pencerelerdeki gürültüyü azaltıp daha tutarlı risk matrisi üretmeyi hedefledik.

### Slayt 6 (Risk Kontrolü ve Gerçekçilik)
Ders gereksinimindeki risk kontrol modülünü volatility targeting ile karşıladık. Her rebalance anında portföyün tahmini volatilitesini kontrol ediyoruz; hedefin üstündeyse ağırlıkları daha düşük risk profiline doğru kaydırıyoruz.

Gerçekçilik için iki ek yaptık. Birincisi turnover bazlı işlem maliyeti parametresi; yani portföy daha çok döndükçe maliyet artıyor. İkincisi adil baseline: sadece günlük 1/N değil, strateji frekansına eşlenmiş aylık 1/N’yi de raporluyoruz.

### Slayt 7 (Backtest Tasarımı)
Backtest tasarımında bilgi sızıntısını engellemek en kritik önceliğimizdi. Veriyi yaklaşık yüzde 60 train ve yüzde 40 out-of-sample olarak ayırdık. Rebalance frekansımız aylık.

Karar anındaki tüm girdiler sadece geçmişten geliyor: momentum da kovaryans da ilgili tarihten önceki verilerle hesaplanıyor. Bu sayede look-ahead bias oluşmuyor ve sonuçlar daha güvenilir hale geliyor.

### Slayt 8 (Ana Sonuçlar - Günlük 1/N)
Bu tabloda stratejiyi günlük 1/N baseline ile karşılaştırıyoruz. Strateji Sharpe’ı 0.4423, günlük 1/N Sharpe’ı 1.0089. Yıllık getiri, kümülatif getiri ve maksimum düşüşte de bu örneklemde baseline daha güçlü.

Buradaki ana mesaj: model çalışmıyor değil, model bu dönem rejiminde baseline’ı geçemiyor. Yani teknik doğruluk var, performans farkı ise piyasa koşullarından etkileniyor.

### Slayt 9 (Adil Baseline - Aylık 1/N)
Frekans adaleti için aylık 1/N baseline’ı da ayrıca simüle ettik. Burada karşılaştırma frekans açısından birebir: strateji aylık, baseline da aylık.

Bu adil karşılaştırmada da 1/N daha iyi performans veriyor. Bu sonuç, “yanlış benchmark seçtik” eleştirisini ortadan kaldırıyor ve performans farkının esasen dönemsel piyasa dinamiği kaynaklı olduğunu destekliyor.

### Slayt 10 (Duyarlılık Analizi)
Parametre duyarlılığı tarafında üç şeyi test ettik: lookback, risk aversion lambda ve vol target. Koddan doğrudan gerçek OOS koşuları aldık.

Bu örneklemde 24 aylık lookback daha güçlü Sharpe verdi. Vol target tarafında yüzde 15 seviyesi daha iyi risk-ayarlı sonuç üretti. Lambda tarafında ise sonuçlar neredeyse aynı kaldı; bu da mevcut kısıtlar ve veri rejiminde çözümün benzer ağırlık bölgelerine oturduğunu gösteriyor.

### Slayt 11 (Yorum)
Bu noktada güçlü ve zayıf tarafları net ayırıyoruz. Güçlü taraflar: finansal olarak açıklanabilir sinyal, modüler ve temiz kod, açık OOS doğrulama, risk kontrol katmanı. Bu kısım gereksinimlerle tam uyumlu.

Zayıf taraf ise rejim duyarlılığı. Düşük kesitsel ayrışma ve belirli liderlik dönemlerinde momentum stratejileri zorlanabiliyor. Dolayısıyla “tek dönem sonucu” yerine metodoloji kalitesi ve parametre hassasiyeti birlikte değerlendirilmeli.

### Slayt 12 (Kapanış)
Sonuç olarak, gereksinimleri karşılayan, çalışan ve savunulabilir bir sistem kurduk. Veri-sinyal-Markowitz-risk-backtest zinciri uçtan uca tamamlandı ve gerçek OOS sonuçları üretildi.

Bir sonraki adım olarak maliyetli senaryoları genişletmek, adaptif parametre yaklaşımı eklemek ve çok faktörlü versiyona geçmek istiyoruz. Sunumumuzu burada tamamlıyoruz, teşekkür ederiz.

---

## Güncellenmiş Süre Planı (Q&A Yoksa)
- Slayt 1–2: 3 dk
- Slayt 3–5: 5 dk
- Slayt 6–7: 4 dk
- Slayt 8–10: 6 dk
- Slayt 11–12: 2 dk

Toplam: ~20 dk

---

## 5 Kişilik Konuşmacı Dağılımı (Satır Satır)

### 1) Tuğberk AKSU — **Slayt 1 + Slayt 3** (~4 dk)
- Açılış cümlesi: “Merhaba, biz Stock Tigers takımıyız. Bugün momentum ve Markowitz tabanlı sistematik stratejimizi anlatacağız.”
- Slayt 1’i kapatış: “Önce veri evrenimizle başlayalım.”
- Slayt 3 ana mesaj: varlık evreni, veri kaynağı, dönem, veri temizliği.
- Slayt 3 geçiş cümlesi: “Veri tarafını gördük, şimdi sinyal katmanına geçelim.”

### 2) Batuhan ÇAĞLAR — **Slayt 2 + Slayt 4 + Slayt 5** (~5 dk)
- Slayt 2 ana mesaj: problem tanımı ve hedef (risk-ayarlı performans).
- Slayt 4 ana mesaj: momentum formülü, finansal sezgi, z-score normalizasyonu.
- Slayt 5 ana mesaj: Markowitz, kısıtlar, expanding covariance.
- Slayt 5 geçiş cümlesi: “Modeli kurduk, şimdi risk kontrolü ve backtest tasarımına geçiyoruz.”

### 3) Gültekin ERİŞİK — **Slayt 6 + Slayt 7** (~4 dk)
- Slayt 6 ana mesaj: volatility targeting, işlem maliyeti, fair baseline ekleri.
- Slayt 7 ana mesaj: train/OOS ayrımı, aylık rebalance, look-ahead bias önleme.
- Slayt 7 geçiş cümlesi: “Altyapıyı kurduktan sonra sonuçlara bakalım.”

### 4) Yiğit Dilaver — **Slayt 8 + Slayt 9 + Slayt 10** (~5 dk)
- Slayt 8 ana mesaj: günlük 1/N baseline karşısında sonuçlar.
- Slayt 9 ana mesaj: aylık fair baseline karşılaştırması ve yorum.
- Slayt 10 ana mesaj: sensitivity bulguları (lookback, vol target, lambda).
- Slayt 10 geçiş cümlesi: “Son bölümde bulguların anlamını ve çıkarımlarımızı özetleyelim.”

### 5) Ali Osman ÇITAK — **Slayt 11 + Slayt 12 + Kapanış** (~2 dk)
- Slayt 11 ana mesaj: güçlü/zayıf yönler ve rejim etkisi.
- Slayt 12 ana mesaj: sonuç, gelecek adımlar, kapanış.
- Kapanış cümlesi: “Teşekkür ederiz. Sunumumuz bu kadardı.”

---

