# -*- coding: utf-8 -*-
"""
==============================================================================
AR AI STUDIO v4.5 — MODÜL 10: DOĞRUDAN SOHBET ENTEGRELİ KAPSAMLI WIKIPEDIA MOTORU
Sohbet Botundan Otomatik "Araştırılıyor, Wikipedia'ya gidiliyor..." Akışı,
Türkçe (tr.wikipedia.org) & İngilizce (en.wikipedia.org) Canlı Arama,
Cümle Bozukluklarını Temizleme ve Geniş Yerleşik Ansiklopedi (modul_10_wikipedia.py)
==============================================================================
"""
import importlib.util
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import streamlit as st

_MODUL_DIZINI = os.path.dirname(os.path.abspath(__file__))
if _MODUL_DIZINI not in sys.path:
    sys.path.insert(0, _MODUL_DIZINI)


def _guvenli_modul_yukle(modul_adi: str):
    if modul_adi in sys.modules and getattr(sys.modules[modul_adi], "__file__", None):
        return sys.modules[modul_adi]
    yol = os.path.join(_MODUL_DIZINI, f"{modul_adi}.py")
    if os.path.exists(yol):
        spec = importlib.util.spec_from_file_location(modul_adi, yol)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[modul_adi] = mod
            spec.loader.exec_module(mod)
            return mod
    return __import__(modul_adi)


_m1 = _guvenli_modul_yukle("modul_1_arayuz_ve_tema")
_m5 = _guvenli_modul_yukle("modul_5_dil_ve_cevirmeli_kartlar")
bilgi_karti_olustur = _m1.bilgi_karti_olustur
guvenli_cevir = _m5.guvenli_cevir

