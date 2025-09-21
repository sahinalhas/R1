/**
 * YKS Rehberlik Yönetim Sistemi - Haftalık Plan
 * Basitleştirilmiş ve optimize edilmiş takvim uygulaması.
 * 
 * Bu dosya FullCalendar'ı kullanarak basit, etkin ve güvenilir sürükle-bırak
 * işlemlerini destekleyen haftalık ders planı takvimini yönetir.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Toast bildirim ayarları
    toastr.options = {
        closeButton: true,
        progressBar: true,
        positionClass: "toast-bottom-right",
        timeOut: 3000
    };
    
    // Modal nesneleri
    const eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
    const autoPlanModal = new bootstrap.Modal(document.getElementById('autoPlanModal'));
    
    // API endpoint - global değişkenden al
    // URL'den kaç numaralı öğrenci olduğunu tespit et
    const path = window.location.pathname;
    const match = path.match(/\/calisma-programi\/ogrenci\/(\d+)\/haftalik-plan/);
    const ogrenciId = match ? match[1] : (window.location.href.match(/\/calisma-programi\/ogrenci\/(\d+)\//) || [])[1];
    
    // API endpoint'i düzgün oluştur
    const API_ENDPOINT = ogrenciId 
        ? `/calisma-programi/${ogrenciId}/api/haftalik-plan` 
        : (window.API_ENDPOINT || '/calisma-programi/api/haftalik-plan');
    
    console.log('Kullanılan API endpoint:', API_ENDPOINT);
    
    // Renk paleti
    const COLOR_PALETTE = window.COLOR_PALETTE || [
        '#6200ea', '#e91e63', '#2e7d32', '#8e24aa', '#37474f', 
        '#c2185b', '#f57c00', '#00897b', '#1565c0', '#512da8'
    ];
    
    // Ders süresi sabitleri - İsteğe göre 60 dakika olarak ayarlandı
    const DEFAULT_DURATION = 60; // dakika (önceki: 30 dakika)
    
    // Takvim DOM elementi
    const calendarEl = document.getElementById('calendar');
    
    /**
     * Form değerlerini temizleyen yardımcı fonksiyon
     */
    function clearEventForm() {
        document.getElementById('event-id').value = '';
        document.getElementById('event-ders').value = '';
        document.getElementById('event-gun').value = '';
        document.getElementById('event-start').value = '';
        document.getElementById('event-end').value = '';
    }
    
    /**
     * Tarih aralığı seçildiğinde çalışacak fonksiyon
     */
    function handleDateSelect(info) {
        clearEventForm();
        
        // Gün ve saat bilgilerini al
        const start = info.start;
        const day = start.getDay() - 1; // 0=Pazartesi, -1=Pazar
        const adjustedDay = day === -1 ? 6 : day;
        
        // Form değerlerini doldur
        document.getElementById('event-gun').value = adjustedDay;
        document.getElementById('event-start').value = start.toTimeString().substring(0, 5);
        
        // Bitiş zamanını hesapla (30 dk sonra)
        const end = new Date(start.getTime() + DEFAULT_DURATION * 60000);
        document.getElementById('event-end').value = end.toTimeString().substring(0, 5);
        
        // Silme butonunu gizle
        document.getElementById('delete-event').style.display = 'none';
        
        // Modalı göster
        eventModal.show();
        
        // Seçimi temizle
        calendar.unselect();
    }
    
    /**
     * Etkinliğe tıklandığında çalışacak fonksiyon
     */
    function handleEventClick(info) {
        clearEventForm();
        
        // Etkinlik bilgilerini al
        const event = info.event;
        
        // Form değerlerini doldur
        document.getElementById('event-id').value = event.id.replace('ders_', '');
        document.getElementById('event-ders').value = event.extendedProps.ders_id;
        document.getElementById('event-gun').value = event.extendedProps.gun;
        document.getElementById('event-start').value = event.extendedProps.baslangic_saat;
        document.getElementById('event-end').value = event.extendedProps.bitis_saat;
        
        // Silme butonunu göster
        document.getElementById('delete-event').style.display = 'block';
        
        // Modalı göster
        eventModal.show();
    }
    
    /**
     * Takvimde bulunan derslerin toplam süresini hesaplayıp gösteren fonksiyon
     */
    function updateTotalLessonDuration() {
        const events = calendar.getEvents();
        let totalMinutes = 0;
        
        // Her ders için ayrı süre toplamlarını tutacak nesne
        let dersSureleri = {};
        let dersAdlari = {};
        let dersRenkleri = {};
        
        events.forEach(event => {
            const start = event.start;
            const end = event.end;
            const dersId = event.extendedProps.ders_id;
            const dersAdi = event.title;
            const renk = event.backgroundColor;
            
            if (start && end && dersId) {
                // İki tarih arasındaki dakika farkını hesapla
                const diffMs = end - start;
                const diffMinutes = Math.round(diffMs / 60000); // ms -> dakika
                totalMinutes += diffMinutes;
                
                // Bu ders için süreyi ekle
                if (!dersSureleri[dersId]) {
                    dersSureleri[dersId] = 0;
                    dersAdlari[dersId] = dersAdi;
                    dersRenkleri[dersId] = renk;
                }
                dersSureleri[dersId] += diffMinutes;
            }
        });
        
        // Toplam süreyi formatlayıp göstergeyi güncelle
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;
        
        // Genel toplam süreyi güncelle
        const durationText = `Toplam: ${hours} saat ${minutes > 0 ? minutes + ' dk' : ''}`;
        document.getElementById('toplam-ders-suresi').textContent = durationText;
        
        // Ders sürelerini doğrudan ilgili ders kartlarının altında göster
        // Ders ID'lerini dizi yapıp sırala
        const dersIds = Object.keys(dersSureleri);
        
        // Her ders için süre bilgisini ilgili ders kartının altına ekle
        dersIds.forEach(dersId => {
            const dakika = dersSureleri[dersId];
            // Ders kartı altındaki süre bilgisi elementi
            const dersSureElement = document.getElementById('ders-sure-' + dersId);
            
            if (!dersSureElement) return; // Element bulunamazsa atla
            
            // Süre yoksa temizle
            if (dakika === 0) {
                dersSureElement.textContent = '';
                return;
            }
            
            // Süre bilgisini formatla
            const saat = Math.floor(dakika / 60);
            const kalanDakika = dakika % 60;
            
            const sureMetni = `${saat} saat ${kalanDakika > 0 ? kalanDakika + ' dk' : ''}`;
            
            // Metin olarak göster
            dersSureElement.textContent = sureMetni;
        });
    }
    
    /**
     * API'ye istek gönderen fonksiyon
     */
    function updateCalendarEvent(data, successMessage) {
        fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('İşlem başarısız oldu');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                toastr.success(successMessage);
                calendar.refetchEvents(); // Takvimi yenile
                // Toplam süreyi güncelle
                setTimeout(updateTotalLessonDuration, 300); // Events yüklendikten sonra çağır
            } else {
                toastr.error(data.message || 'Bir hata oluştu');
            }
        })
        .catch(error => {
            console.error('Hata:', error);
            toastr.error('İşlem sırasında bir hata oluştu');
        });
    }
    
    /**
     * Başarılı animasyon ekleyen fonksiyon
     */
    function showSuccessIndicator(element) {
        // Başarılı efekti uygula
        $(element).addClass('operation-success');
        
        // Belirli bir süre sonra efekti kaldır
        setTimeout(() => {
            $(element).removeClass('operation-success');
        }, 800);
    }
    
    /**
     * Takvimi oluştur - FullCalendar v5.11.3
     */
    const calendar = new FullCalendar.Calendar(calendarEl, {
        // Temel Yapılandırma
        headerToolbar: false, // Başlık çubuğunu kaldır
        initialView: 'timeGridWeek', // Haftalık zaman ızgarası görünümü
        slotMinTime: '08:00:00', // Gün başlangıç saati
        slotMaxTime: '23:00:00', // Gün bitiş saati
        slotDuration: '00:30:00', // Her zaman dilimi 30 dakika
        slotLabelInterval: '01:00:00', // Saat etiketleri 1 saat aralıklarla
        allDaySlot: false, // Tüm gün etkinlikleri için alan gösterme
        weekends: true, // Hafta sonlarını göster
        height: 'auto', // Otomatik yükseklik
        locale: 'tr', // Türkçe dil desteği
        timeZone: 'local', // Yerel zaman dilimi
        nowIndicator: false, // Şu anki zaman göstergesi kapalı
        
        // Başlık formatı - sadece gün adlarını göster (tarihleri değil)
        dayHeaderFormat: { weekday: 'long' }, // Pazartesi, Salı, vb.
        
        // Çalışma saatleri vurgulaması
        businessHours: {
            daysOfWeek: [0, 1, 2, 3, 4, 5, 6], // 0=Pazartesi, 6=Pazar
            startTime: '09:00',
            endTime: '21:00',
        },
        
        // Aynı zamanda birden fazla ders olamaz (çakışma engellendi)
        eventOverlap: false,
        
        // Etkinlik içerik özelleştirme (bu color hatası için eklendi)
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
                console.warn('FullCalendar eventContent render hatası:', error);
                return { html: '<div>Ders</div>' };
            }
        },
        
        // Kullanıcı etkileşimi özellikleri
        selectable: true, // Tarih/saat seçimine izin ver
        select: handleDateSelect, // Seçim işleyici
        
        // Sürükleme özellikleri
        editable: true, // Etkinlikler sürükle-bırak ile düzenlenebilir
        eventStartEditable: true, // Etkinlik başlangıç zamanı düzenlenebilir
        eventResizableFromStart: false, // Başlangıçtan yeniden boyutlandırma kapalı
        eventDurationEditable: true, // Etkinlik süresi düzenlenebilir
        
        // Dışarıdan öğelerin takvime bırakılabilmesi
        droppable: true,
        
        // Etkinlik işleyicileri
        eventClick: handleEventClick, // Etkinliğe tıklama
        
        // Etkinlik taşıma ve boyutlandırma
        eventDrop: function(info) {
            // Yeni tarih bilgilerini al
            const event = info.event;
            
            // Yeni gün indeksi
            const newStart = event.start;
            const newEnd = event.end;
            const newDayIdx = newStart.getDay() - 1;
            const adjustedDay = newDayIdx === -1 ? 6 : newDayIdx;
            
            // Zaman bilgilerini formatla
            const startTime = newStart.toTimeString().substring(0, 5);
            const endTime = newEnd ? newEnd.toTimeString().substring(0, 5) : '';
            
            // Veriyi hazırla
            const data = {
                action: 'update',
                id: event.id.replace('ders_', ''),
                gun: adjustedDay,
                start: startTime,
                end: endTime
            };
            
            // Başarılı görseli göster
            showSuccessIndicator(info.el);
            
            // API isteği gönder
            updateCalendarEvent(data, 'Ders programı güncellendi');
        },
        
        eventResize: function(info) {
            // Yeni süre bilgilerini al
            const event = info.event;
            const newEnd = event.end;
            const endTime = newEnd.toTimeString().substring(0, 5);
            
            // Veriyi hazırla
            const data = {
                action: 'update',
                id: event.id.replace('ders_', ''),
                gun: event.extendedProps.gun,
                start: event.extendedProps.baslangic_saat,
                end: endTime
            };
            
            // Başarılı görseli göster
            showSuccessIndicator(info.el);
            
            // API isteği gönder
            updateCalendarEvent(data, 'Ders süresi güncellendi');
        },
        
        // Dışarıdan bırakma işlemi
        drop: function(info) {
            // Bırakılan elemanın bilgilerini al
            const dersId = info.draggedEl.getAttribute('data-ders-id');
            const dersAd = info.draggedEl.getAttribute('data-ders-ad');
            
            if (!dersId) {
                toastr.error('Ders bilgisi alınamadı!');
                return;
            }
            
            const date = info.date;
            
            // Gün indeksi (FullCalendar'da 0=Pazar, 1=Pazartesi)
            // Backend'de 0=Pazartesi, 6=Pazar formatına dönüştür
            // (date.getDay() - 1) kullanıp, Pazar = -1 olduğunda 6'ya çevir
            let dayIdx = date.getDay() - 1;
            if (dayIdx === -1) dayIdx = 6;
            
            // Saat bilgisi
            const hour = date.getHours();
            const minute = date.getMinutes();
            
            // 30 dakikalık aralıklara yuvarla
            const roundedMinute = Math.round(minute / 30) * 30;
            
            // Bitiş saati (30 dakika sonra)
            let endHour = hour;
            let endMinute = roundedMinute + DEFAULT_DURATION;
            
            if (endMinute >= 60) {
                endHour += Math.floor(endMinute / 60);
                endMinute = endMinute % 60;
            }
            
            // Saatleri formatlı hale getir
            const startTime = `${hour.toString().padStart(2, '0')}:${roundedMinute.toString().padStart(2, '0')}`;
            const endTime = `${endHour.toString().padStart(2, '0')}:${endMinute.toString().padStart(2, '0')}`;
            
            // Veriyi hazırla
            const data = {
                action: 'add',
                ders_id: dersId,
                gun: dayIdx,
                start: startTime,
                end: endTime
            };
            
            console.log('Ders ekleniyor:', data);
            
            // API'ye gönder
            updateCalendarEvent(data, `${dersAd} dersi eklendi`);
        },
        
        // FullCalendar'ın kendiliğinden oluşturduğu etkinliği hemen kaldır
        // Biz API'den gelen verilerle her şeyi yeniden yükleyeceğiz
        eventReceive: function(info) {
            info.event.remove();
        },
        
        // Etkinlik kaynağı
        events: API_ENDPOINT
    });
    
    // Takvimi render et
    calendar.render();
    
    // Etkinlikler yüklendiğinde toplam süreyi güncelle
    calendar.on('eventsSet', function() {
        updateTotalLessonDuration();
    });
    
    // Dışarıdan sürüklenebilir öğeleri yapılandır
    function setupDraggableItems() {
        // FullCalendar'ın dışarıdan sürükleme özelliğini kullan
        const draggableItems = document.querySelectorAll('.ders-item');
        
        draggableItems.forEach(function(item) {
            // FullCalendar'ın yalın sürükleme API'si ile yapılandır
            new FullCalendar.Draggable(item, {
                itemSelector: '.ders-item',
                eventData: function(el) {
                    const dersId = el.getAttribute('data-ders-id');
                    const dersAd = el.getAttribute('data-ders-ad');
                    const colorIdx = parseInt(dersId) % COLOR_PALETTE.length;
                    
                    return {
                        title: dersAd,
                        duration: { minutes: DEFAULT_DURATION }, // 60 dakika süre
                        backgroundColor: COLOR_PALETTE[colorIdx],
                        borderColor: COLOR_PALETTE[colorIdx],
                        extendedProps: {
                            ders_id: dersId
                        }
                    };
                }
            });
            
            // Ayrıca click ile de ekleme yapılabilir
            item.addEventListener('click', function() {
                const dersId = this.getAttribute('data-ders-id');
                const dersAd = this.getAttribute('data-ders-ad');
                
                clearEventForm();
                
                // Form değerlerini doldur
                document.getElementById('event-ders').value = dersId;
                
                // Bugünün günü (0=Pazartesi, 6=Pazar)
                const today = new Date().getDay() - 1;
                document.getElementById('event-gun').value = today === -1 ? 6 : today;
                
                // Varsayılan başlangıç saati (şu an)
                const now = new Date();
                const hour = now.getHours();
                const minute = Math.floor(now.getMinutes() / 30) * 30;
                
                document.getElementById('event-start').value = 
                    `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
                
                // Varsayılan bitiş saati (30 dk sonra)
                let endHour = hour;
                let endMinute = minute + DEFAULT_DURATION;
                
                if (endMinute >= 60) {
                    endHour += 1;
                    endMinute -= 60;
                }
                
                document.getElementById('event-end').value = 
                    `${endHour.toString().padStart(2, '0')}:${endMinute.toString().padStart(2, '0')}`;
                
                // Silme butonunu gizle
                document.getElementById('delete-event').style.display = 'none';
                
                // Modalı göster
                eventModal.show();
            });
        });
    }
    
    // Butonları ve formları yapılandır
    function setupButtonsAndForms() {
        // Kaydet butonu
        document.getElementById('save-event').addEventListener('click', function() {
            const eventId = document.getElementById('event-id').value;
            const dersId = document.getElementById('event-ders').value;
            const gun = document.getElementById('event-gun').value;
            const start = document.getElementById('event-start').value;
            const end = document.getElementById('event-end').value;
            
            // Form doğrulama
            if (!dersId || gun === '' || !start || !end) {
                toastr.error('Lütfen tüm alanları doldurun');
                return;
            }
            
            // Zaman kontrolü
            if (start >= end) {
                toastr.error('Başlangıç saati bitiş saatinden önce olmalıdır');
                return;
            }
            
            // Ekleme veya güncelleme
            const data = eventId
                ? { action: 'update', id: eventId, gun, start, end }
                : { action: 'add', ders_id: dersId, gun, start, end };
            
            // API isteği gönder
            updateCalendarEvent(
                data, 
                eventId ? 'Ders programı güncellendi' : 'Yeni ders programı eklendi'
            );
            
            // Modalı kapat
            eventModal.hide();
        });
        
        // Sil butonu
        document.getElementById('delete-event').addEventListener('click', function() {
            const eventId = document.getElementById('event-id').value;
            
            if (!eventId) {
                toastr.error('Silinecek etkinlik bulunamadı');
                return;
            }
            
            // Onay iste
            document.getElementById('confirm-message').textContent = 
                'Bu ders programını silmek istediğinizden emin misiniz?';
            
            document.getElementById('confirm-action').onclick = function() {
                const data = {
                    action: 'delete',
                    id: eventId
                };
                
                updateCalendarEvent(data, 'Ders programı silindi');
                
                confirmModal.hide();
                eventModal.hide();
            };
            
            confirmModal.show();
        });
        
        // Temizle butonu
        document.getElementById('temizle-btn').addEventListener('click', function() {
            document.getElementById('confirm-message').textContent = 
                'Tüm ders programını temizlemek istediğinizden emin misiniz? Bu işlem geri alınamaz.';
            
            document.getElementById('confirm-action').onclick = function() {
                const data = {
                    action: 'clear'
                };
                
                updateCalendarEvent(data, 'Ders programı temizlendi');
                confirmModal.hide();
            };
            
            confirmModal.show();
        });
        
        // Otomatik plan
        document.getElementById('otomatik-plan-btn').addEventListener('click', function() {
            autoPlanModal.show();
        });
        
        document.getElementById('create-auto-plan').addEventListener('click', function() {
            // Seçili günleri topla
            const selectedDays = [];
            
            for (let i = 0; i < 7; i++) {
                if (document.getElementById(`gun-${i}`).checked) {
                    selectedDays.push(i);
                }
            }
            
            if (selectedDays.length === 0) {
                toastr.error('En az bir gün seçmelisiniz');
                return;
            }
            
            // Form verilerini al
            const baslangicSaat = document.getElementById('baslangic-saat').value;
            const bitisSaat = document.getElementById('bitis-saat').value;
            const dersSure = parseInt(document.getElementById('ders-sure').value);
            const molaSure = parseInt(document.getElementById('mola-sure').value);
            
            // Zaman kontrolü
            if (baslangicSaat >= bitisSaat) {
                toastr.error('Başlangıç saati bitiş saatinden önce olmalıdır');
                return;
            }
            
            // Veriyi hazırla
            const data = {
                action: 'auto_schedule',
                gunler: selectedDays,
                baslangic_saat: baslangicSaat,
                bitis_saat: bitisSaat,
                ders_suresi: dersSure,
                mola_suresi: molaSure
            };
            
            // API isteği gönder
            updateCalendarEvent(data, 'Otomatik plan oluşturuldu');
            
            // Modalı kapat
            autoPlanModal.hide();
        });
    }
    
    // Sürüklenebilir öğeleri yapılandır
    setupDraggableItems();
    
    // Butonları ve formları yapılandır
    setupButtonsAndForms();
});