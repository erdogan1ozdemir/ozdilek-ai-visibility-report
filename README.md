# İki Evrende Yaşayan Marka — Özdilekteyim AI Görünürlük Raporu

Türkiye'nin önde gelen AI asistanlarına (ChatGPT + Gemini) 56 marka-nötr soru sorarak Özdilekteyim'in
yapay zekâ cevaplarındaki görünürlüğünü ölçen araştırma raporu. İlk baskı: **Temmuz 2026**.

**Ana bulgu:** AI modelleri Özdilek'i marka olarak %65,2 görünürlükle 2. sıraya koyuyor;
alışveriş adresi olarak ise %5,4 ile 5. sıraya düşürüyor — 12 katlık makas.

## Yapı

```
index.html   → tek dosyalık rapor (statik, bağımlılık yok; Google Fonts CDN hariç)
data/        → ham veri: AI görünürlük aracı CSV dışa aktarımları + panel metrikleri
  ├─ marka-gorunurluk-analizi.csv            (domain düzeyi atıflar, marka merceği)
  ├─ pazaryeri-gorunurluk-analizi.csv        (domain düzeyi atıflar, pazaryeri merceği)
  ├─ marka-gorunurluk-analizi-url-citation.csv
  ├─ pazaryeri-gorunurluk-analizi-url-citations.csv
  ├─ dashboard.json                          (panel KPI/sıralama/heatmap aktarımı)
  ├─ report-data.json                        (CSV agregasyonu — analyze.py çıktısı)
  └─ analyze.py                              (agregasyon scripti)
```

## Deploy (Vercel)

Statik site — ek yapılandırma gerekmez:

```bash
vercel --prod
```

veya GitHub repo'yu Vercel'e bağlayıp framework preset olarak **Other** seçmek yeterli
(`index.html` kök dizinde).

## Metodoloji özeti

- 56 marka-nötr prompt: 28 **marka merceği** ("hangi marka iyi?") + 28 **pazaryeri merceği** ("nereden alayım?")
- 2 model: ChatGPT + Gemini · model başına mercek başına 55–56 çalıştırma · son 7 gün penceresi
- 2.098 görünür atıf, 686 tekil kaynak domain
- Soru-düzeyi atıf toplamları her kaynağın "Top Prompts" (ilk 5) kolonundan derlenir → raporda "görünür atıf"
- Çeyreklik tekrar planlanıyor (trend + 5 modelli karşılaştırma)