# Genişletilmiş Yerleşik Yedek Wikipedia Ansiklopedisi (İnternet yavaşsa/kesikse bile sıfır cümle bozukluğuyla anında yanıt verir)
YEDEK_WIKIPEDIA_MADDELERI = {
    "yapay zeka": {
        "baslik": "Yapay zekâ",
        "ozet": (
            "Yapay zekâ (YZ), bir bilgisayarın veya bilgisayar kontrolündeki bir robotun çeşitli faaliyetleri zeki canlılara benzer şekilde yerine getirme kabiliyetidir. "
            "İnsan zekâsına özgü öğrenme, akıl yürütme, problem çözme, algılama ve doğal dil anlama gibi yüksek bilişsel işlevleri моделleyen yazılım ve donanım sistemlerini kapsar.\n\n"
            "Günümüzde yapay zekâ; makine öğrenmesi, derin öğrenme, büyük dil modelleri (LLM), bilgisayarlı görü ve otonom robotik sistemlerde temel teknoloji olarak kullanılmaktadır."
        ),
        "url": "https://tr.wikipedia.org/wiki/Yapay_zek%C3%A2",
        "gorsel": "",
        "bolumler": ["Tarihçe", "Makine Öğrenmesi", "Derin Öğrenme", "Kullanım Alanları"],
    },
    "insansız hava aracı": {
        "baslik": "İnsansız hava aracı (İHA)",
        "ozet": (
            "İnsansız hava aracı (İHA), içerisinde insan pilot bulunmadan uzaktan kumanda ile veya otonom uçuş kontrol bilgisayarları sayesinde kendi kendine uçabilen hava aracıdır. "
            "Sivil alanda haritalama, tarım, arama-kurtarma ve yangınla mücadelede; savunma alanında ise keşif, gözetleme ve operasyonel görevlerde yaygın olarak kullanılır."
        ),
        "url": "https://tr.wikipedia.org/wiki/%C4%B0nsans%C4%B1z_hava_arac%C4%B1",
        "gorsel": "",
        "bolumler": ["Tarihçe", "Otonom Uçuş Kontrolü", "Sensör ve Aviyonik Sistemler"],
    },
    "kara delik": {
        "baslik": "Kara delik",
        "ozet": (
            "Kara delik, astrofizikte kütleçekim alanı her türlü maddesel oluşumun ve ışık dahil tüm elektromanyetik radyasyonun kendisinden kaçmasına izin vermeyecek derecede güçlü olan kozmik bir gök cismidir. "
            "Genel görelilik kuramına göre yeterince sıkışmış bir kütle, uzay-zamanı bükerek olay ufku adı verilen geri dönülmez bir sınır oluşturur.\n\n"
            "Büyük kütleli yıldızların süpernova patlamasıyla çökmeleri sonucunda yıldızsal kara delikler, galaksilerin merkezlerinde ise milyonlarca Güneş kütleli süper kütleli kara delikler bulunur."
        ),
        "url": "https://tr.wikipedia.org/wiki/Kara_delik",
        "gorsel": "",
        "bolumler": ["Olay Ufku", "Genel Görelilik", "Yıldızsal ve Süper Kütleli Kara Delikler"],
    },
    "karadelik": {
        "baslik": "Kara delik",
        "ozet": (
            "Kara delik, astrofizikte kütleçekim alanı ışık dahil hiçbir maddenin veya radyasyonun kaçmasına izin vermeyecek kadar güçlü olan kozmik gök cismidir. "
            "Sınırına 'olay ufku' adı verilir; büyük kütleli yıldızların ömrünü tamamlayıp kendi içine çökmesiyle oluşur."
        ),
        "url": "https://tr.wikipedia.org/wiki/Kara_delik",
        "gorsel": "",
        "bolumler": ["Olay Ufku", "Oluşumu", "Gözlemlenmesi"],
    },
    "mars": {
        "baslik": "Mars (Kızıl Gezegen)",
        "ozet": (
            "Mars, Güneş Sistemi'nde Güneş'e yakınlık sırasına göre dördüncü gezegendir. Yüzeyindeki yaygın demir oksit nedeniyle kızılımsı bir görünüme sahip olduğu için 'Kızıl Gezegen' olarak da adlandırılır.\n\n"
            "İnce bir atmosferi olan Mars; Güneş Sistemi'nin en yüksek dağı olan Olympus Mons'a ve en büyük kanyon sistemlerinden Valles Marineris'e ev sahipliği yapar. İki küçük doğal uydusu vardır: Phobos ve Deimos."
        ),
        "url": "https://tr.wikipedia.org/wiki/Mars",
        "gorsel": "",
        "bolumler": ["Fiziksel Özellikler", "Atmosfer ve İklim", "Phobos ve Deimos", "Uzay Araştırmaları"],
    },
    "osmanlı imparatorluğu": {
        "baslik": "Osmanlı İmparatorluğu",
        "ozet": (
            "Osmanlı İmparatorluğu veya Osmanlı Devleti, 1299 yılında Osman Gazi tarafından Söğüt ve Domaniç çevresinde kurulan, 1453'te Fatih Sultan Mehmet'in İstanbul'u fethiyle imparatorluk gücüne ulaşan ve 1922 yılına kadar üç kıtada (Avrupa, Asya ve Afrika) hüküm süren Türk-İslam devletidir.\n\n"
            "En geniş sınırlarına 16. ve 17. yüzyıllarda ulaşmış; bilim, mimari, hukuk ve sanatta dünya tarihine derin izler bırakmıştır."
        ),
        "url": "https://tr.wikipedia.org/wiki/Osmanl%C4%B1_%C4%B0mparatorlu%C4%9Fu",
        "gorsel": "",
        "bolumler": ["Kuruluş Dönemi (1299)", "Yükseliş Dönemi (1453)", "Bilim ve Kültür"],
    },
    "albert einstein": {
        "baslik": "Albert Einstein",
        "ozet": (
            "Albert Einstein (14 Mart 1879 – 18 Nisan 1955), modern fiziğin iki temel direğinden biri olan Özel ve Genel Görelilik (İzafiyet) kuramlarını geliştiren teorik fizikçidir. "
            "Kütle-enerji eşdeğerliği formülü (E = mc²) ve fotoelektrik etki yasasıyla 1921 Nobel Fizik Ödülü'nü kazanmıştır."
        ),
        "url": "https://tr.wikipedia.org/wiki/Albert_Einstein",
        "gorsel": "",
        "bolumler": ["Özel ve Genel Görelilik", "Fotoelektrik Etki", "Nobel Fizik Ödülü"],
    },
    "dünya": {
        "baslik": "Dünya",
        "ozet": (
            "Dünya, Güneş Sistemi'nde Güneş'e en yakın üçüncü gezegen olup üzerinde yaşam ve sıvı su barındırdığı bilinen tek astronomik cisimdir. "
            "Kendi ekseni etrafındaki dönüşünü yaklaşık 24 saatte (1 gün) tamamlar ve bu dönüş açısal momentumun korunumu sayesinde gece ile gündüzün oluşmasını sağlar. Güneş etrafındaki yörünge turunu ise 365 gün 6 saatte tamamlar."
        ),
        "url": "https://tr.wikipedia.org/wiki/D%C3%BCnya",
        "gorsel": "",
        "bolumler": ["Dönüş Hareketi", "Atmosfer ve Biyosfer", "İç Yapısı"],
    },
    "kuantum mekaniği": {
        "baslik": "Kuantum mekaniği",
        "ozet": (
            "Kuantum mekaniği, atom ve atom altı parçacıkların (elektron, foton, kuark) davranışlarını inceleyen temel fizik kuramıdır. "
            "Enerjinin kesikli paketçikler (kuanta) halinde yayıldığını, dalga-parçacık ikiliğini ve Heisenberg belirsizlik ilkesini açıklar."
        ),
        "url": "https://tr.wikipedia.org/wiki/Kuantum_mekani%C4%9Fi",
        "gorsel": "",
        "bolumler": ["Dalga-Parçacık İkiliği", "Belirsizlik İlkesi", "Kuantum Bilgisayarlar"],
    },
    "python": {
        "baslik": "Python (programlama dili)",
        "ozet": (
            "Python, Guido van Rossum tarafından 1991 yılında geliştirilen; okunabilirliği yüksek, nesne yönelimli, yorumlamalı ve çok amaçlı bir programlama dilidir. "
            "Yapay zekâ, veri bilimi, görüntü işleme (OpenCV), robotik (Raspberry Pi), web geliştirme (Streamlit, Django) ve otomasyon alanlarında dünyanın en popüler dilidir."
        ),
        "url": "https://tr.wikipedia.org/wiki/Python_(programlama_dili)",
        "gorsel": "",
        "bolumler": ["Tasarım Felsefesi", "Yapay Zekâ ve Veri Bilimi", "Kütüphane Ekosistemi"],
    },
    "dna": {
        "baslik": "Deoksiribonükleik asit (DNA)",
        "ozet": (
            "DNA (Deoksiribonükleik asit), tüm canlı organizmaların ve birçok virüsün yaşamsal işlevleri, büyümesi ve çoğalması için gerekli olan genetik talimatları taşıyan çift sarmallı nükleik asit molekülüdür. "
            "Adenin (A), Timin (T), Guanin (G) ve Sitozin (C) bazlarının dizilimiyle genetik kodu oluşturur."
        ),
        "url": "https://tr.wikipedia.org/wiki/DNA",
        "gorsel": "",
        "bolumler": ["Çift Sarmal Yapı", "Genetik Kod", "Replikasyon"],
    },
}


