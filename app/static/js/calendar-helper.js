/**
 * YKS Rehberlik Yönetim Sistemi - Takvim Yardımcı Fonksiyonları
 * Bu dosya, takvim işlevleri için yardımcı fonksiyonlar içerir
 */

class CalendarHelper {
    constructor(options = {}) {
        this.options = options;
        this.colorMap = [
            '#6200ea', // Mor
            '#e91e63', // Pembe 
            '#2e7d32', // Yeşil
            '#8e24aa', // Koyu Mor
            '#37474f', // Gri
            '#c2185b', // Koyu Pembe
            '#f57c00', // Turuncu
            '#00897b', // Turkuaz
            '#1565c0', // Mavi
            '#512da8'  // Koyu Mor
        ];
    }

    /**
     * Takvim etkinliği öğelerini hazırla
     * @param {Array} dersProgramlari - API'den gelen ders programları 
     * @returns {Array} Takvim etkinlikleri
     */
    prepareEvents(dersProgramlari) {
        const events = [];
        
        dersProgramlari.forEach(program => {
            // Ders renk indeksini belirle
            const renkIndex = program.renk_index || 0;
            
            // Olayı daha güvenli bir şekilde oluştur
            const event = {
                id: program.id,
                title: program.title || 'Ders',
                start: program.start,
                end: program.end,
                className: 'calendar-event', // CSS için sınıf adını ekle
                extendedProps: {
                    ders_id: program.ders_id,
                    gun: program.gun,
                    baslangic_saat: program.baslangic_saat, 
                    bitis_saat: program.bitis_saat,
                    sure: program.sure_dakika,
                    renk_index: renkIndex // Renk indeksi bilgisini taşı
                }
            };
            
            // Renkleri güvenli bir şekilde ekle
            try {
                // Renk kodunu güvenli bir değişkene ata
                const colorCode = this.getColorForIndex(renkIndex);
                if (colorCode) {
                    event.backgroundColor = colorCode;
                    event.borderColor = colorCode;
                    event.textColor = '#ffffff';
                }
            } catch (e) {
                console.warn('Renk atama hatası:', e);
                // Hata durumunda varsayılan bir renk ata
                event.backgroundColor = '#6200ea';
                event.borderColor = '#6200ea';
                event.textColor = '#ffffff';
            }
            
            events.push(event);
        });
        
        return events;
    }
    
    /**
     * Renk indeksine göre renk kodu döndürür
     * @param {number} index - Renk indeksi
     * @returns {string} Renk kodu
     */
    getColorForIndex(index) {
        return this.colorMap[index % this.colorMap.length];
    }
    
    /**
     * Tarih/saat seçildiğinde çalışacak işlev
     * @param {object} selectInfo - Seçim bilgileri
     * @param {function} callback - Geri çağırma fonksiyonu
     */
    handleDateSelect(selectInfo, callback) {
        const startDate = new Date(selectInfo.start);
        const endDate = new Date(selectInfo.end);
        
        const data = {
            dayIndex: startDate.getDay() - 1, // 0: Pazartesi, -1: Pazar  
            adjustedDay: startDate.getDay() - 1 === -1 ? 6 : startDate.getDay() - 1,
            startTime: startDate.toTimeString().slice(0, 5),
            endTime: endDate.toTimeString().slice(0, 5),
            startDate: startDate,
            endDate: endDate
        };
        
        if (callback && typeof callback === 'function') {
            callback(data);
        }
    }
    
    /**
     * Etkinliğe tıklandığında çalışacak işlev  
     * @param {object} eventInfo - Etkinlik bilgileri
     * @param {function} callback - Geri çağırma fonksiyonu
     */
    handleEventClick(eventInfo, callback) {
        const event = eventInfo.event;
        
        const data = {
            id: event.id.replace('ders_', ''),
            title: event.title,
            ders_id: event.extendedProps.ders_id,
            gun: event.extendedProps.gun,
            baslangic_saat: event.extendedProps.baslangic_saat,
            bitis_saat: event.extendedProps.bitis_saat
        };
        
        if (callback && typeof callback === 'function') {
            callback(data);
        }
    }
    
    /**
     * Etkinlik taşındığında çalışacak işlev
     * @param {object} dropInfo - Taşıma bilgileri
     * @param {function} callback - Geri çağırma fonksiyonu 
     */
    handleEventDrop(dropInfo, callback) {
        const event = dropInfo.event;
        const startTime = event.start.toTimeString().slice(0, 5);
        const endTime = event.end.toTimeString().slice(0, 5);
        
        // Günü belirle
        let newDay = event.start.getDay() - 1; // 0: Pazartesi, -1: Pazar
        if (newDay === -1) newDay = 6; // Pazar için 6 yap
        
        const data = {
            id: event.id.replace('ders_', ''),
            gun: newDay,
            start: startTime,
            end: endTime,
            action: 'update'
        };
        
        if (callback && typeof callback === 'function') {
            callback(data);
        }
    }
    
    /**
     * Etkinlik yeniden boyutlandırıldığında çalışacak işlev 
     * @param {object} resizeInfo - Boyutlandırma bilgileri
     * @param {function} callback - Geri çağırma fonksiyonu
     */
    handleEventResize(resizeInfo, callback) {
        const event = resizeInfo.event;
        const startTime = event.start.toTimeString().slice(0, 5);
        const endTime = event.end.toTimeString().slice(0, 5);
        
        const data = {
            id: event.id.replace('ders_', ''),
            gun: event.extendedProps.gun,
            start: startTime,
            end: endTime,
            action: 'update'
        };
        
        if (callback && typeof callback === 'function') {
            callback(data);
        }
    }
}

// Eğer modül sistemi kullanılıyorsa export et
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CalendarHelper;
}