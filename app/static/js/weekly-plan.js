/**
 * YKS Rehberlik Yönetim Sistemi - Haftalık Plan
 * 
 * Bu dosya, haftalık ders planı takvimini yönetir.
 * FullCalendar API'si kullanılarak daha güvenilir sürükle-bırak işlemleri sağlanır.
 * 
 * @version 2.0
 * @author Replit Team
 */

// Hata düzeltme - console hata işlemleri
if (typeof console.error !== 'function') {
    console.error = console.log;
}

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function() {
    // Toast bildirimleri için yapılandırma
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "newestOnTop": true,
        "progressBar": true,
        "positionClass": "toast-bottom-right",
        "preventDuplicates": false,
        "onclick": null,
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "3000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    };

    // Modal nesneleri
    const eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
    const autoPlanModal = new bootstrap.Modal(document.getElementById('autoPlanModal'));

    // Renk paletini global değişkenden al ya da varsayılan değerleri kullan
    const colors = typeof COLOR_PALETTE !== 'undefined' ? COLOR_PALETTE : [
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

    // Takvim animasyon süreleri (milisaniye)
    const ANIMATION_DURATION = 300;
    
    // Akıllı yerleştirme için sabitleri
    const SNAP_TO_INTERVAL = 15; // 15 dakikalık aralıklara yuvarla
    const DEFAULT_DURATION = 30;  // Dakika olarak varsayılan ders süresi (30 dakika)
    
    // Sürükleme animasyonları için değişkenler
    let lastHighlightedCell = null;
    let dropTargetVisualizer = null;

    // FullCalendar için tüm DOM hazır olmalı 
    // ve takvim alanı kesin olmalı
    const calendarEl = document.getElementById('calendar');
    
    // Sürükle-bırak hedef göstergesi oluştur
    function createDropTargetVisualizer() {
        // Zaten varsa yeniden oluşturma
        if (dropTargetVisualizer) return;
        
        // Gösterge elementini oluştur
        dropTargetVisualizer = document.createElement('div');
        dropTargetVisualizer.className = 'drop-target-visualizer';
        dropTargetVisualizer.style.cssText = `
            position: absolute;
            background-color: rgba(76, 175, 80, 0.3);
            border: 2px dashed #4caf50;
            border-radius: 3px;
            z-index: 9;
            pointer-events: none;
            display: none;
            transition: all ${ANIMATION_DURATION}ms ease;
        `;
        
        document.body.appendChild(dropTargetVisualizer);
    }
    
    // Göstergeyi güncelle ve göster
    function updateDropVisualizer(cellElement, dersAd) {
        if (!dropTargetVisualizer) createDropTargetVisualizer();
        
        // Hedef hücrenin pozisyonunu ve boyutunu al
        const rect = cellElement.getBoundingClientRect();
        const calendarRect = calendarEl.getBoundingClientRect();
        
        // Süreyi hesapla (varsayılan 30 dk = 1 birim yükseklik)
        const cellHeight = rect.height;
        const targetHeight = cellHeight; // 30 dakikalık tek bir slot
        
        // Pozisyonu ve boyutu ayarla
        dropTargetVisualizer.style.display = 'block';
        dropTargetVisualizer.style.left = `${rect.left}px`;
        dropTargetVisualizer.style.top = `${rect.top}px`;
        dropTargetVisualizer.style.width = `${rect.width}px`;
        dropTargetVisualizer.style.height = `${targetHeight}px`;
        
        // İçerik ekle
        dropTargetVisualizer.innerHTML = `
            <div style="padding: 5px; font-size: 12px; color: #4caf50; font-weight: bold;">
                ${dersAd}
            </div>
        `;
    }
    
    // Göstergeyi gizle
    function hideDropVisualizer() {
        if (dropTargetVisualizer) {
            dropTargetVisualizer.style.display = 'none';
        }
    }
    
    // Takvim oluşturulduktan sonra, takvim alanını droppable yap
    $(calendarEl).droppable({
        accept: '.ders-item',
        tolerance: 'pointer',
        over: function(event, ui) {
            // Daha akıcı deneyim için sürükleme animasyonunu etkinleştir
            const dersAd = ui.draggable.attr('data-ders-ad');
            trackDraggedItem(event.pageX, event.pageY, dersAd);
        },
        out: function(event, ui) {
            // Takvim üzerinden çıkınca vurgulamayı kaldır
            $('.fc-highlight-cell').removeClass('fc-highlight-cell');
            hideDropVisualizer();
            lastHighlightedCell = null;
        },
        drop: function(event, ui) {
            // Vurgulamayı kaldır
            $('.fc-highlight-cell').removeClass('fc-highlight-cell');
            hideDropVisualizer();
            
            const dersId = ui.draggable.attr('data-ders-id');
            const dersAd = ui.draggable.attr('data-ders-ad');
            
            // Takvim içindeki hedef hücreyi tam olarak tespit et
            const dropX = event.pageX;
            const dropY = event.pageY;
            const cell = findTargetTimeGridCell(dropX, dropY);
            
            if (!cell) {
                console.error('Hedef hücre bulunamadı');
                toastr.error('Ders eklenecek hücre bulunamadı!');
                return;
            }
            
            // Onay için hedef hücreyi vurgula ve log bilgisi göster
            console.log('Bırakma noktası:', {
                x: dropX,
                y: dropY,
                cell: cell
            });
            
            // Hücreyi manuel olarak vurgula
            if (cell.element) {
                $(cell.element).addClass('fc-highlight-cell');
                setTimeout(() => {
                    $(cell.element).removeClass('fc-highlight-cell');
                }, 800);
            }
            
            // Gün ve saat bilgilerini al
            const targetDay = parseInt(cell.day); // String'i number'a çevir
            const targetHour = cell.hour;
            const targetMinute = cell.minute;
            
            // Dakikayı belirlenen aralıklara yuvarla (30 dk)
            const roundedMinute = Math.round(targetMinute / SNAP_TO_INTERVAL) * SNAP_TO_INTERVAL;
            
            // Bitiş saati (varsayılan süre sonra)
            let endHour = targetHour;
            let endMinute = roundedMinute + DEFAULT_DURATION;
            
            if (endMinute >= 60) {
                endHour += Math.floor(endMinute / 60);
                endMinute = endMinute % 60;
            }
            
            // Saatleri formatlı hale getir
            const startTime = `${targetHour.toString().padStart(2, '0')}:${roundedMinute.toString().padStart(2, '0')}`;
            const endTime = `${endHour.toString().padStart(2, '0')}:${endMinute.toString().padStart(2, '0')}`;
            
            console.log('Eklenecek ders:', {
                ders_id: dersId,
                ders_ad: dersAd,
                gun: targetDay,
                start: startTime,
                end: endTime
            });
            
            // Başarılı animasyon ekle
            addDropSuccessAnimation(dropX, dropY);
            
            // Veriyi hazırla
            const data = {
                action: 'add',
                ders_id: dersId,
                gun: targetDay,
                start: startTime,
                end: endTime
            };
            
            // API isteği gönder
            updateCalendarEvent(data, `${dersAd} dersi eklendi`);
        }
    });
    
    // Sürüklenen dersi fare hareketine göre takip eden fonksiyon
    function trackDraggedItem(x, y, dersAd) {
        // Önce tüm vurgulamaları kaldır (önceki hücrelerden)
        $('.fc-highlight-cell').removeClass('fc-highlight-cell');
        
        // Takvim içindeki hedef hücreyi bul (geliştirilmiş hassas algılama)
        const cell = findTargetTimeGridCell(x, y);
        
        if (cell && cell.element) {
            // Aynı hücre üzerinde kalıyorsak tekrar işlem yapma (performans için)
            if (lastHighlightedCell === cell.element) return;
            
            // Yeni hücreyi vurgula (kırmızı kenarlıkla)
            $(cell.element).addClass('fc-highlight-cell');
            
            // Bırakma göstergesini güncelle
            updateDropVisualizer(cell.element, dersAd);
            
            // Son vurgulanan hücreyi güncelle
            lastHighlightedCell = cell.element;
            
            // Kullanıcıya daha iyi bir geri bildirim için hafif bir yanıp sönme animasyonu
            $(cell.element).css('opacity', '0.85').animate({opacity: '1'}, 150);
            
            // Hedef konum bilgisini göster
            console.log(`Hedeflenen: ${cell.day}. gün - ${cell.hour}:${cell.minute}`);
        } else {
            // Geçerli bir hücre yoksa vurgulamaları kaldır
            hideDropVisualizer();
            lastHighlightedCell = null;
        }
    }
    
    // Başarılı ekleme animasyonu
    function addDropSuccessAnimation(x, y) {
        // Animasyon elementi oluştur
        const successElement = document.createElement('div');
        successElement.className = 'drop-success-animation';
        successElement.innerHTML = '<i class="fas fa-check-circle"></i>';
        successElement.style.cssText = `
            position: absolute;
            left: ${x - 15}px;
            top: ${y - 15}px;
            color: #4CAF50;
            font-size: 30px;
            pointer-events: none;
            z-index: 9999;
            opacity: 0;
            transform: scale(0.5);
            animation: successPop 1s ease forwards;
        `;
        
        // Animasyon stilini ekle (eğer henüz eklenmemişse)
        if (!document.getElementById('success-animation-style')) {
            const style = document.createElement('style');
            style.id = 'success-animation-style';
            style.innerHTML = `
                @keyframes successPop {
                    0% { opacity: 0; transform: scale(0.5); }
                    30% { opacity: 1; transform: scale(1.2); }
                    70% { opacity: 1; transform: scale(1); }
                    100% { opacity: 0; transform: scale(1.5) translateY(-20px); }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Elementi ekle ve annimasyon bitince kaldır
        document.body.appendChild(successElement);
        setTimeout(() => {
            successElement.remove();
        }, 1000);
    }
    
    // Takvim hücrelerini vurgulamak için fonksiyon
    function highlightTargetCell(x, y) {
        $('.fc-highlight-cell').removeClass('fc-highlight-cell');
        
        // Takvim içindeki hedef hücreyi bul
        const cell = findTargetTimeGridCell(x, y);
        
        if (cell && cell.element) {
            $(cell.element).addClass('fc-highlight-cell');
        }
    }
    
    // Fare konumuna göre takvim hücresini bulan fonksiyon - geliştirilmiş hücre tespiti
    function findTargetTimeGridCell(x, y) {
        // Takvimin koordinatlarını al
        const calendarRect = calendarEl.getBoundingClientRect();
        
        // Takvim içinde değilse null döndür
        if (x < calendarRect.left || x > calendarRect.right || 
            y < calendarRect.top || y > calendarRect.bottom) {
            return null;
        }
        
        // Tüm gün sütunlarını bul
        const dayColumns = $('.fc-timegrid-col');
        let targetDay = null;
        let targetDayEl = null;

        // Önce tam olarak hangi X konumunda olduğumuzu belirle (yakınlığa göre)
        const dayWidths = [];
        const dayLefts = [];
        
        dayColumns.each(function(index) {
            const colRect = this.getBoundingClientRect();
            dayWidths[index] = colRect.width;
            dayLefts[index] = colRect.left;
        });
        
        // Hangi günün sütununda olduğumuzu tam olarak belirle
        // Yarım hücre genişliğine kadar mesafede en yakın gün hücresini bul
        let closestDayIndex = -1;
        let minDistance = Infinity;
        
        for (let i = 0; i < dayColumns.length; i++) {
            // Günün merkez X pozisyonu
            const dayCenterX = dayLefts[i] + (dayWidths[i] / 2);
            const distance = Math.abs(x - dayCenterX);
            
            if (distance < minDistance) {
                minDistance = distance;
                closestDayIndex = i;
                targetDayEl = dayColumns[i];
            }
        }
        
        targetDay = closestDayIndex;
        
        if (targetDay === null || targetDay < 0) return null;
        
        // Hedef günün zaman hücrelerini bul
        const timeSlots = $(targetDayEl).find('.fc-timegrid-slot-lane');
        let targetHour = 8; // Varsayılan
        let targetMinute = 0;
        let targetElement = null;
        
        // Tam olarak hangi zaman diliminin üzerinde olduğumuzu belirle
        let closestTimeSlotIndex = -1;
        minDistance = Infinity;
        
        timeSlots.each(function(index) {
            const slotRect = this.getBoundingClientRect();
            // Slot'un merkez Y konumu
            const slotCenterY = slotRect.top + (slotRect.height / 2);
            const distance = Math.abs(y - slotCenterY);
            
            if (distance < minDistance) {
                minDistance = distance;
                closestTimeSlotIndex = index;
                
                // Zaman etiketi formatı: "08:00"
                const timeLabel = $(this).attr('data-time');
                if (timeLabel) {
                    const [hour, minute] = timeLabel.split(':').map(Number);
                    targetHour = hour;
                    targetMinute = minute;
                    targetElement = this;
                }
            }
        });
        
        // Kullanıcıya görsel geri bildirim eklemek için daha belirgin bir vurgulama
        if (targetElement) {
            // Hücreyi belirginleştirmek için taşma efekti ekle
            $(targetElement).addClass('fc-highlight-cell');
            // Sonraki işlemler için hücreyi hatırla
            lastHighlightedCell = targetElement;
        }
        
        console.log('Hedeflenen hücre:', {
            day: targetDay,
            hour: targetHour,
            minute: targetMinute,
            element: targetElement
        });
        
        // Daha iyi debug için
        const result = {
            day: targetDay,  // Number olarak döndür, stringe çevirme
            hour: targetHour,
            minute: targetMinute,
            element: targetElement
        };
        return result;
    }
    
    // Takvim oluştur
    const calendar = new FullCalendar.Calendar(calendarEl, {
        headerToolbar: false, // Başlık çubuğunu kaldır
        initialView: 'timeGridWeek',
        slotMinTime: '08:00:00',
        slotMaxTime: '23:00:00',
        slotDuration: '00:30:00',
        slotLabelInterval: '01:00:00',
        allDaySlot: false,
        weekends: true,
        height: 'auto',
        locale: 'tr',
        timeZone: 'local',
        nowIndicator: false, // Şu anki saat göstergesini kaldır
        dayHeaderFormat: { weekday: 'long' }, // Sadece gün adlarını göster (Pazartesi, Salı, vb.)
        businessHours: {
            daysOfWeek: [0, 1, 2, 3, 4, 5, 6], // 0=Pazartesi, 6=Pazar
            startTime: '09:00',
            endTime: '21:00',
        },
        // Aynı saat dilimine birden fazla ders eklemeye izin verme (çakışmayı engelle)
        eventOverlap: false,
        
        // Temel fonksiyonlar
        selectable: true,
        select: handleDateSelect,
        editable: true,
        eventStartEditable: true,
        eventResizableFromStart: false,
        eventDurationEditable: true,
        droppable: true, // Dışarıdan öğelerin bırakılabilmesi
        
        // Etkinlik yönetimi
        eventClick: handleEventClick,
        eventDrop: handleEventDrop,
        eventResize: handleEventResize,
        
        // Sürükle-bırak destekleri
        drop: handleExternalDrop,
        eventReceive: function(info) {
            console.log('Event received:', info);
        },
        
        // Evenlerin yüklendiği kaynak
        events: API_ENDPOINT
    });

    // Takvimi render et
    calendar.render();

    // Ders elemanlarını sürüklenebilir yap
    makeDraggable();
    
    // Butonları ayarla
    setupButtons();
    
    /**
     * Tarih aralığı seçildiğinde çalışacak fonksiyon
     */
    function handleDateSelect(info) {
        clearEventForm();
        
        // Gün/saat bilgilerini al
        const start = info.start;
        const day = start.getDay() - 1; // 0=Pazartesi, -1=Pazar
        const adjustedDay = day === -1 ? 6 : day;
        
        // Form değerlerini doldur
        document.getElementById('event-gun').value = adjustedDay;
        document.getElementById('event-start').value = start.toTimeString().substring(0, 5);
        
        // Bitiş zamanını hesapla (30 dk sonra)
        const end = new Date(start.getTime() + 30 * 60000);
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
     * Etkinlik taşındığında çalışacak fonksiyon - geliştirilmiş kullanıcı deneyimi
     */
    function handleEventDrop(info) {
        const event = info.event;
        
        // Orijinal ve yeni zaman bilgileri
        const oldStart = info.oldEvent.start;
        const oldEnd = info.oldEvent.end;
        const newStart = event.start;
        const newEnd = event.end;
        
        // Akıllı zaman formatlaması
        const startTime = newStart.toTimeString().substring(0, 5);
        
        // Yeni bitiş zamanı
        const endTime = newEnd ? newEnd.toTimeString().substring(0, 5) : '';
        
        // Yeni gün indeksi
        const newDayIdx = newStart.getDay() - 1;
        const adjustedDay = newDayIdx === -1 ? 6 : newDayIdx;
        
        // Veriyi hazırla
        const data = {
            action: 'update',
            id: event.id.replace('ders_', ''),
            gun: adjustedDay,
            start: startTime,
            end: endTime
        };
        
        // Animasyon ve görsel geri bildirim
        const eventEl = info.el;
        
        // Başarılı animasyon
        $(eventEl).css({
            'transition': 'box-shadow 0.3s ease',
            'box-shadow': '0 0 10px 3px rgba(76, 175, 80, 0.5)'
        });
        
        // 0.5 saniye sonra normal haline getir
        setTimeout(() => {
            $(eventEl).css({
                'transition': 'box-shadow 0.3s ease',
                'box-shadow': 'none'
            });
        }, 500);
        
        // Eğer mobil cihazda ise hafif titreşim (başarılı feedback)
        if ('vibrate' in navigator) {
            try {
                navigator.vibrate([15, 30, 15]);
            } catch (e) {
                // Titreşim desteklenmiyor veya izin yok
            }
        }
        
        // API isteği gönder
        updateCalendarEvent(data, 'Ders programı güncellendi');
    }
    
    /**
     * Etkinlik yeniden boyutlandırıldığında çalışacak fonksiyon
     */
    function handleEventResize(info) {
        const event = info.event;
        
        // Orijinal ve yeni boyut bilgileri
        const oldEnd = info.oldEvent.end;
        const newEnd = event.end;
        
        // Süre değişimleri için limit uygulaması (minimum 30 dakika, maksimum 120 dakika)
        const eventDuration = (newEnd - event.start) / (1000 * 60); // dakika olarak
        
        // Yeni bitiş zamanı
        const endTime = newEnd.toTimeString().substring(0, 5);
        
        // Veriyi hazırla
        const data = {
            action: 'update',
            id: event.id.replace('ders_', ''),
            gun: event.extendedProps.gun,
            start: event.extendedProps.baslangic_saat,
            end: endTime
        };
        
        // Basit kullanıcı geribildirimi
        let resizeMessage = `Ders süresi: ${Math.round(eventDuration)} dakika`;
        
        // Boyutlandırma animasyonu
        const eventEl = info.el;
        
        // Yeni boyuta göre arka plan rengini ayarla
        if (eventDuration < 30) {
            $(eventEl).addClass('short-duration-alert');
            setTimeout(() => $(eventEl).removeClass('short-duration-alert'), 1000);
            resizeMessage = 'Ders süresi çok kısa';
        } else if (eventDuration > 120) {
            $(eventEl).addClass('long-duration-alert');
            setTimeout(() => $(eventEl).removeClass('long-duration-alert'), 1000);
            resizeMessage = 'Ders süresi çok uzun';
        } else {
            // Başarılı boyutlandırma vurgusu
            $(eventEl).css({
                'transition': 'box-shadow 0.3s ease',
                'box-shadow': '0 0 8px 2px rgba(76, 175, 80, 0.5)'
            });
            
            // Bir süre sonra normal haline getir
            setTimeout(() => {
                $(eventEl).css({
                    'transition': 'box-shadow 0.3s ease',
                    'box-shadow': 'none'
                });
            }, 800);
        }
        
        // Süre bilgisi etiketini göster
        toastr.info(resizeMessage);
        
        // API isteği gönder
        updateCalendarEvent(data, 'Ders süresi güncellendi');
    }
    
    /**
     * Dışarıdan öğe bırakıldığında çalışacak fonksiyon
     */
    function handleExternalDrop(info) {
        // Log debugging
        console.log('Drop event:', info);
        
        // Sürüklenen elemanın bilgilerini al
        const draggedEl = info.draggedEl;
        const dersId = draggedEl.getAttribute('data-ders-id');
        const dersAd = draggedEl.getAttribute('data-ders-ad');
        
        if (!dersId) {
            toastr.error('Ders bilgisi alınamadı!');
            console.error('Ders ID alınamadı', draggedEl);
            return;
        }
        
        // Tam olarak bırakılan konum bilgisi için mouse koordinatlarını kullan
        const dropPosition = {
            x: info.jsEvent.pageX,
            y: info.jsEvent.pageY
        };
        
        // Takvim içindeki hedef hücreyi hassas şekilde bul
        const cell = findTargetTimeGridCell(dropPosition.x, dropPosition.y);
        
        if (!cell) {
            console.error('Hedef hücre bulunamadı');
            toastr.error('Ders eklenecek hücre bulunamadı!');
            return;
        }
        
        // Hücre bulunduğunda işlemi onaylamak için görsel geri bildirim
        if (cell.element) {
            $(cell.element).addClass('fc-highlight-cell');
            setTimeout(() => {
                $(cell.element).removeClass('fc-highlight-cell');
            }, 800);
        }
        
        // Gün ve saat bilgilerini al
        const targetDay = cell.day;
        const targetHour = cell.hour;
        const targetMinute = cell.minute;
        
        // Dakikayı belirlenen aralıklara yuvarla (15dk)
        const roundedMinute = Math.round(targetMinute / SNAP_TO_INTERVAL) * SNAP_TO_INTERVAL;
        
        // Bitiş saati (varsayılan süre sonra)
        let endHour = targetHour;
        let endMinute = roundedMinute + DEFAULT_DURATION;
        
        if (endMinute >= 60) {
            endHour += Math.floor(endMinute / 60);
            endMinute = endMinute % 60;
        }
        
        // Saatleri formatlı hale getir
        const startTime = `${targetHour.toString().padStart(2, '0')}:${roundedMinute.toString().padStart(2, '0')}`;
        const endTime = `${endHour.toString().padStart(2, '0')}:${endMinute.toString().padStart(2, '0')}`;
        
        console.log('Ekleniyor:', {
            ders_id: dersId,
            gun: targetDay,
            start: startTime,
            end: endTime
        });
        
        // Başarılı animasyon ekle
        addDropSuccessAnimation(dropPosition.x, dropPosition.y);
        
        // Veriyi hazırla
        const data = {
            action: 'add',
            ders_id: dersId,
            gun: targetDay,
            start: startTime,
            end: endTime
        };
        
        // API isteği gönder
        updateCalendarEvent(data, `${dersAd} dersi eklendi`);
    }
    
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
     * Fare sürükleme hareketi için olay dinleyicisi
     * Takvim üzerindeki hedef hücreyi dinamik olarak vurgular ve göstergeyi günceller
     */
    document.addEventListener('mousemove', function(e) {
        if ($('.ui-draggable-dragging').length > 0) {
            // Bir öğe sürükleniyor, gerçek zamanlı takip et
            const draggedEl = $('.ui-draggable-dragging')[0];
            if (draggedEl) {
                const dersAd = $(draggedEl).attr('data-ders-ad');
                // Takvim üzerindeki hedef hücreyi takip et ve visualizer'ı güncelle
                trackDraggedItem(e.pageX, e.pageY, dersAd || 'Ders');
            }
        }
    });
            
    /**
     * Ders öğelerini sürüklenebilir yapan fonksiyon - geliştirilmiş kullanıcı deneyimi
     */
    function makeDraggable() {
        const dersItems = document.querySelectorAll('.ders-item');
        
        dersItems.forEach(function(item) {
            // Görsel olarak işaretle
            item.style.cursor = 'grab';
            
            // Dokunmatik ekranlarda etkileşim için
            item.style.touchAction = 'none';
            
            // Tooltip ekle
            item.setAttribute('title', 'Derse tıklayın veya takvime sürükleyin');
            
            // Hover efekti
            item.addEventListener('mouseenter', function() {
                this.classList.add('ders-item-hover');
            });
            item.addEventListener('mouseleave', function() {
                this.classList.remove('ders-item-hover');
            });
            
            // jQuery UI ile sürüklenebilir yap - geliştirilmiş kullanıcı deneyimi
            $(item).draggable({
                helper: function() {
                    // Özel yardımcı element - daha görsel bir sürükleme deneyimi
                    const helper = $(item).clone().addClass('ders-drag-helper');
                    helper.css({
                        'width': '100px',
                        'height': 'auto',
                        'padding': '6px 10px',
                        'box-shadow': '0 5px 15px rgba(0,0,0,0.3)',
                        'border-radius': '4px',
                        'font-weight': 'bold',
                        'display': 'flex',
                        'align-items': 'center',
                        'justify-content': 'center',
                        'white-space': 'nowrap',
                        'transform': 'rotate(-2deg)'
                    });
                    return helper;
                },
                appendTo: 'body',
                revert: function(isValid) {
                    if (!isValid) {
                        // Geçersiz bir alana bırakıldıysa animasyonlu geri dönüş
                        $(this).effect('shake', { direction: 'left', times: 2, distance: 5 }, 300);
                        return true;
                    }
                    return false;
                },
                connectToSortable: false,
                cursor: 'grabbing',
                cursorAt: { top: 15, left: 50 }, // Geliştirilmiş konumlandırma
                scroll: true,
                scrollSpeed: 15,
                zIndex: 10000,
                opacity: 0.9,
                distance: 5, // Sürükleme başlamadan önce hareket edilmesi gereken piksel sayısı
                delay: 100, // Sürükleme başlamadan önce küçük bir gecikme (ms) - tıklama işlemiyle çakışmayı önler
                start: function(event, ui) {
                    // Sürükleme başladığında orijinal öğeyi soluklaştır
                    $(item).css('opacity', '0.5');
                    $(item).addClass('ders-item-dragging');
                    
                    // Sürükleme yardımcısına animasyon ekle
                    ui.helper.css('transition', 'transform 0.1s ease');
                    
                    // Sürükleme başladığında hafif bir titreşim efekti ekle
                    if ('vibrate' in navigator) {
                        try {
                            navigator.vibrate(10);
                        } catch (e) {
                            // Titreşim desteklenmiyor veya izin yok - sorun değil
                        }
                    }
                },
                stop: function(event, ui) {
                    // Orijinal öğeyi normale döndür
                    $(item).css('opacity', '1');
                    $(item).removeClass('ders-item-dragging');
                    
                    // Göstergeyi temizle
                    hideDropVisualizer();
                    lastHighlightedCell = null;
                }
            });
            
            // Tıklama işleviyle ekleme
            item.addEventListener('click', function() {
                const dersId = this.getAttribute('data-ders-id');
                const dersAd = this.getAttribute('data-ders-ad');
                
                clearEventForm();
                
                // Formu doldur
                document.getElementById('event-ders').value = dersId;
                
                // Bugünün günü (0=Pazartesi, 6=Pazar)
                const today = new Date().getDay() - 1;
                document.getElementById('event-gun').value = today === -1 ? 6 : today;
                
                // Varsayılan başlangıç saati (şu an)
                const now = new Date();
                const hour = now.getHours();
                const minute = Math.floor(now.getMinutes() / 15) * 15;
                
                document.getElementById('event-start').value = 
                    `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
                
                // Varsayılan bitiş saati (30 dk sonra)
                let endHour = hour;
                let endMinute = minute + 30;
                
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
    
    /**
     * Butonları ayarlayan fonksiyon
     */
    function setupButtons() {
        // Kaydet butonu
        document.getElementById('save-event').addEventListener('click', function() {
            const eventId = document.getElementById('event-id').value;
            const dersId = document.getElementById('event-ders').value;
            const gun = document.getElementById('event-gun').value;
            const start = document.getElementById('event-start').value;
            const end = document.getElementById('event-end').value;
            
            // Form doğrulama
            if (!dersId || !gun || !start || !end) {
                toastr.error('Lütfen tüm alanları doldurun');
                return;
            }
            
            // Zaman kontrolü
            if (start >= end) {
                toastr.error('Başlangıç saati bitiş saatinden önce olmalıdır');
                return;
            }
            
            // Yeni veya güncelleme
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
        
        // Otomatik plan oluşturma
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
});