def wikipedia_metnini_temizle(ham_metin: str) -> str:
    """
    Wikipedia API'sinden gelen metindeki [1], [2] dipnotlarını, bozuk parantezleri,
    IPA telaffuz kalıntılarını ve kopuk satırları temizleyerek akıcı Türkçe cümleler üretir.
    """
    if not ham_metin:
        return ""
    metin = re.sub(r"\[\d+\]|\[kaynak belirtilmeli\]|\[d[üu]zenle\]|\[not \d+\]", "", ham_metin, flags=re.IGNORECASE)
    # Boş veya sadece noktalama içeren parantezleri kaldır
    metin = re.sub(r"\(\s*[;,:\-]*\s*\)", "", metin)
    # Parantez başındaki bozuk noktalama: "(; İngilizce: ...)" -> "(İngilizce: ...)"
    metin = re.sub(r"\(\s*[;,]+\s*", "(", metin)
    # Noktalama öncesi fazla boşlukları düzelt
    metin = re.sub(r"\s+([.,;:!?])", r"\1", metin)
    metin = re.sub(r"[ \t]+", " ", metin)
    metin = re.sub(r"\n{3,}", "\n\n", metin)
    # Bölüm başlıklarını (== Başlık ==) temiz alt başlıklara dönüştür
    metin = re.sub(r"===\s*(.+?)\s*===", r"\n**🔹 \1**", metin)
    metin = re.sub(r"==\s*(.+?)\s*==", r"\n### 📌 \1", metin)
    return metin.strip()


