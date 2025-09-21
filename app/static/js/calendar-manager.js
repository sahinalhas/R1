/**
 * YKS Rehberlik Yönetim Sistemi - Takvim Yöneticisi
 * Bu dosya, takvim işlevlerini yönetmek için araçlar sağlar.
 */

class CalendarManager {
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
        this.defaultOptions = {
            locale: 'tr',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
            },
            buttonText: {
                today: 'Bugün',
                month: 'Ay',
                week: 'Hafta',
                day: 'Gün',
                list: 'Liste'
            },
            firstDay: 1, // Pazartesi
            allDaySlot: false,
            slotMinTime: '08:00:00',
            slotMaxTime: '24:00:00',
            slotDuration: '00:30:00',
            slotLabelFormat: {
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            },
            dayHeaderFormat: { weekday: 'long', day: 'numeric', month: 'long' },
            eventTimeFormat: {
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            },
            nowIndicator: true,
            height: 'auto'
        };
    }

    /**
     * Haftalık çalışma planı takvimini oluşturur
     * @param {string} elementId - Takvim container element ID'si
     * @param {string} apiUrl - Veri yüklemek için API URL'si
     * @param {object} customOptions - Özel yapılandırma seçenekleri
     * @returns {object} FullCalendar nesnesi
     */
    createWeeklyPlanCalendar(elementId, apiUrl, customOptions = {}) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.error(`Element with ID ${elementId} not found`);
            return null;
        }

        // Temel ayarları özel ayarlarla birleştir
        const calendarOptions = {
            ...this.defaultOptions,
            initialView: 'timeGridWeek',
            editable: true,
            droppable: true,
            selectable: true,
            selectMirror: true,
            eventResizableFromStart: false,
            eventDurationEditable: true,
            navLinks: true,
            eventOverlap: false, // Derslerin üst üste gelmesini engelle
            
            // API'den verileri al
            events: apiUrl,
            
            // Tarih/saat seçimi
            select: this._handleDateSelect.bind(this),
            
            // Etkinlik işlemleri
            eventClick: this._handleEventClick.bind(this),
            eventDrop: this._handleEventDrop.bind(this),
            eventResize: this._handleEventResize.bind(this),
            
            // Etkinlik içerik özelleştirme - hata oluşursa güvenli içerik göster
            eventContent: function(arg) {
                // Global güvenli render kullan
                if (window.safeEventRender) {
                    return window.safeEventRender(arg);
                }
                
                // Fallback: Bir şeyler yanlış giderse basit içerik oluştur
                try {
                    return {
                        html: `
                        <div class="fc-event-main-inner">
                            <div class="fc-event-title">${arg.event.title || 'Ders'}</div>
                            <div class="fc-event-time">${arg.timeText || ''}</div>
                        </div>
                        `
                    };
                } catch (error) {
                    console.warn('Takvim etkinlik içerik render hatası:', error);
                    return { html: '<div>Ders</div>' };
                }
            },
            
            // Dışarıdan öğe bırakma
            drop: this._handleExternalDrop.bind(this),
            
            ...customOptions
        };

        // Takvimi oluştur
        const calendar = new FullCalendar.Calendar(element, calendarOptions);
        calendar.render();
        
        return calendar;
    }

    /**
     * Tarih seçimi işlemi
     * @param {object} info - Seçim bilgileri
     * @private
     */
    _handleDateSelect(info) {
        if (this.options.onDateSelect && typeof this.options.onDateSelect === 'function') {
            // Tarih ve saat bilgilerini al
            const startDate = new Date(info.start);
            const endDate = new Date(info.end);
            
            // Haftanın gününü hesapla (0: Pazartesi, 6: Pazar)
            const dayIndex = startDate.getDay() - 1;
            const adjustedDay = dayIndex === -1 ? 6 : dayIndex;
            
            this.options.onDateSelect({
                startDate,
                endDate,
                dayIndex: adjustedDay,
                startTime: startDate.toTimeString().slice(0, 5),
                endTime: endDate.toTimeString().slice(0, 5)
            });
        }
    }

    /**
     * Etkinliğe tıklama işlemi
     * @param {object} info - Etkinlik bilgileri
     * @private
     */
    _handleEventClick(info) {
        if (this.options.onEventClick && typeof this.options.onEventClick === 'function') {
            const event = info.event;
            
            this.options.onEventClick({
                id: event.id.replace('ders_', ''),
                title: event.title,
                ders_id: event.extendedProps.ders_id,
                gun: event.extendedProps.gun,
                baslangic_saat: event.extendedProps.baslangic_saat,
                bitis_saat: event.extendedProps.bitis_saat
            });
        }
    }

    /**
     * Etkinlik sürükleme işlemi
     * @param {object} info - Etkinlik bilgileri
     * @private
     */
    _handleEventDrop(info) {
        if (this.options.onEventDrop && typeof this.options.onEventDrop === 'function') {
            const event = info.event;
            
            // Başlangıç ve bitiş zamanlarını al
            const startTime = event.start.toTimeString().slice(0, 5);
            const endTime = event.end ? event.end.toTimeString().slice(0, 5) : '';
            
            // Yeni günü hesapla
            let newDay = event.start.getDay() - 1; // 0: Pazartesi, -1: Pazar
            if (newDay === -1) newDay = 6; // Pazar için 6
            
            this.options.onEventDrop({
                id: event.id.replace('ders_', ''),
                ders_id: event.extendedProps.ders_id,
                gun: newDay,
                start: startTime,
                end: endTime,
                action: 'update'
            });
        }
    }

    /**
     * Etkinlik yeniden boyutlandırma işlemi
     * @param {object} info - Etkinlik bilgileri
     * @private
     */
    _handleEventResize(info) {
        if (this.options.onEventResize && typeof this.options.onEventResize === 'function') {
            const event = info.event;
            
            // Başlangıç ve bitiş zamanlarını al
            const startTime = event.start.toTimeString().slice(0, 5);
            const endTime = event.end ? event.end.toTimeString().slice(0, 5) : '';
            
            this.options.onEventResize({
                id: event.id.replace('ders_', ''),
                ders_id: event.extendedProps.ders_id,
                gun: event.extendedProps.gun,
                start: startTime,
                end: endTime,
                action: 'update'
            });
        }
    }

    /**
     * Dışarıdan öğe bırakma işlemi
     * @param {object} info - Bırakma bilgileri
     * @private
     */
    _handleExternalDrop(info) {
        if (this.options.onExternalDrop && typeof this.options.onExternalDrop === 'function') {
            // Bırakılan öğenin ID ve adını al
            const dersId = info.draggedEl.getAttribute('data-ders-id');
            const dersAdi = info.draggedEl.getAttribute('data-ders-ad');
            
            // Tarih bilgilerini al
            const date = info.date;
            const dayIndex = date.getDay() - 1; // 0: Pazartesi, -1: Pazar
            const adjustedDay = dayIndex === -1 ? 6 : dayIndex;
            
            // Saat bilgilerini al
            const hour = date.getHours();
            const minute = Math.floor(date.getMinutes() / 15) * 15;
            
            // 45 dakika sonrası için bitiş saati hesapla
            let endHour = hour;
            let endMinute = minute + 45;
            
            if (endMinute >= 60) {
                endHour += 1;
                endMinute -= 60;
            }
            
            // Saatleri formatla
            const startTime = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
            const endTime = `${endHour.toString().padStart(2, '0')}:${endMinute.toString().padStart(2, '0')}`;
            
            this.options.onExternalDrop({
                ders_id: dersId,
                ders_adi: dersAdi,
                gun: adjustedDay,
                start: startTime,
                end: endTime,
                action: 'add'
            });
        }
    }

    /**
     * Renk indeksine göre renk kodu döndürür
     * @param {number} index - Renk indeksi
     * @returns {string} Renk kodu
     */
    getColorForIndex(index) {
        return this.colorMap[index % this.colorMap.length];
    }
}

// Global erişim için window nesnesine ekle
window.CalendarManager = CalendarManager;