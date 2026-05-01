# Multi-Sector Momentum Strategy using Markowitz Allocator

## 📋 Genel Bakış

Bu proje, **momentum sinyalini** Markowitz portföy optimizasyonu ile birleştirerek risk-kontrollü bir yatırım stratejisi oluşturuyor. Stratejinin performansı out-of-sample dönemde eşit ağırlık (1/N) baseline ile karşılaştırılıyor.

### Temel Özellikler
- ✅ **10 adet US Large-Cap hisse** farklı sektörlerden (AAPL, JNJ, XOM, PG, JPM, NEE, LMT, GOLD, AMT, VZ)
- ✅ **12 aylık momentum sinyali** trend devamlılığı temeline dayalı
- ✅ **Dinamik Markowitz optimizasyonu** aylık rebalance ile
- ✅ **Volatilite hedefleme** risk kontrolü için
- ✅ **Titiz backtest metodolojisi** look-ahead bias olmaksızın

---

## 📊 Proje Yapısı

```
471_Project/
├── main.py                 # Ana çalıştırma dosyası
├── config.py               # Konfigürasyon parametreleri
├── data.py                 # Veri indirme ve hazırlama
├── signals.py              # Momentum sinyal hesaplaması
├── markowitz.py            # Markowitz optimizasyonu
├── backtest.py             # Backtest motoruna ve metrikleri
├── requirements.txt        # Python bağımlılıkları
├── README.md               # Bu dosya
```

---

## 🔧 Kurulum

### Gereksinimler
- Python 3.8+
- pip veya conda

### Adım 1: Repository'i klonla
```bash
git clone https://github.com/nalkapon/markowitz.git
cd markowitz
```

### Adım 2: Sanal ortam oluştur ve etkinleştir
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Adım 3: Bağımlılıkları yükle
```bash
pip install -r requirements.txt
```

---

## 🚀 Çalıştırma

Stratejiyi backtest etmek için:
```bash
python main.py
```

Bu komut şu adımları gerçekleştirir:

1. **Veri İndirme:** Yahoo Finance'dan günlük OHLCV verilerini indirir (2021-01-01 → 2026-01-31)
2. **Veri Hazırlama:** Getirileri hesaplar, eksik veriler için forward-fill, winsorize ile aykırı değerleri temizler
3. **Train/Test Ayrımı:** Out-of-sample bias olmaksızın %60 train, %40 test (OOS: 2024-01-19 → 2026-01-31)
4. **Backtest:** Aylık rebalance ile momentum+Markowitz stratejisini ve 1/N baseline'ı test eder
5. **Raporlama:** Her iki portföy için Sharpe oranı, yıllık getiri, volatilite ve maksimum düşüş yazdırır

---

## ⚙️ Konfigürasyon

`config.py` dosyasında aşağıdaki parametreleri düzenleyebilirsiniz:

| Parametre | Varsayılan | Açıklama |
|-----------|-----------|---------|
| `TICKERS` | AAPL, JNJ, ... | 10 adet hisse ticker'ı |
| `START_DATE` | 2021-01-01 | Veri başlangıç tarihi |
| `END_DATE` | 2026-01-31 | Veri bitiş tarihi |
| `MOMENTUM_LOOKBACK_MONTHS` | 12 | Momentum hesabı için geri bakış penceresi (ay) |
| `ROLLING_WINDOW_DAYS` | 252 | Kovaryans tahmini için geri bakış penceresi (gün) |
| `OOS_START_RATIO` | 0.60 | Out-of-sample başlangıcı (0.6 = ilk %60 train) |
| `VOLATILITY_TARGET` | 0.18 | Yıllık hedef volatilite |
| `RISK_FREE_RATE_ANNUAL` | 0.03 | Sharpe oranı hesabı için yıllık risksiz oran |
| `TRANSACTION_COST_BPS` | 10 | İşlem maliyeti (basispoint cinsinden) |

---

## 📈 Strateji Tasarımı

### 1. Sinyal: Momentum
Kesitsel normalize edilmiş 12 aylık momentum:
$$M_{t,i} = \frac{\sum_{j=1}^{252} r_{t-j,i} - \mu_t}{\sigma_t}$$

Burada $\mu_t$ ve $\sigma_t$ kesitsel ortalama ve standart sapma.

### 2. Portföy Optimizasyonu: Markowitz
$$\max_w \left(\tilde{\mu}^T w - \frac{\lambda}{2} w^T \Sigma w\right)$$

**Kısıtlar:**
- $0 \le w_i \le 1$ (açığa satış yok, tam kullanım)
- $\sum_i w_i = 1$ (bütçe kısıtı)

**Girdiler:**
- Beklenen getiri vekili: normalize momentum skorları
- Kovaryans matrisi: 252 günlük rolling pencere

### 3. Risk Kontrolü: Volatilite Hedefleme
Tahmini portföy volatilitesi hedefi aşarsa ağırlıklar orantılı şekilde indirilerek risksiz varlıkla harmanlama yapılır.

### 4. Rebalance
Stratejide **aylık rebalance** uygulanır. Her ayın sonunda pozisyonlar yeniden optimize edilir.

---

## 📊 Sonuçlar Özeti

Out-of-sample dönemde (2024-01-19 → 2026-01-31) elde edilen sonuçlar:

| Metrik | Momentum+Markowitz | 1/N Baseline |
|--------|---:|---:|
| Sharpe Oranı | 0.4423 | 1.2002 |
| Yıllık Getiri | 13.74% | 20.19% |
| Yıllık Volatilite | 19.76% | 12.66% |
| Kümülatif Getiri | 32.06% | 50.47% |
| Maksimum Düşüş | -24.85% | -17.21% |

**Yorum:** Bu OOS döneminde momentum rejimi zayıf kalmış ve baseline daha üstün performans göstermiştir. Bu metodoloji hatasını değil, pazar rejimi etkisini yansıtır.

---

## 🔍 Dosya Açıklamaları

### `main.py`
Projenin giriş noktası. Tüm modülleri koordine eder:
- Veri indirme ve hazırlama
- Train/test ayrımı
- Backtest çalıştırma
- Sonuç raporlaması

### `config.py`
Tüm parametrelerin merkezi tanımlandığı dosya. Stratejiyi özelleştirmek için buradan başlayın.

### `data.py`
- `download_data()`: Yahoo Finance'dan veri indir
- `prepare_returns()`: Getirileri hesapla, winsorize ve forward-fill
- `expand_windows()`: Belirli bir tarihten önce tüm veriyi dahil et

### `signals.py`
- `calculate_momentum()`: Kesitsel normalize momentum hesapla
- `rolling_momentum()`: Belirli tarih aralığında momentum

### `markowitz.py`
- `optimize_portfolio()`: Markowitz optimizasyonunu çalıştır
- `apply_vol_targeting()`: Volatilite hedeflemesi uygula
- `backtest_mean_variance()`: Backtest stratejisi

### `backtest.py`
- `backtest_strategy()`: Tam backtest motorune
- `calculate_metrics()`: Sharpe, getiri, volatilite vb. hesapla

---

## 🧪 Duyarlılık Analizi

Strateji parametreleri üzerine yapılan test sonuçları:

| Parametre | Değer | Sharpe |
|-----------|--------|--------|
| Momentum Lookback | 6 ay | 0.3912 |
| Momentum Lookback | 12 ay | 0.4423 |
| Momentum Lookback | **24 ay** | **0.7190** |
| Vol Target | 15% | 0.5178 |
| Vol Target | 18% | 0.4423 |
| Vol Target | 25% | 0.4018 |