def wikipedia_konu_ayikla(kullanici_girdisi: str) -> str:
    """
    Kullanıcının doğal sohbet cümlesinden Wikipedia'da aranacak saf Türkçe konu başlığını
    (Türkçe karakterleri bozmadan!) ayıklar.
    Örn: 'Osmanlı İmparatorluğu ne zaman kuruldu?' -> 'Osmanlı İmparatorluğu'
         'Mars gezegeni hakkında bilgi ver' -> 'Mars'
         'Karadelik nedir?' -> 'Kara delik'
    """
    temiz = kullanici_girdisi.strip()
    # Başındaki komut ve hitapları temizle
    temiz = re.sub(
        r"^(?:wikipedia|vikipedi|wiki|araştır|arastir|bana|lütfen|lutfen|acaba|ar|hey ar|merhaba|selam)\s*[:\-]?\s*",
        "",
        temiz,
        flags=re.IGNORECASE,
    ).strip()
    temiz = re.sub(r"^(?:bana|lütfen|lutfen|biraz)\s+", "", temiz, flags=re.IGNORECASE).strip()

    # Sonundaki soru kalıplarını ve fiilleri temizle
    kaliplar = [
        r"\s+hakkında\s+(?:detaylı\s+|kapsamlı\s+|kısa\s+)?bilgi\s*(?:verir\s*misin|ver|anlat|söyle)?$",
        r"\s+hakkında\s+ne\s+(?:biliyorsun|düşünüyorsun|dusunuyorsun)$",
        r"\s+hakkında$",
        r"\s+ne\s+zaman\s+(?:kuruldu|yıkıldı|doğdu|öldü|yapıldı|keşfedildi|icat\s+edildi|başladı|bitti)$",
        r"\s+nasıl\s+(?:oluşur|çalışır|yapılır|kuruldu|keşfedildi)$",
        r"\s+neden\s+(?:dönüyor|döner|oluşur|önemlidir|mavidir)$",
        r"\s+ile\s+ilgili\s+bilgi\s*(?:ver)?$",
        r"\s+kimdir$",
        r"\s+kim$",
        r"\s+nedir$",
        r"\s+ne\s+demektir$",
        r"\s+ne\s+demek$",
        r"\s+nerededir$",
        r"\s+nerede\s+bulunur$",
        r"\s+nerede$",
        r"\s+neresi(?:dir)?$",
        r"\s+anlatır\s*mısın$",
        r"\s+anlat$",
        r"\s+araştır(?:ır\s*mısın)?$",
        r"\s+vikipedi(?:\s*de\s*ara)?$",
        r"\s+wikipedia(?:\s*da\s*ara)?$",
    ]
    temiz = temiz.strip("?!.,;:\"' ")
    for k in kaliplar:
        temiz = re.sub(k, "", temiz, flags=re.IGNORECASE).strip("?!.,;:\"' ")

    # 'Mars gezegeni' -> 'Mars' gibi gereksiz tür eklerini sadeleştir
    temiz = re.sub(r"^mars\s+gezegeni$", "Mars", temiz, flags=re.IGNORECASE)
    temiz = re.sub(r"^karadelik$", "Kara delik", temiz, flags=re.IGNORECASE)
    return temiz.strip("?!.,;:\"' ")


