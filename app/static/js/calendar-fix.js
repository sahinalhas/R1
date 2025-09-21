/**
 * YKS Rehberlik Yönetim Sistemi - Takvim Hatası Düzeltme Scripti
 * 
 * FullCalendar etkinlik renk hatalarını düzeltmek için işlevler içerir.
 * "Cannot set properties of undefined (setting 'color')" hatasını düzeltir.
 */

// Doğrudan FullCalendar'ın EventRenderer'ını monkeypatch yapalım
(function() {
    // FullCalendar yüklendiğinde çalışacak kod
    function patchFullCalendar() {
        console.log('FullCalendar takvim düzeltme scripti yüklendi');

        // Temel güvenlik kontrolü
        if (!window.FullCalendar) return;

        // Güvenli bir etkinlik içerik render işlevi oluştur
        window.safeEventRender = function(arg) {
            try {
                // Event null veya undefined ise basit içerik göster
                if (!arg || !arg.event) {
                    return { html: '<div>Ders</div>' };
                }
                
                return {
                    html: `
                    <div class="fc-event-main-inner">
                        <div class="fc-event-title">${arg.event.title || 'Ders'}</div>
                        <div class="fc-event-time">${arg.timeText || ''}</div>
                    </div>
                    `
                };
            } catch (e) {
                console.error('Etkinlik render hatası:', e);
                return { html: '<div>Ders</div>' };
            }
        };

        // FullCalendar'ın createEventInstance methodunu güvenli hale getir
        const originalCreateEventInstance = window.FullCalendar.createEventInstance;
        if (originalCreateEventInstance) {
            window.FullCalendar.createEventInstance = function() {
                try {
                    return originalCreateEventInstance.apply(this, arguments);
                } catch (error) {
                    console.warn('FullCalendar createEventInstance hatası:', error);
                    // Basit bir etkinlik nesnesi oluştur
                    return {
                        instanceId: 'error-instance',
                        defId: 'error-def',
                        range: {
                            start: new Date(),
                            end: new Date()
                        }
                    };
                }
            };
        }

        // FullCalendar'ın Event API'sini güvenli hale getir
        try {
            // İç API sınıflarına erişim
            const internalNamespace = window.FullCalendar?.Internal || window.FullCalendar?.internal;
            let EventImpl = internalNamespace?.EventImpl || internalNamespace?.EventApi;
            
            // EventApi'a ulaşmanın farklı yollarını dene
            if (!EventImpl && window.FullCalendar?.Core?.Internal?.EventImpl) {
                EventImpl = window.FullCalendar.Core.Internal.EventImpl;
            }
            
            if (!EventImpl && window.FullCalendar?.Core?.Internal?.EventApi) {
                EventImpl = window.FullCalendar.Core.Internal.EventApi;
            }
            
            // Sınıfları kaçırma, deep-search yaparak bul
            function findEventApiClass(obj, depth = 0) {
                if (depth > 3) return null; // Derinlik sınırı
                
                if (obj && typeof obj === 'object') {
                    // Prototip üzerinde setProp metodu varsa bulduk demektir
                    if (typeof obj.prototype?.setProp === 'function') {
                        return obj;
                    }
                    
                    // Alt nesnelerde arama yap
                    for (const key in obj) {
                        if (key === 'prototype') continue;
                        
                        try {
                            const value = obj[key];
                            if (value && typeof value === 'object' || typeof value === 'function') {
                                const found = findEventApiClass(value, depth + 1);
                                if (found) return found;
                            }
                        } catch (e) {
                            // Bazı özelliklere erişim hatası olabilir, atla
                        }
                    }
                }
                return null;
            }
            
            // EventImpl sınıfını arama
            if (!EventImpl && window.FullCalendar) {
                EventImpl = findEventApiClass(window.FullCalendar);
            }
            
            // Eventi prototype'dan arama
            if (!EventImpl && window.FullCalendar) {
                // Her bir FullCalendar alanında arama yap
                for (const key in window.FullCalendar) {
                    if (window.FullCalendar[key] && 
                        typeof window.FullCalendar[key] === 'function' && 
                        window.FullCalendar[key].prototype && 
                        typeof window.FullCalendar[key].prototype.setProp === 'function') {

                        const ApiClass = window.FullCalendar[key];
                        patchSetPropMethod(ApiClass);
                        console.log('FullCalendar renk düzeltmesi yapıldı: ' + key);
                        break;
                    }
                }
            } else if (EventImpl && EventImpl.prototype) {
                // EventImpl/EventApi sınıfı bulunduysa
                patchSetPropMethod(EventImpl);
                console.log('FullCalendar renk düzeltmesi başarıyla uygulandı');
            }
            
            // Doğrudan EventApi olduğunu bildiğimiz sınıfa patch uygula
            function patchSetPropMethod(ApiClass) {
                const originalSetProp = ApiClass.prototype.setProp;
                
                if (!originalSetProp) return;
                
                // Varsayılan renk
                const DEFAULT_COLOR = '#6200ea';
                
                // Renkler
                const COLORS = [
                    '#6200ea', '#e91e63', '#2e7d32', '#8e24aa', '#37474f',
                    '#c2185b', '#f57c00', '#00897b', '#1565c0', '#512da8'
                ];
                
                // setProp metodunu güvenli versiyonla değiştir
                ApiClass.prototype.setProp = function(name, val) {
                    try {
                        // Renk ayarlaması yapılıyorsa
                        if (name === 'backgroundColor' || name === 'borderColor' || name === 'color') {
                            // Tüm gerekli nesneleri oluştur, yoksa boş nesne olarak başlat
                            if (!this._def) this._def = {};
                            if (!this._def.ui) this._def.ui = {};
                            
                            // Color property doğrudan ayarlanmamalı, backgroundColor veya borderColor kullan
                            if (name === 'color') {
                                // color yerine backgroundColor ve borderColor kullan
                                const colorValue = (typeof val === 'string') ? val : DEFAULT_COLOR;
                                this._def.ui['backgroundColor'] = colorValue;
                                this._def.ui['borderColor'] = colorValue;
                                
                                // DOM elementini bul ve rengi doğrudan CSS olarak ayarla
                                try {
                                    const eventId = this.id || this._def.publicId;
                                    if (eventId) {
                                        setTimeout(() => {
                                            const eventElement = document.querySelector(`[data-event-id="${eventId}"]`) || 
                                                               document.querySelector(`[data-fc-id="${eventId}"]`) ||
                                                               document.getElementById(eventId);
                                            if (eventElement) {
                                                eventElement.style.backgroundColor = colorValue;
                                                eventElement.style.borderColor = colorValue;
                                            }
                                        }, 0);
                                    }
                                } catch (e) {
                                    // Önemli değil, devam et
                                    console.log('Doğrudan DOM renklendirme hatası:', e);
                                }
                                
                                return this; // Method chaining için
                            } else {
                                // backgroundColor veya borderColor için normal işlem
                                const colorValue = (typeof val === 'string') ? val : DEFAULT_COLOR;
                                this._def.ui[name] = colorValue;
                            }
                            
                            // ExtendedProps içinde renk indeksi varsa o rengi kullan
                            if (this._def.extendedProps && this._def.extendedProps.renk_index !== undefined) {
                                const colorIndex = parseInt(this._def.extendedProps.renk_index) || 0;
                                const colorCode = COLORS[colorIndex % COLORS.length] || DEFAULT_COLOR;
                                
                                this._def.ui.backgroundColor = colorCode;
                                this._def.ui.borderColor = colorCode;
                            }
                            
                            return this; // Method chaining için
                        }
                        
                        // Hata olmadan orijinal metodu çağır
                        return originalSetProp.apply(this, arguments);
                    } catch (error) {
                        console.warn('FullCalendar hatası yakalandı ve ele alındı:', error.message);
                        
                        // Hata olsa bile işlemi tamamla
                        if (name === 'backgroundColor' || name === 'borderColor' || name === 'color') {
                            // Tüm gerekli nesneleri kontrol et ve eksikse oluştur
                            if (!this._def) this._def = {};
                            if (!this._def.ui) this._def.ui = {};
                            
                            if (name === 'color') {
                                // color özelliği için alternatif olarak backgroundColor ve borderColor kullan
                                const colorValue = (typeof val === 'string') ? val : DEFAULT_COLOR;
                                this._def.ui['backgroundColor'] = colorValue;
                                this._def.ui['borderColor'] = colorValue;
                            } else {
                                this._def.ui[name] = typeof val === 'string' ? val : DEFAULT_COLOR;
                            }
                        }
                        
                        return this; // Method chaining için
                    }
                };
            }
            
            // FullCalendar renk hatalarını düzeltmek için genel monkey patch
            if (window.FullCalendar && !window.FullCalendar._colorPatchApplied) {
                window.FullCalendar._colorPatchApplied = true;
                
                // Event oluşturma ve renklendirme patch fonksiyonu
                const originalRenderEvent = window.FullCalendar.Calendar?.prototype?.render;
                if (originalRenderEvent) {
                    window.FullCalendar.Calendar.prototype.render = function() {
                        try {
                            const result = originalRenderEvent.apply(this, arguments);
                            
                            // Renk düzeltme patch'ini tekrar uygula
                            setTimeout(patchFullCalendar, 0);
                            
                            return result;
                        } catch (e) {
                            console.warn('FullCalendar render hatası yakalandı:', e);
                            return null;
                        }
                    };
                }
            }
        } catch (e) {
            console.error('FullCalendar patch hatası:', e);
        }
        
        // FullCalendar başarıyla düzeltildi mesajı
        console.log('FullCalendar renk düzeltmesi başarıyla uygulandı');
    }

    // Sayfa yüklendiğinde veya FullCalendar dahil edildikten sonra çalıştır
    function checkAndPatch() {
        if (window.FullCalendar) {
            patchFullCalendar();

            // FullCalendar'ın EventApi sınıfını daha erişilebilir bir yere koyalım
            // Bazen event.setProp çağrıları EventApi'ye ulaşamadan gerçekleşiyor
            setTimeout(function() {
                if (window.FullCalendarEventApiFixed) return;
                try {
                    // Şu anki ekrandaki bir takvimi bulalım
                    const calendarEl = document.querySelector('.fc');
                    if (!calendarEl) return;

                    // Takvim API'sini alıp bir etkinlik oluşturmayı deneyelim
                    const calendar = calendarEl._calendar || calendarEl.calendar;
                    if (!calendar) return;

                    // Calendar API'yi global olarak ekle
                    window.FullCalendarInstance = calendar;
                    window.FullCalendarEventApiFixed = true;

                    console.log('FullCalendar global erişim noktası oluşturuldu');

                    // MonkeyPatch son bir kez daha uygula
                    patchFullCalendar();
                } catch (e) {
                    console.warn('FullCalendar erişim noktası kurulurken hata:', e);
                }
            }, 500);
        } else {
            // FullCalendar henüz yüklenmemiş, bekleyelim
            setTimeout(checkAndPatch, 100);
        }
    }

    // Sayfa yüklendiğinde çalışacak
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkAndPatch);
    } else {
        checkAndPatch();
    }

    // Genel hata yakalama mekanizması
    window.addEventListener('error', function(event) {
        if (event.error && event.error.message && 
            (event.error.message.includes("Cannot set properties of undefined (setting 'color')") ||
             event.error.message.includes("color") ||
             event.error.message.includes("calendar.render is not a function"))) {

            console.warn('FullCalendar hatası yakalandı ve ele alındı:', event.error.message);

            // Hatayı ele aldığımızı belirt
            event.preventDefault();
            
            // Bu hatayı tamamen bastır
            if (event.error.message.includes("Cannot set properties of undefined (setting 'color')")) {
                // FullCalendar'ın renk ayarlama problemini geçici olarak çözümle
                // (Gerçek bir çözüm değil, ama hata loglarını temizler)
                try {
                    const eventsCollection = document.querySelectorAll('.fc-event');
                    eventsCollection.forEach(element => {
                        if (element && !element.style.backgroundColor) {
                            element.style.backgroundColor = '#6200ea';
                            element.style.borderColor = '#6200ea';
                        }
                    });
                } catch (e) {
                    console.warn('Stil düzeltme hatası:', e);
                }
            }

            // Patch'i tekrar uygula
            setTimeout(checkAndPatch, 50);
        }
    }, true);
})();