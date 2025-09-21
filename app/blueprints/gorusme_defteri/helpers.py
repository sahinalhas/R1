"""
Görüşme defteri modülü için yardımcı işlevler
"""

def get_categories(meeting_topic: str, meeting_type: str = "") -> dict:
    """
    Görüşme konusuna göre kategorileri belirler
    
    Args:
        meeting_topic: Görüşme konusu
        meeting_type: Görüşme şekli (Yüzyüze, Telefon, vb.)
        
    Returns:
        Dict: Kategori bilgilerini içeren sözlük
    """
    categories = {
        "hizmet_turu": "",
        "calisma_kategorisi": "",
        "calisma_alani": "",
        "kisi_rolu": "Öğrenci",  # Varsayılan rol
        "calisma_yontemi": meeting_type  # Görüşme şekli
    }

    if not meeting_topic:
        return categories
        
    # Kişi rolü belirleme
    if meeting_topic.startswith(("DMV", "DMVG")):
        categories["kisi_rolu"] = "Veli"
    elif meeting_topic.startswith(("DMÖ", "DMÖG")):
        categories["kisi_rolu"] = "Öğretmen"

    # ÖOVE - Akademik Gelişim kategorisi
    if meeting_topic.startswith("ÖOVEb"):
        categories.update({
            "hizmet_turu": "Ö - Gelişimsel ve Önleyici Hizmetler",
            "calisma_kategorisi": "ÖOV - Bilgi Verme Çalışmaları",
            "calisma_alani": "ÖOVE - Akademik Gelişim"
        })
        
    # ÖOVM - Kariyer Gelişimi kategorisi    
    elif meeting_topic.startswith("ÖOVMb"):
        categories.update({
            "hizmet_turu": "Ö - Gelişimsel ve Önleyici Hizmetler",
            "calisma_kategorisi": "ÖOV - Bilgi Verme Çalışmaları", 
            "calisma_alani": "ÖOVM - Kariyer Gelişimi"
        })
        
    # ÖOVK - Sosyal Duygusal Gelişim kategorisi
    elif meeting_topic.startswith("ÖOVKb"):
        categories.update({
            "hizmet_turu": "Ö - Gelişimsel ve Önleyici Hizmetler",
            "calisma_kategorisi": "ÖOV - Bilgi Verme Çalışmaları",
            "calisma_alani": "ÖOVK - Sosyal Duygusal Gelişim"
        })
        
    # ÖOB - Bireyi Tanıma Çalışmaları kategorisi
    elif meeting_topic.startswith(("B.K", "ÖOB", "RAM")):
        categories.update({
            "hizmet_turu": "Ö - Gelişimsel ve Önleyici Hizmetler",
            "calisma_kategorisi": "ÖOB - Bireyi Tanıma Çalışmaları",
            "calisma_alani": meeting_topic
        })
        
    # ÖOY - Yöneltme Ve İzleme kategorisi
    elif meeting_topic.startswith("ÖOYb"):
        categories.update({
            "hizmet_turu": "Ö - Gelişimsel ve Önleyici Hizmetler",
            "calisma_kategorisi": "ÖOY - Yöneltme Ve İzleme",
            "calisma_alani": meeting_topic
        })
        
    # İB - Bireysel Psikolojik Danışma kategorisi
    elif meeting_topic.startswith("İB"):
        categories.update({
            "hizmet_turu": "İ - İyileştirici Hizmetler",
            "calisma_kategorisi": "İB - Bireysel Psikolojik Danışma",
            "calisma_alani": meeting_topic
        })
        
    # İPbB - Bildirim Yükümlülüğü kategorisi
    elif meeting_topic.startswith("İPbB"):
        categories.update({
            "hizmet_turu": "İ - İyileştirici Hizmetler",
            "calisma_kategorisi": "İP - Psikososyal Müdahale",
            "calisma_alani": "İPbB - Bildirim Yükümlülüğü"
        })
        
    # İPbİ - İntihar kategorisi
    elif meeting_topic.startswith("İPbİ"):
        categories.update({
            "hizmet_turu": "İ - İyileştirici Hizmetler",
            "calisma_kategorisi": "İP - Psikososyal Müdahale",
            "calisma_alani": "İPbİ - İntihar"
        })
        
    # İPbT - Koruyucu ve Destekleyici Tedbir kategorisi
    elif meeting_topic.startswith("İPbT"):
        categories.update({
            "hizmet_turu": "İ - İyileştirici Hizmetler",
            "calisma_kategorisi": "İP - Psikososyal Müdahale",
            "calisma_alani": "İPbT - Koruyucu ve Destekleyici Tedbir"
        })
        
    # İS - Sevk (Yönlendirme) kategorisi
    elif meeting_topic.startswith("İS"):
        categories.update({
            "hizmet_turu": "İ - İyileştirici Hizmetler",
            "calisma_kategorisi": "İS - Sevk (Yönlendirme)",
            "calisma_alani": meeting_topic
        })
        
    # DMÖG - Öğretmene Yönelik kategorisi
    elif meeting_topic.startswith("DMÖG"):
        categories.update({
            "hizmet_turu": "D - Destek Hizmetler",
            "calisma_kategorisi": "DM - Müşavirlik",
            "calisma_alani": "DMÖ - Öğretmene Yönelik"
        })
        
    # DMVG - Veliye Yönelik kategorisi
    elif meeting_topic.startswith("DMVG"):
        categories.update({
            "hizmet_turu": "D - Destek Hizmetler",
            "calisma_kategorisi": "DM - Müşavirlik",
            "calisma_alani": "DMV - Veliye Yönelik"
        })

    return categories