def _http_json_getir(url: str, timeout: int = 7):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ArAIStudio/4.5 (Ahmet Educational Assistant; Python urllib)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def wikipedia_arama_onerileri(sorgu: str, dil: str = "tr", limit: int = 6) -> list:
    """Wikipedia'da sorguya en yakın madde başlıklarını ve kısa açıklamalarını arar."""
    konu = wikipedia_konu_ayikla(sorgu)
    if not konu:
        return []
    try:
        q = urllib.parse.quote(konu)
        url = (
            f"https://{dil}.wikipedia.org/w/api.php?"
            f"action=query&list=search&srsearch={q}&srlimit={limit}&format=json&utf8=1"
        )
        veri = _http_json_getir(url)
        sonuclar = []
        for item in veri.get("query", {}).get("search", []):
            snippet = re.sub(r"<[^>]+>", "", item.get("snippet", ""))
            sonuclar.append({
                "baslik": item.get("title", ""),
                "kisa_ozet": wikipedia_metnini_temizle(snippet),
            })
        return sonuclar
    except Exception:
        return []


def wikipedia_madde_getir(sorgu: str, dil: str = "tr", detay_karakter: int = 2400) -> dict:
    """
    Wikipedia'dan maddenin tam düzgün özetini, alt bölümlerini, kapak görselini
    ve kaynak bağlantısını getirir. Türkçe Vikipedi'de bulunamazsa İngilizce'den
    otomatik arayıp Türkçeye çevirme desteği sunar; çevrimdışıysa yerleşik yedekten döner.
    """
    konu = wikipedia_konu_ayikla(sorgu)
    if not konu:
        return {"basarili": False, "hata": "Lütfen aramak istediğiniz bir konu başlığı girin."}

    def _tek_dil_cek(aranan_baslik: str, hedef_dil: str):
        adaylar = wikipedia_arama_onerileri(aranan_baslik, dil=hedef_dil, limit=5)
        secilen_baslik = adaylar[0]["baslik"] if adaylar else aranan_baslik

        q_title = urllib.parse.quote(secilen_baslik)
        detay_url = (
            f"https://{hedef_dil}.wikipedia.org/w/api.php?"
            f"action=query&prop=extracts|pageimages|info&inprop=url&pithumbsize=500"
            f"&explaintext=1&redirects=1&titles={q_title}&format=json&utf8=1"
        )
        veri = _http_json_getir(detay_url)
        sayfalar = veri.get("query", {}).get("pages", {})
        for pid, sayfa in sayfalar.items():
            if str(pid) == "-1" or "missing" in sayfa:
                continue
            ham_ozet = sayfa.get("extract", "")
            if not ham_ozet.strip():
                continue
            temiz_ozet = wikipedia_metnini_temizle(ham_ozet)
            if len(temiz_ozet) > detay_karakter:
                kesilmis = temiz_ozet[:detay_karakter]
                son_nokta = kesilmis.rfind(".")
                temiz_ozet = kesilmis[:son_nokta + 1] if son_nokta > 250 else kesilmis + "..."

            bolumler = re.findall(r"^### 📌 (.+)$", temiz_ozet, flags=re.MULTILINE)
            gorsel_url = sayfa.get("thumbnail", {}).get("source", "")
            tam_url = sayfa.get("fullurl", f"https://{hedef_dil}.wikipedia.org/wiki/{q_title}")
            return {
                "basarili": True,
                "baslik": sayfa.get("title", secilen_baslik),
                "ozet": temiz_ozet,
                "gorsel": gorsel_url,
                "url": tam_url,
                "dil": "Türkçe Vikipedi" if hedef_dil == "tr" else "English Wikipedia",
                "bolumler": bolumler,
                "diger_oneriler": [a["baslik"] for a in adaylar[1:5]],
            }
        return None

    try:
        sonuc = _tek_dil_cek(konu, dil)
        if sonuc:
            return sonuc
        if dil == "tr":
            en_sonuc = _tek_dil_cek(konu, "en")
            if en_sonuc:
                try:
                    en_sonuc["ozet"] = guvenli_cevir(en_sonuc["ozet"][:1800], src="en", dest="tr")
                    en_sonuc["dil"] = "Wikipedia (İngilizce -> Türkçe Çeviri)"
                except Exception:
                    pass
                return en_sonuc
    except Exception:
        pass

    # Çevrimdışı / Hızlı Yedek Ansiklopedi Kontrolü
    konu_kucuk = konu.replace("İ", "i").replace("I", "ı").lower().replace("\u0307", "").strip()
    for anahtar, y in YEDEK_WIKIPEDIA_MADDELERI.items():
        if anahtar == konu_kucuk or anahtar in konu_kucuk or konu_kucuk in anahtar:
            return {
                "basarili": True,
                "baslik": y["baslik"],
                "ozet": y["ozet"],
                "gorsel": y["gorsel"],
                "url": y["url"],
                "dil": "Wikipedia Ansiklopedi Belleği",
                "bolumler": y["bolumler"],
                "diger_oneriler": [],
            }

    return {
        "basarili": False,
        "hata": f"Wikipedia'da '{konu}' ile ilgili madde bulunamadı veya internet bağlantısı kurulamadı.",
    }


def wikipedia_sonucunu_metne_formatla(sonuc: dict) -> str:
    """Sohbet botu için akıcı, düzgün cümleli ve kaynak bağlantılı Wikipedia yanıtı üretir."""
    if not sonuc.get("basarili"):
        return f"🌐 **Wikipedia:** {sonuc.get('hata', 'Sonuç bulunamadı.')}"

    satirlar = [
        f"### 🌐 Wikipedia: **{sonuc['baslik']}**",
        f"*🔍 Araştırıldı — Kaynak: `{sonuc.get('dil', 'Türkçe Vikipedi')}`* | [🔗 Wikipedia Sayfasını Aç]({sonuc.get('url', '')})\n",
        sonuc["ozet"],
    ]
    if sonuc.get("diger_oneriler"):
        satirlar.append("\n**🔎 İlgili Diğer Başlıklar:** " + " • ".join(f"`{b}`" for b in sonuc["diger_oneriler"]))
    return "\n".join(satirlar)


# ==============================================================================
# WIKIPEDIA STÜDYOSU ARAYÜZÜ (Eğitim & Ansiklopedi Merkezinden de Erişilebilir)
# ==============================================================================
def wikipedia_studyosu_goster(sesli_soyle_fn):
    st.markdown("#### 🌐 Wikipedia (Vikipedi) Canlı Ansiklopedi Araştırma Ekranı")
    st.caption("💡 İpucu: Burayı kullanabileceğin gibi doğrudan **Ana Sohbet Botuna** istediğin konuyu yazarak da Wikipedia'dan araştırma yaptırabilirsin!")

    ust1, ust2 = st.columns([1.2, 2.0])
    with ust1:
        st.session_state.wikipedia_aktif = st.toggle(
            "🌐 Sohbette Otomatik Wikipedia (Aç / Kapat)",
            value=st.session_state.get("wikipedia_aktif", True),
            key="studio_wiki_toggle",
        )
    with ust2:
        wiki_dil = st.radio(
            "Ansiklopedi Dili:",
            ["tr", "en"],
            format_func=lambda x: "🇹🇷 Türkçe Vikipedi" if x == "tr" else "🇬🇧 İngilizce Wikipedia",
            horizontal=True,
        )

    hk1, hk2, hk3, hk4, hk5, hk6 = st.columns(6)
    hizli_konu = None
    if hk1.button("🤖 Yapay Zeka", use_container_width=True):
        hizli_konu = "Yapay zeka"
    if hk2.button("🚁 İHA / Drone", use_container_width=True):
        hizli_konu = "İnsansız hava aracı"
    if hk3.button("⚛️ Kuantum", use_container_width=True):
        hizli_konu = "Kuantum mekaniği"
    if hk4.button("🪐 Kara Delik", use_container_width=True):
        hizli_konu = "Kara delik"
    if hk5.button("🏰 Osmanlı", use_container_width=True):
        hizli_konu = "Osmanlı İmparatorluğu"
    if hk6.button("🐍 Python", use_container_width=True):
        hizli_konu = "Python"

    col_w1, col_w2 = st.columns([2.2, 1.0])
    with col_w1:
        aranan_konu = st.text_input(
            "Wikipedia'da Araştırmak İstediğin Konu:",
            value=hizli_konu or st.session_state.get("son_wiki_konu", "Yapay zeka"),
            placeholder="Örn: El-Cezeri, Fatih Sultan Mehmet, Mars, DNA...",
        )
    with col_w2:
        detay_uzunlugu = st.selectbox(
            "Okuma Derinliği:",
            [1500, 3000, 5000],
            index=1,
            format_func=lambda x: "📄 Kısa Özet" if x == 1500 else ("📚 Detaylı Madde" if x == 3000 else "📖 Tam Makale"),
        )

    wb1, wb2 = st.columns(2)
    btn_wiki_ara = wb1.button("🔍 Araştır ve Wikipedia'dan Getir", use_container_width=True)
    btn_wiki_ses = wb2.button("🔊 Bul ve Sesli Dinle", use_container_width=True)

    if btn_wiki_ara or btn_wiki_ses or hizli_konu:
        secilen_konu = hizli_konu or aranan_konu
        st.session_state["son_wiki_konu"] = secilen_konu
        with st.spinner(f"🔍 Araştırılıyor, Wikipedia'ya gidiliyor ('{secilen_konu}')..."):
            sonuc = wikipedia_madde_getir(secilen_konu, dil=wiki_dil, detay_karakter=detay_uzunlugu)
        st.session_state["son_wiki_sonuc"] = sonuc
        if btn_wiki_ses and sonuc.get("basarili"):
            sesli_soyle_fn(f"{sonuc['baslik']}. {sonuc['ozet'][:650]}", dil="tr" if wiki_dil == "tr" else "en")

    aktif_wiki = st.session_state.get("son_wiki_sonuc")
    if aktif_wiki is None:
        aktif_wiki = wikipedia_madde_getir("Yapay zeka", dil="tr", detay_karakter=2400)
        st.session_state["son_wiki_sonuc"] = aktif_wiki

    if aktif_wiki.get("basarili"):
        if aktif_wiki.get("gorsel"):
            col_img, col_txt = st.columns([1.0, 2.4], gap="large")
            with col_img:
                st.image(aktif_wiki["gorsel"], caption=aktif_wiki["baslik"], use_container_width=True)
                st.link_button("🔗 Wikipedia'da Aç", aktif_wiki["url"], use_container_width=True)
            with col_txt:
                st.markdown(
                    bilgi_karti_olustur(
                        f"🌐 {aktif_wiki['baslik']}",
                        f"Kaynak: {aktif_wiki.get('dil', 'Wikipedia')}",
                        aktif_wiki["ozet"].replace("\n", "<br>"),
                    ),
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                bilgi_karti_olustur(
                    f"🌐 {aktif_wiki['baslik']}",
                    f"Kaynak: {aktif_wiki.get('dil', 'Wikipedia')}",
                    aktif_wiki["ozet"].replace("\n", "<br>"),
                ),
                unsafe_allow_html=True,
            )
            st.link_button("🔗 Orijinal Wikipedia Sayfasını Aç", aktif_wiki["url"])

        if aktif_wiki.get("diger_oneriler"):
            st.info("**🔎 İlgili Diğer Wikipedia Maddeleri:** " + " • ".join(aktif_wiki["diger_oneriler"]))
    else:
        st.warning(aktif_wiki.get("hata", "Madde bulunamadı."))
