/**
 * YKS Çalışma Programı Takip Sistemi - Haftalık Plan JavaScript
 * FullCalendar benzeri modern tasarım ile geliştirilmiş
 * Görsel olarak daha çekici ve kullanıcı dostu arayüz
 */

// İleri düzey sürükle-bırak ve boyutlandırma özellikleri

/**
 * Modern takvimi sürükle-bırak ve boyutlandırma işlemleriyle yapılandır
 */
function setupModernCalendar() {
    // Takvim konteynerını seç
    const calendarContainer = document.querySelector('.calendar-container');
    if (!calendarContainer) {
        console.error("Modern takvim konteyneri bulunamadı!");
        return;
    }
    
    // Sayfa yüklendikten sonra veya yeniden yüklendiğinde
    // var olan ders bloklarına resize kolu ekle
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(() => {
            // Tüm ders bloklarına resize kolu ekle
            document.querySelectorAll('.lesson-block').forEach(block => {
                // Resize kolu yoksa ekle
                if (!block.querySelector('.resize-handle')) {
                    const resizeHandle = document.createElement('div');
                    resizeHandle.className = 'resize-handle';
                    block.appendChild(resizeHandle);
                }
                
                // Etkileşimleri tekrar ekle
                addLessonBlockInteractions(block);
            });
        }, 500);
    });
    
    // Hücrelerin tamamını seç
    const dayCells = document.querySelectorAll('.day-cell');
    const lessonBlocks = document.querySelectorAll('.lesson-block');
    
    // Ders kartlarını drag & drop için yapılandır
    const dersKartlari = document.querySelectorAll('.ders-karti');
    dersKartlari.forEach(kart => {
        kart.setAttribute('draggable', 'true');
        
        // Sürükleme başladığında
        kart.addEventListener('dragstart', function(e) {
            const dersId = this.getAttribute('data-ders-id');
            const dersAdi = this.getAttribute('data-ders-adi');
            const renkIndex = this.getAttribute('data-renk-index');
            
            e.dataTransfer.setData('text/plain', dersId);
            e.dataTransfer.setData('application/json', JSON.stringify({
                type: 'kart',
                dersId: dersId,
                dersAdi: dersAdi,
                renkIndex: renkIndex
            }));
            
            this.classList.add('dragging');
        });
        
        // Sürükleme bittiğinde
        kart.addEventListener('dragend', function() {
            this.classList.remove('dragging');
        });
        
        // Ders kartına tıklanınca seçim işlemi için
        kart.addEventListener('click', function() {
            dersKartlari.forEach(k => k.classList.remove('selected'));
            this.classList.add('selected');
            
            // Seçim modunu etkinleştir
            document.getElementById('dragDropInfo').textContent = 'Takvimde bir hücreye tıklayarak dersi ekleyin';
        });
    });
    
    // Takvim hücrelerinin drop işlemlerini yapılandır
    dayCells.forEach(cell => {
        // Sürüklenebilir alanları işaretle
        cell.setAttribute('droppable', 'true');
        
        // Sürüklenip bırakma olayları
        cell.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        cell.addEventListener('dragleave', function() {
            this.classList.remove('dragover');
        });
        
        cell.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            try {
                // Sürüklenen veriye eriş
                const dersId = e.dataTransfer.getData('text/plain');
                const jsonData = e.dataTransfer.getData('application/json');
                
                if (jsonData) {
                    const data = JSON.parse(jsonData);
                    
                    if (data.type === 'kart') {
                        const gun = parseInt(this.getAttribute('data-gun'));
                        const saat = parseInt(this.getAttribute('data-saat'));
                        
                        // Renk indeksini kullan
                        const renkIndex = data.renkIndex || (parseInt(dersId) % 10);
                        
                        // Ders bloğunu oluştur ve ekle - iki hücrelik (60 dakika) olarak
                        addLessonBlock(dersId, data.dersAdi, gun, saat, saat + 1, renkIndex);
                    } else if (data.type === 'move') {
                        // Mevcut ders bloğunu taşıma işlemi
                        const dersAdi = data.dersAdi;
                        const gun = parseInt(this.getAttribute('data-gun'));
                        const saat = parseInt(this.getAttribute('data-saat'));
                        const renkIndex = data.renkIndex;
                        const sureDakika = data.sureDakika;
                        const bitisSaat = saat + (sureDakika / 30);
                        
                        // Eski bloğu kaldır
                        document.getElementById(data.blockId).remove();
                        
                        // Yeni bloğu ekle
                        addLessonBlock(dersId, dersAdi, gun, saat, bitisSaat, renkIndex);
                    }
                }
            } catch (err) {
                console.error("Sürükle-bırak işleminde hata:", err);
            }
        });
        
        // Tıklama olayı
        cell.addEventListener('click', function() {
            const selectedKart = document.querySelector('.ders-karti.selected');
            if (selectedKart) {
                const dersId = selectedKart.getAttribute('data-ders-id');
                const dersAdi = selectedKart.getAttribute('data-ders-adi');
                const gun = parseInt(this.getAttribute('data-gun'));
                const saat = parseInt(this.getAttribute('data-saat'));
                
                // Renk indeksini belirle
                const renkIndex = selectedKart.getAttribute('data-renk-index') || parseInt(dersId) % 10;
                
                // Ders bloğunu oluştur ve ekle (iki hücre - 60 dakika)
                addLessonBlock(dersId, dersAdi, gun, saat, saat + 1, renkIndex);
                
                // Seçimi temizle
                selectedKart.classList.remove('selected');
            }
        });
    });
    
    // Var olan ders bloklarını yapılandır
    lessonBlocks.forEach(block => {
        addLessonBlockInteractions(block);
    });
    
    // Ders blokları için tıklama olaylarını ekle
    function addLessonBlockInteractions(block) {
        // Her blok için benzersiz bir ID oluştur
        if (!block.id) {
            block.id = 'lesson-block-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
        }
        
        // Blok sürükleme için yapılandırma
        block.setAttribute('draggable', 'true');
        
        // Resize koluna tıklama olayı
        const resizeHandle = block.querySelector('.resize-handle');
        if (resizeHandle) {
            let isResizing = false;
            let startY = 0;
            let originalHeight = 0;
            
            resizeHandle.addEventListener('mousedown', function(e) {
                console.log("Resize başladı");
                e.stopPropagation();
                e.preventDefault();
                isResizing = true;
                startY = e.clientY;
                originalHeight = block.offsetHeight;
                document.body.style.cursor = 'ns-resize';
                
                // Geçici bir class ekle
                block.classList.add('resizing');
                
                // Sürüklemeyi devre dışı bırak
                block.setAttribute('draggable', 'false');
            });
            
            document.addEventListener('mousemove', function(e) {
                if (!isResizing) return;
                
                console.log("Resize hareket ediyor");
                
                const diffY = e.clientY - startY;
                const newHeight = originalHeight + diffY;
                
                // Her 30px bir yarım saat
                const rowHeight = 30;
                const minHeight = rowHeight; // Min 30 dakika
                const maxHeight = rowHeight * 8; // Max 4 saat
                
                if (newHeight >= minHeight && newHeight <= maxHeight) {
                    // 30 dakikalık dilimlere yuvarlama
                    const numberOfSlots = Math.max(1, Math.round(newHeight / rowHeight));
                    const snappedHeight = (numberOfSlots * rowHeight) - 4; // 4px margin
                    
                    // Yüksekliği güncelle
                    block.style.height = snappedHeight + 'px';
                    
                    // Dakika süresini hesapla ve güncelle
                    const durationInMinutes = numberOfSlots * 30;
                    const durationElement = block.querySelector('.lesson-duration');
                    if (durationElement) {
                        durationElement.textContent = durationInMinutes + ' dk';
                    }
                    
                    // Başlangıç-bitiş saatlerini güncelle
                    const baslangicIndeks = parseInt(block.getAttribute('data-baslangic'));
                    const bitisIndeks = baslangicIndeks + numberOfSlots - 1; // Başlangıç dahil, ardışık zaman dilimi sayısı
                    
                    const baslangicSaat = formatTimeFromIndex(baslangicIndeks);
                    const bitisSaat = formatTimeFromIndex(bitisIndeks + 1); // Görsel: Son dilimin bir sonraki zaman dilimi bitiş
                    
                    // Bitiş zaman indeksini güncelle
                    block.setAttribute('data-bitis', bitisIndeks);
                    
                    // Zaman etiketini güncelle
                    const timeElement = block.querySelector('.lesson-time');
                    if (timeElement) {
                        timeElement.textContent = baslangicSaat + ' - ' + bitisSaat;
                    }
                }
            });
            
            document.addEventListener('mouseup', function() {
                if (isResizing) {
                    console.log("Resize bitti");
                    isResizing = false;
                    document.body.style.cursor = 'default';
                    
                    // Geçici class'ı kaldır
                    block.classList.remove('resizing');
                    
                    // Sürüklemeyi yeniden etkinleştir
                    block.setAttribute('draggable', 'true');
                    
                    // Form verilerini güncelle
                    updateFormData();
                }
            });
        }
        
        // Sürükleme başladığında
        block.addEventListener('dragstart', function(e) {
            // Eğer şu anda yeniden boyutlandırma yapılıyorsa, sürüklemeyi iptal et
            if (block.classList.contains('resizing')) {
                e.preventDefault();
                return;
            }
            
            e.stopPropagation();
            
            // Sürüklerken saydamlık ekle
            this.style.opacity = '0.5';
            
            // Sürükleme verilerini ayarla
            const dersId = this.getAttribute('data-ders-id');
            const dersAdi = this.querySelector('.lesson-title').textContent;
            const renkIndex = parseInt(this.getAttribute('data-ders-id')) % 10;
            const sureDakika = parseInt(this.querySelector('.lesson-duration').textContent);
            
            e.dataTransfer.setData('application/json', JSON.stringify({
                type: 'move',
                blockId: this.id,
                dersId: dersId,
                dersAdi: dersAdi,
                renkIndex: renkIndex,
                sureDakika: sureDakika
            }));
        });
        
        // Sürükleme bittiğinde
        block.addEventListener('dragend', function(e) {
            this.style.opacity = '1';
        });
        
        // Blok tıklama - silmek için
        block.addEventListener('click', function(e) {
            // Eğer tıklanan element resize handle ise, silme işlemini yapma
            if (e.target.classList.contains('resize-handle')) {
                e.stopPropagation();
                return;
            }
            
            e.stopPropagation();
            
            if (confirm('Bu ders bloğunu kaldırmak istiyor musunuz?')) {
                block.remove();
                
                // Form verilerini güncelle
                updateFormData();
            }
        });
    }
    
    // Yeni ders bloğu ekleyen fonksiyon
    function addLessonBlock(dersId, dersAdi, gun, baslangicSaat, bitisSaat, renkIndex) {
        // Takvim içeriğini seç
        const calendarBody = document.querySelector('.calendar-body');
        if (!calendarBody) return;
        
        // Her ders bloğu en az 30 dakikalık (1 yarım saat) olsun
        const baslangicDilim = baslangicSaat;
        // Bitiş dilimi baslangıç ile aynı ise (30 dakika), görsel olarak bitişi 1 artır
        const bitisDilim = (bitisSaat == baslangicSaat) ? (baslangicSaat + 1) : bitisSaat;
        
        // Baslangıç ve bitiş zamanlarını hesapla
        const baslangicZamani = formatTimeFromIndex(baslangicDilim);
        const bitisZamani = formatTimeFromIndex(bitisDilim);
        
        // Süreyi hesapla (dakika cinsinden)
        const sureDakika = (bitisDilim - baslangicDilim) * 30;
        
        // Blok yüksekliğini hesapla - her yarım saat 30px
        const yukseklik = (bitisDilim - baslangicDilim) * 30 - 4; // -4 için kenar boşluğu
        
        // Yeni bloğu oluştur
        const block = document.createElement('div');
        block.className = `lesson-block ders-renk-${renkIndex}`;
        block.style.top = `${baslangicSaat * 30}px`;
        block.style.left = `calc(60px + (${gun} * (100% - 60px) / 7))`;
        block.style.height = `${yukseklik}px`;
        block.style.width = `calc((100% - 60px) / 7 - 4px)`;
        block.style.zIndex = '50';
        block.setAttribute('data-ders-id', dersId);
        block.setAttribute('data-gun', gun);
        block.setAttribute('data-baslangic', baslangicSaat);
        block.setAttribute('data-bitis', bitisSaat - 1);
        
        block.innerHTML = `
            <div class="lesson-title">${dersAdi}</div>
            <div class="lesson-time">${baslangicZamani} - ${bitisZamani}</div>
            <div class="lesson-duration">${sureDakika} dk</div>
            <div class="resize-handle"></div>
        `;
        
        // Bloku takvime ekle
        calendarBody.appendChild(block);
        
        // Etkileşimleri ekle
        addLessonBlockInteractions(block);
        
        // Form alanlarını güncelle
        updateFormData();
    }
    
    // Form verilerini güncelleyen yardımcı fonksiyon
    function updateFormData() {
        console.log("Form verilerini güncelleme başladı");
        
        // Önce tüm gizli form alanlarını temizle
        for (let gun = 0; gun < 7; gun++) {
            for (let saat = 0; saat < 35; saat++) { // 8:00 - 24:00 arası maksimum 35 yarım saat (güvenli olsun)
                const input = document.getElementById(`ders_${gun}_${saat}`);
                if (input) {
                    input.value = '';
                }
            }
        }
        
        // Mevcut ders bloklarına göre form alanlarını doldur
        const lessonBlocks = document.querySelectorAll('.lesson-block');
        console.log(`${lessonBlocks.length} ders bloğu bulundu`);
        
        lessonBlocks.forEach((block, index) => {
            const dersId = block.getAttribute('data-ders-id');
            const gun = parseInt(block.getAttribute('data-gun'));
            const baslangic = parseInt(block.getAttribute('data-baslangic'));
            const bitis = parseInt(block.getAttribute('data-bitis'));
            
            console.log(`Blok ${index+1}: Ders ID=${dersId}, Gün=${gun}, Başlangıç=${baslangic}, Bitiş=${bitis}`);
            
            // Resize kolu kontrolü - her bloğun resize kolu olduğundan emin ol
            if (!block.querySelector('.resize-handle')) {
                const resizeHandle = document.createElement('div');
                resizeHandle.className = 'resize-handle';
                block.appendChild(resizeHandle);
                
                // Yeni resize kolu eklendiğinde etkileşimleri yenile
                addLessonBlockInteractions(block);
            }
            
            // Bu aralıktaki tüm yarım saatler için form alanlarını doldur
            for (let saat = baslangic; saat <= bitis; saat++) {
                const inputId = `ders_${gun}_${saat}`;
                const input = document.getElementById(inputId);
                if (input) {
                    input.value = dersId;
                    console.log(`Input ${inputId} değeri ${dersId} olarak güncellendi`);
                } else {
                    console.warn(`Input ${inputId} bulunamadı`);
                    // Eğer input element bulunamadıysa, dinamik olarak oluştur
                    const newInput = document.createElement('input');
                    newInput.type = 'hidden';
                    newInput.id = inputId;
                    newInput.name = inputId;
                    newInput.value = dersId;
                    document.getElementById('scheduleForm').appendChild(newInput);
                    console.log(`Input ${inputId} oluşturuldu ve değeri ${dersId} olarak ayarlandı`);
                }
            }
        });
        
        console.log("Form verilerini güncelleme tamamlandı");
    }
}

/**
 * Haftalık plan takvimini başlat
 * Ders bloklarını sürükleyip bırakma, seçim yapma ve
 * boyutlandırma özellikleri
 */
function initScheduleTable() {
    // Şimdilik eski tablo etkinleştirme kodu burada tutulacak
    const scheduleTable = document.getElementById('scheduleTable');
    if (!scheduleTable) {
        console.log("Eski tablo düzeni bulunamadı veya gizli. Modern takvim kullanılıyor.");
    } else {
        // Hücrelerin görünümünü ayarla
        const cells = document.querySelectorAll('.schedule-cell');
        cells.forEach(cell => {
            cell.style.width = '100px';
            cell.style.height = '50px';
            cell.style.border = '1px solid #e0e0e0';
            cell.style.backgroundColor = '#ffffff';
            cell.style.position = 'relative'; // Ders bloklarının doğru konumlanması için
            // Hücre bırakılabilir (droppable) özelliği ekle
            cell.setAttribute('droppable', 'true');
        });
    }
    
    // Modern takvimi yapılandır
    setupModernCalendar();
    
    // Drag & Drop işlemleri için değişkenler
    let dragStartCell = null;
    let dragEndCell = null;
    let isDragging = false;
    let isResizing = false;
    let selectionStart = null;
    let selectionEnd = null;
    let selectedCells = [];
    let activeDersId = null;
    let draggedBlok = null;
    let dragOffset = { x: 0, y: 0 };
    
    // Resize işlemleri için değişkenler
    let resizingBlock = null;
    let resizingGun = null;
    let resizingBaslangic = null;
    let resizingBitis = null;
    let startY = 0;
    let gridSnapEnabled = true; // Izgaraya yapışma özelliği
    
    // Resize işlemleri için olay dinleyicileri
    document.addEventListener('mousedown', function(e) {
        // Tıklanan element resize kolu mu?
        if (e.target.classList.contains('ders-blok-resize')) {
            e.preventDefault();
            e.stopPropagation();
            
            // Resize başlat
            isResizing = true;
            
            // Resize edilen bloğu belirle
            resizingBlock = e.target.closest('.ders-blok');
            
            // Resize için başlangıç konumunu kaydet
            startY = e.clientY;
            
            // Resize bilgilerini al
            resizingGun = parseInt(e.target.getAttribute('data-gun'));
            resizingBaslangic = parseInt(e.target.getAttribute('data-baslangic'));
            resizingBitis = parseInt(e.target.getAttribute('data-bitis'));
            
            // Bilgi metnini güncelle
            document.getElementById('dragDropInfo').textContent = 'Ders süresini değiştirmek için yukarı/aşağı sürükleyin';
        }
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;
        
        // Fare hareketi (piksel cinsinden)
        const diffY = e.clientY - startY;
        
        // Her hücre 50px yüksekliğinde
        const cellHeight = 50;
        
        // Kaç hücre değişecek
        const cellsDiff = Math.round(diffY / cellHeight);
        
        // En az 0.5 hücre kadar (25px) hareket ettiyse değişiklik yap
        if (Math.abs(cellsDiff) >= 1) {
            // Yeni bitiş saati hesapla
            let yeniBitis = resizingBitis + cellsDiff;
            
            // En az bir 30 dakikalık slot (başlangıç saati olmalı minimum)
            if (yeniBitis < resizingBaslangic) {
                yeniBitis = resizingBaslangic;
            }
            
            // Maksimum 3 saat (6 tane 30 dakikalık slot)
            const maxSure = resizingBaslangic + 5; // 6 slot - 1 (başlangıç dahil)
            if (yeniBitis > maxSure) {
                yeniBitis = maxSure;
            }
            
            // Değişiklik varsa uygula
            if (yeniBitis !== resizingBitis) {
                // İlgili hücreyi bul
                const cell = document.querySelector(`.schedule-cell[data-gun="${resizingGun}"][data-saat="${resizingBaslangic}"]`);
                if (!cell) return;
                
                // Ders ID'sini al
                const dersId = cell.getAttribute('data-ders-id');
                if (!dersId) return;
                
                // Ders bilgilerini al
                const dersKarti = document.querySelector(`.ders-karti[data-ders-id="${dersId}"]`);
                if (!dersKarti) return;
                
                const dersAdi = dersKarti.getAttribute('data-ders-adi');
                
                // Eğer küçültüyorsak fazla hücreleri temizle
                if (yeniBitis < resizingBitis) {
                    for (let s = yeniBitis + 1; s <= resizingBitis; s++) {
                        const temizlenecekHucre = document.querySelector(`.schedule-cell[data-gun="${resizingGun}"][data-saat="${s}"]`);
                        if (temizlenecekHucre) {
                            clearCellData(temizlenecekHucre);
                        }
                    }
                }
                
                // Eğer büyütüyorsak ek hücreleri ekle
                if (yeniBitis > resizingBitis) {
                    // Ders renk indeksini belirle
                    const renkIndex = parseInt(dersId) % 10;
                    
                    for (let s = resizingBitis + 1; s <= yeniBitis; s++) {
                        const eklenecekHucre = document.querySelector(`.schedule-cell[data-gun="${resizingGun}"][data-saat="${s}"]`);
                        if (eklenecekHucre) {
                            // Hücre boş mu kontrol et
                            if (eklenecekHucre.hasAttribute('data-ders-id')) {
                                // Dolu hücreye denk geldik, bitiş sınırını değiştir
                                yeniBitis = s - 1;
                                break;
                            }
                            
                            // Hücreyi ders ile işaretle
                            eklenecekHucre.setAttribute('data-ders-id', dersId);
                            eklenecekHucre.classList.add(`ders-renk-${renkIndex}`);
                            eklenecekHucre.classList.add('devam-hucresi');
                            
                            // Devam hücresi görselini oluştur - Resim 5'teki gibi tek blok görünümü için
                            eklenecekHucre.innerHTML = `
                                <div class="ders-devam-blogu ders-renk-${renkIndex}"></div>
                            `;
                            
                            // Hücre sınırlarını kaldır - tek blok görünümü için
                            eklenecekHucre.style.borderTop = "none";
                            eklenecekHucre.style.borderBottom = "none";
                            
                            // Form değerini güncelle
                            document.getElementById(`ders_${resizingGun}_${s}`).value = dersId;
                        }
                    }
                }
                
                // Hücreyi güncelle
                cell.setAttribute('data-bitis', yeniBitis);
                
                // Yeni zaman bilgilerini hesapla
                const baslangic = formatTimeFromIndex(resizingBaslangic);
                const bitis = formatTimeFromIndex(yeniBitis + 1); // Bitiş bir sonraki saat dilimi
                
                // Süreyi hesapla
                const sureDakika = (yeniBitis - resizingBaslangic + 1) * 30;
                
                // Renk indeksini belirle
                const renkIndex = parseInt(dersId) % 10;
                
                // Bloğu güncelle - daha profesyonel görünüm ve belirgin saat bilgisi
                cell.innerHTML = `
                    <div class="ders-blok ders-renk-${renkIndex}">
                        <div class="ders-blok-baslik">${dersAdi}</div>
                        <div class="ders-blok-saat" style="background-color: rgba(0, 0, 0, 0.2); padding: 3px 8px; border-radius: 4px; margin: 3px 0;">
                            <strong>${baslangic}</strong> - ${bitis}
                        </div>
                        <div class="ders-blok-sure">${sureDakika} dk</div>
                        <div class="ders-blok-resize" data-gun="${resizingGun}" data-baslangic="${resizingBaslangic}" data-bitis="${yeniBitis}"></div>
                    </div>
                `;
                
                // Güncellenen bitiş saatini kaydet
                resizingBitis = yeniBitis;
                
                // Fare başlangıç pozisyonunu güncelle
                startY = e.clientY;
            }
        }
    });
    
    document.addEventListener('mouseup', function() {
        if (isResizing) {
            // Resize işlemini bitir
            isResizing = false;
            resizingBlock = null;
            
            // Bilgi metnini sıfırla
            document.getElementById('dragDropInfo').textContent = 'Ders kartına tıklayıp takvimde seçim yapın veya dersleri sürükleyip bırakın';
        }
    });
    
    // Ders bloklarını sürüklenebilir yap
    document.addEventListener('mousedown', function(e) {
        // Ders bloğuna tıklandığında ve resize koluna tıklanmadığında
        const dersBlok = e.target.closest('.ders-blok');
        if (dersBlok && !e.target.classList.contains('ders-blok-resize') && !isResizing) {
            // Sürükleme modunu etkinleştir
            dersBlok.setAttribute('draggable', 'true');
            
            dersBlok.addEventListener('dragstart', function(e) {
                const hucre = this.closest('.schedule-cell');
                if (!hucre) return;
                
                // Bilgileri al
                const dersId = hucre.getAttribute('data-ders-id');
                const gun = hucre.getAttribute('data-gun');
                const baslangic = hucre.getAttribute('data-baslangic');
                const bitis = hucre.getAttribute('data-bitis');
                
                // Veriyi taşı
                e.dataTransfer.setData('text/plain', dersId);
                e.dataTransfer.setData('application/json', JSON.stringify({
                    type: 'blok',
                    dersId: dersId,
                    gun: gun,
                    baslangic: baslangic,
                    bitis: bitis
                }));
                
                // Stil ekle
                this.classList.add('dragging');
                
                // Orijinal hücreyi temizleyelim
                setTimeout(() => {
                    clearCellData(hucre);
                }, 10);
            }, { once: true });
            
            dersBlok.addEventListener('dragend', function(e) {
                // Sürükleme bittikten sonra
                this.classList.remove('dragging');
                this.setAttribute('draggable', 'false');
            }, { once: true });
        }
    });
    
    // Ders kartlarını drag & drop için hazırla
    document.querySelectorAll('.ders-kartlari .ders-karti').forEach(kart => {
        kart.setAttribute('draggable', 'true');
        
        kart.addEventListener('dragstart', function(e) {
            const dersId = this.getAttribute('data-ders-id');
            e.dataTransfer.setData('text/plain', dersId);
            e.dataTransfer.effectAllowed = 'copy';
            
            // Taşıma stili ekle
            this.classList.add('dragging');
        });
        
        kart.addEventListener('dragend', function() {
            this.classList.remove('dragging');
        });
        
        // Ders kartına tıklandığında seçili hale getir
        kart.addEventListener('click', function() {
            // Önceki seçileni kaldır
            document.querySelectorAll('.ders-karti.selected').forEach(k => {
                k.classList.remove('selected');
            });
            
            // Bu kartı seç
            this.classList.add('selected');
            
            // Aktif ders ID'sini güncelle
            activeDersId = this.getAttribute('data-ders-id');
            
            // Seçim moduna geç
            document.getElementById('scheduleTable').classList.add('selection-mode');
            
            // Bilgi metni güncelle
            document.getElementById('dragDropInfo').textContent = 'Takvimde seçim yaparak dersi ekleyebilirsiniz';
        });
    });
    
    // Hücre tıklama olayları
    scheduleTable.addEventListener('click', function(e) {
        const cell = e.target.closest('.schedule-cell');
        if (!cell) return;
        
        // Seçim modu aktif ise
        if (scheduleTable.classList.contains('selection-mode')) {
            if (!selectionStart) {
                // Seçim başlat
                selectionStart = cell;
                selectionStart.classList.add('selection-start');
                
                // Tek hücrelik seçim
                selectedCells = [selectionStart];
                
                // Ders ID'si atanmışsa seçilen hücreyi temizle
                if (selectionStart.hasAttribute('data-ders-id')) {
                    clearCellData(selectionStart);
                }
            } else {
                // Seçim tamamla
                selectionEnd = cell;
                
                // Seçim aralığını hesapla
                const cells = calculateSelectionRange(selectionStart, selectionEnd);
                
                // Seçilen hücreleri uygula
                selectedCells = cells;
                
                // Tüm hücreleri temizle
                selectedCells.forEach(cell => {
                    if (cell.hasAttribute('data-ders-id')) {
                        clearCellData(cell);
                    }
                });
                
                // Seçilen hücrelere aktif dersi ata
                if (activeDersId) {
                    applyDersToSelectedCells(activeDersId);
                }
                
                // Seçimi temizle
                document.querySelectorAll('.schedule-cell.selection-start, .schedule-cell.selection-highlight').forEach(cell => {
                    cell.classList.remove('selection-start', 'selection-highlight');
                });
                
                // Seçim modunu kapat
                scheduleTable.classList.remove('selection-mode');
                selectionStart = null;
                selectionEnd = null;
                selectedCells = [];
                
                // Bilgi metni sıfırla
                document.getElementById('dragDropInfo').textContent = 'Ders kartına tıklayıp takvimde seçim yapın veya dersleri sürükleyip bırakın';
                
                // Ders kartı seçimini kaldır
                document.querySelectorAll('.ders-karti.selected').forEach(k => {
                    k.classList.remove('selected');
                });
                
                activeDersId = null;
            }
        } else {
            // Normal hücre tıklama
            // Ders bloğuna tıklandıysa
            const dersBlok = e.target.closest('.ders-blok');
            if (dersBlok) {
                // Resize kısmına tıklanmadıysa (resize olayı ayrı yönetiliyor)
                if (!e.target.classList.contains('ders-blok-resize')) {
                    // Ders bloğunu silme onayı
                    if (confirm("Bu ders bloğunu kaldırmak istiyor musunuz?")) {
                        clearCellData(cell);
                    }
                }
                return;
            }
            
            if (cell.hasAttribute('data-ders-id')) {
                // Hücreyi temizle
                if (confirm("Bu ders bloğunu kaldırmak istiyor musunuz?")) {
                    clearCellData(cell);
                }
            } else {
                // Seçim modunu aktifleştir ve bilgi ver
                document.getElementById('dragDropInfo').textContent = 'Önce soldan bir ders kartı seçiniz';
            }
        }
    });
    
    // Hücrelerde hover işlemleri (seçim sırasında)
    scheduleTable.addEventListener('mouseover', function(e) {
        const cell = e.target.closest('.schedule-cell');
        if (!cell) return;
        
        // Seçim modu aktifse ve seçim başladıysa geçici seçim göster
        if (scheduleTable.classList.contains('selection-mode') && selectionStart) {
            // Önceki vurguları temizle
            document.querySelectorAll('.schedule-cell.selection-highlight').forEach(c => {
                c.classList.remove('selection-highlight');
            });
            
            // Geçici seçim aralığını hesapla
            const tempCells = calculateSelectionRange(selectionStart, cell);
            
            // Aralıktaki hücreleri vurgula
            tempCells.forEach(c => {
                if (c !== selectionStart) {
                    c.classList.add('selection-highlight');
                }
            });
        }
    });
    
    // Tabloda sürükle bırak (drop) olayları
    scheduleTable.addEventListener('dragover', function(e) {
        e.preventDefault();
        const cell = e.target.closest('.schedule-cell');
        if (cell) {
            e.dataTransfer.dropEffect = 'copy';
            
            try {
                // Sürüklenen bloğun bilgilerini al
                const jsonData = e.dataTransfer.getData('application/json');
                if (jsonData) {
                    const data = JSON.parse(jsonData);
                    if (data.type === 'blok') {
                        // Sürüklenen bloğun süresini al
                        const blokSuresi = parseInt(data.bitis) - parseInt(data.baslangic);
                        
                        // Izgara yapışma etkisini göster
                        const gunIndex = parseInt(cell.getAttribute('data-gun'));
                        const saatIndex = parseInt(cell.getAttribute('data-saat'));
                        
                        // Önce tüm vurguları temizle
                        document.querySelectorAll('.schedule-cell.dragover').forEach(c => {
                            c.classList.remove('dragover', 'dragover-main', 'dragover-extend');
                        });
                        
                        // Ana hücreyi vurgula
                        cell.classList.add('dragover', 'dragover-main');
                        
                        // Uzatılmış blok için diğer hücreleri vurgula
                        if (gridSnapEnabled && blokSuresi > 0) {
                            for (let i = 1; i <= blokSuresi; i++) {
                                const extendCell = document.querySelector(`.schedule-cell[data-gun="${gunIndex}"][data-saat="${saatIndex + i}"]`);
                                if (extendCell) {
                                    // Hücre dolu mu kontrol et
                                    if (extendCell.hasAttribute('data-ders-id') && 
                                        extendCell.getAttribute('data-ders-id') !== data.dersId) {
                                        break; // Dolu hücre varsa vurgulamayı durdur
                                    }
                                    extendCell.classList.add('dragover', 'dragover-extend');
                                }
                            }
                        }
                        return;
                    }
                }
            } catch (e) {
                // JSON veri yoksa veya hata varsa sadece ana hücreyi vurgula
            }
            
            // Normal sürükleme için yalnızca hücreyi vurgula
            cell.classList.add('dragover', 'dragover-main');
            
            // Diğer hücrelerdeki göstergeyi kaldır
            document.querySelectorAll('.schedule-cell.dragover').forEach(c => {
                if (c !== cell) c.classList.remove('dragover', 'dragover-main', 'dragover-extend');
            });
        }
    });
    
    scheduleTable.addEventListener('dragleave', function(e) {
        const cell = e.target.closest('.schedule-cell');
        if (cell) {
            // Yalnızca doğrudan bu hücreye ait vurgulamayı kaldır
            cell.classList.remove('dragover', 'dragover-main', 'dragover-extend');
        }
    });
    
    scheduleTable.addEventListener('drop', function(e) {
        e.preventDefault();
        const cell = e.target.closest('.schedule-cell');
        if (cell) {
            // Tüm drop göstergelerini kaldır
            document.querySelectorAll('.schedule-cell.dragover').forEach(c => {
                c.classList.remove('dragover', 'dragover-main', 'dragover-extend');
            });
            
            // Hücrede daha önce ders var mı kontrol et ve temizle
            if (cell.hasAttribute('data-ders-id')) {
                clearCellData(cell);
            }
            
            // Sürüklenen dersi al
            const dersId = e.dataTransfer.getData('text/plain');
            
            try {
                // Ders bloğu mu yoksa ders kartı mı sürükleniyor kontrol et
                const jsonData = e.dataTransfer.getData('application/json');
                if (jsonData) {
                    const data = JSON.parse(jsonData);
                    // Eğer bu bir ders bloğu ise
                    if (data.type === 'blok') {
                        // Ders bloğunu doğrudan ekle
                        const gunIndex = parseInt(cell.getAttribute('data-gun'));
                        const saatIndex = parseInt(cell.getAttribute('data-saat'));
                        const dersId = data.dersId;
                        
                        // Orijinal bloğun süresini al
                        const blokSuresi = parseInt(data.bitis) - parseInt(data.baslangic);
                        
                        // Izgaraya yapışma özelliği ile yeni konuma uygula
                        selectedCells = [cell];
                        
                        // Blok süresi kadar hücre ekle, ancak dolu hücre varsa durdur
                        let uygulanabilirSure = blokSuresi;
                        for (let i = 1; i <= blokSuresi; i++) {
                            const nextCell = document.querySelector(`.schedule-cell[data-gun="${gunIndex}"][data-saat="${saatIndex + i}"]`);
                            if (nextCell) {
                                // Hücre dolu mu kontrol et (farklı ders ile dolu mu?)
                                if (nextCell.hasAttribute('data-ders-id') && nextCell.getAttribute('data-ders-id') !== dersId) {
                                    uygulanabilirSure = i - 1; // Dolu hücre öncesine kadar
                                    break;
                                }
                                selectedCells.push(nextCell);
                            } else {
                                uygulanabilirSure = i - 1; // Tablo dışına çıkılıyorsa
                                break;
                            }
                        }
                        
                        // Animasyon etkisiyle dersi uygula
                        setTimeout(() => {
                            applyDersToSelectedCells(dersId);
                            
                            // Eklenen bloğu vurgula
                            const eklenenBlok = cell.querySelector('.ders-blok');
                            if (eklenenBlok) {
                                eklenenBlok.classList.add('just-dropped');
                                setTimeout(() => {
                                    eklenenBlok.classList.remove('just-dropped');
                                }, 500);
                            }
                            
                            // Seçimi temizle
                            selectedCells = [];
                        }, 50);
                        
                        return;
                    }
                }
            } catch (e) {
                console.error("JSON işleme hatası:", e);
            }
            
            // Normal ders kartı sürükleme işlemi
            if (dersId) {
                // Doğrudan ders bloğunu ekle - tek hücrelik olarak başla
                selectedCells = [cell];
                applyDersToSelectedCells(dersId);
                
                // Tüm seçimleri temizle
                document.querySelectorAll('.schedule-cell.selection-start, .schedule-cell.selection-highlight').forEach(cell => {
                    cell.classList.remove('selection-start', 'selection-highlight');
                });
                
                // Eklenen bloğu vurgula
                const eklenenBlok = cell.querySelector('.ders-blok');
                if (eklenenBlok) {
                    eklenenBlok.classList.add('just-dropped');
                    setTimeout(() => {
                        eklenenBlok.classList.remove('just-dropped');
                    }, 500);
                }
                
                // Bilgi metni güncelle
                document.getElementById('dragDropInfo').textContent = 'Ders eklendi! Boyutlandırmak için alttaki kolu kullanabilirsiniz.';
                
                // Seçim modunu kapat ve değişkenleri temizle
                scheduleTable.classList.remove('selection-mode');
                selectionStart = null;
                selectionEnd = null;
                selectedCells = [];
                activeDersId = null;
            }
        }
    });
    
    // İki hücre arasındaki tüm hücreleri hesapla (seçim için)
    function calculateSelectionRange(startCell, endCell) {
        const startGun = parseInt(startCell.getAttribute('data-gun'));
        const startSaat = parseInt(startCell.getAttribute('data-saat'));
        const endGun = parseInt(endCell.getAttribute('data-gun'));
        const endSaat = parseInt(endCell.getAttribute('data-saat'));
        
        // Başlangıç ve bitiş hücrelerini doğru sıraya koy
        const minGun = Math.min(startGun, endGun);
        const maxGun = Math.max(startGun, endGun);
        const minSaat = Math.min(startSaat, endSaat);
        const maxSaat = Math.max(startSaat, endSaat);
        
        // Seçim tek gün içinde olmalı (yatay seçim)
        if (minGun !== maxGun) {
            return [startCell]; // Tek hücre dön
        }
        
        // Aralıktaki tüm hücreleri bul
        const selectedCells = [];
        for (let saat = minSaat; saat <= maxSaat; saat++) {
            const cell = document.querySelector(`.schedule-cell[data-gun="${minGun}"][data-saat="${saat}"]`);
            if (cell) {
                selectedCells.push(cell);
            }
        }
        
        return selectedCells;
    }
    
    // Bir hücreyi tamamen temizle
    function clearCellData(cell) {
        // Diğer hücreleri de temizleyin (birleşik bloklar için)
        const dersId = cell.getAttribute('data-ders-id');
        const gun = parseInt(cell.getAttribute('data-gun'));
        
        // Eğer hücre bir ana hücre ise ve birleştirilmiş blok varsa
        if (cell.hasAttribute('data-baslangic') && cell.hasAttribute('data-bitis')) {
            const baslangicSaat = parseInt(cell.getAttribute('data-baslangic'));
            const bitisSaat = parseInt(cell.getAttribute('data-bitis'));
            
            // Birleştirilmiş bloğun tüm hücrelerini temizle
            if (bitisSaat > baslangicSaat) {
                for (let saat = baslangicSaat + 1; saat <= bitisSaat; saat++) {
                    const ekHucre = document.querySelector(`.schedule-cell[data-gun="${gun}"][data-saat="${saat}"]`);
                    if (ekHucre && ekHucre.getAttribute('data-ders-id') === dersId) {
                        // Ek hücrenin özelliklerini temizle
                        ekHucre.innerHTML = '';
                        ekHucre.removeAttribute('data-ders-id');
                        for (let i = 0; i < 10; i++) {
                            ekHucre.classList.remove(`ders-renk-${i}`);
                        }
                        ekHucre.classList.remove('devam-hucresi');
                        
                        // Form alanını güncelle
                        document.getElementById(`ders_${gun}_${saat}`).value = '';
                    }
                }
            }
        }
        
        // Ders renklerini temizle
        for (let i = 0; i < 10; i++) {
            cell.classList.remove(`ders-renk-${i}`);
        }
        
        // Hücre içeriğini ve özelliklerini temizle
        cell.innerHTML = '';
        cell.removeAttribute('data-ders-id');
        cell.removeAttribute('data-baslangic');
        cell.removeAttribute('data-bitis');
        cell.classList.remove('devam-hucresi');
        
        // Form alanını güncelle
        const saat = cell.getAttribute('data-saat');
        document.getElementById(`ders_${gun}_${saat}`).value = '';
    }
    
    // Seçilen tüm hücrelere dersi uygula - Resim 5'teki gibi tek parça blok görünümü
    function applyDersToSelectedCells(dersId) {
        if (!selectedCells.length || !dersId) return;
        
        // Ders adını al
        const dersAdi = document.querySelector(`.ders-karti[data-ders-id="${dersId}"]`).getAttribute('data-ders-adi');
        
        // Saat aralığını hesapla
        const firstCell = selectedCells[0];
        const lastCell = selectedCells[selectedCells.length - 1];
        
        const gun = parseInt(firstCell.getAttribute('data-gun'));
        const baslangicSaat = parseInt(firstCell.getAttribute('data-saat'));
        const bitisSaat = parseInt(lastCell.getAttribute('data-saat'));
        
        // Başlangıç ve bitiş saatlerini oluştur
        const baslangic = formatTimeFromIndex(baslangicSaat);
        const bitis = formatTimeFromIndex(bitisSaat + 1); // Bitişi bir sonraki saat dilimi yap
        
        // Blok süresi (dakika olarak)
        const sureDakika = (bitisSaat - baslangicSaat + 1) * 30;
        
        // Renk indeksini belirle - YKS renklerini kullan
        const renkIndex = parseInt(dersId) % 10;
        
        // Eğer tek hücre ise standart blok
        if (selectedCells.length === 1) {
            // İlk ve tek hücreye tüm içeriği ekle
            firstCell.setAttribute('data-ders-id', dersId);
            firstCell.setAttribute('data-baslangic', baslangicSaat);
            firstCell.setAttribute('data-bitis', bitisSaat);
            firstCell.classList.add(`ders-renk-${renkIndex}`);
            
            // Tek hücre için tam blok görünümü - daha küçük yazı boyutu
            firstCell.innerHTML = `
                <div class="ders-blok ders-renk-${renkIndex}" style="border-radius: 8px;">
                    <div class="ders-blok-baslik" style="font-size: 9px; margin-bottom: 1px; line-height: 1.1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 95%;">${dersAdi}</div>
                    <div class="ders-blok-saat" style="background-color: rgba(0, 0, 0, 0.15); padding: 1px 3px; border-radius: 3px; margin: 1px 0; font-size: 8px; line-height: 1.1;">
                        <strong>${baslangic}</strong>-${bitis}
                    </div>
                    <div class="ders-blok-sure" style="font-size: 7px; margin-top: 1px; line-height: 1;">${sureDakika}dk</div>
                    <div class="ders-blok-resize" data-gun="${gun}" data-baslangic="${baslangicSaat}" data-bitis="${bitisSaat}"></div>
                </div>
            `;
            
            // Form değerini güncelle
            document.getElementById(`ders_${gun}_${baslangicSaat}`).value = dersId;
            
            return;
        }
        
        // Birden fazla hücre için - tamamen tek parça blok görünümü (Ekran Görüntüsü 12'deki gibi)
        
        // İlk olarak ana hücreyi belirle - bizim için ilk hücre olacak
        const mainCell = firstCell;
        
        // Diğer tüm hücreleri görünmez yap ve içeriklerini temizle
        selectedCells.forEach(cell => {
            // İlk hücre dışındaki her hücreyi temizle
            if(cell !== mainCell) {
                cell.classList.add('devam-hucresi', 'hidden-cell');
                cell.style.border = "none"; // Tüm kenarlıkları temizle
                cell.style.padding = "0";
                cell.style.margin = "0";
                cell.style.height = "0"; // Sıfır yükseklik
                cell.innerHTML = ''; // İçerik temizle
                cell.setAttribute('data-ders-id', dersId);
                
                // Form değerini güncelle
                const cellGun = cell.getAttribute('data-gun');
                const cellSaat = cell.getAttribute('data-saat');
                document.getElementById(`ders_${cellGun}_${cellSaat}`).value = dersId;
            }
        });
        
        // Ana hücreyi (ilk hücre) yapılandır
        mainCell.setAttribute('data-ders-id', dersId);
        mainCell.setAttribute('data-baslangic', baslangicSaat);
        mainCell.setAttribute('data-bitis', bitisSaat);
        mainCell.classList.add(`ders-renk-${renkIndex}`);
        
        // Ana hücrenin boyutunu ayarla - tüm bloğun toplam yüksekliğinde 
        const totalHeight = (selectedCells.length * 100) + '%';  // Her bir hücre 45px 
        
        // Ana hücreye tek bir büyük blok oluştur
        mainCell.innerHTML = `
            <div class="ders-blok ders-renk-${renkIndex}" 
                 style="position: absolute; 
                        left: 0; 
                        top: 0; 
                        right: 0; 
                        bottom: 0; 
                        height: ${totalHeight}; 
                        border-radius: 8px; 
                        z-index: 5; 
                        display: flex; 
                        flex-direction: column; 
                        justify-content: center; 
                        align-items: center; 
                        text-align: center;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div class="ders-blok-baslik" 
                     style="font-weight: bold; 
                            font-size: 14px; 
                            white-space: nowrap; 
                            overflow: hidden; 
                            text-overflow: ellipsis; 
                            width: 100%; 
                            padding: 0 8px; 
                            margin-bottom: 5px;">${dersAdi}</div>
                <div class="ders-blok-saat" 
                     style="background-color: rgba(0, 0, 0, 0.15); 
                            padding: 3px 8px; 
                            border-radius: 4px; 
                            margin: 3px 0; 
                            font-size: 13px;">
                    <strong>${baslangic}</strong> - ${bitis}
                </div>
                <div class="ders-blok-sure" 
                     style="font-size: 12px; 
                            margin-top: 4px;">${sureDakika} dk</div>
                <div class="ders-blok-resize" 
                     data-gun="${gun}" 
                     data-baslangic="${baslangicSaat}" 
                     data-bitis="${bitisSaat}"></div>
            </div>
        `;
        
        // Form değerini güncelle
        document.getElementById(`ders_${gun}_${baslangicSaat}`).value = dersId;
    }
    
    // Saat indeksini formatlı saat:dakika olarak dönüştür
    function formatTimeFromIndex(index) {
        const saat = Math.floor(index / 2) + 8; // 8:00'dan başla
        const dakika = (index % 2) === 0 ? "00" : "30";
        return `${saat < 10 ? '0' + saat : saat}:${dakika}`;
    }
    
    // Mevcut programı yükle
    loadExistingSchedule();
    
    // Kaydet butonuna tıklandığında programı gönder
    const saveButton = document.getElementById('saveScheduleBtn');
    if (saveButton) {
        saveButton.addEventListener('click', function() {
            document.getElementById('scheduleForm').submit();
        });
    }
}

/**
 * Mevcut programı tabloya yükle
 */
function loadExistingSchedule() {
    // Program verisi global değişkenden gelir (backend tarafından tanımlanır)
    if (typeof programVerisi === 'undefined') {
        console.warn("Program verisi bulunamadı");
        return;
    }
    
    console.log("Program verisi yükleniyor:", programVerisi);
    
    // Tüm hücreleri temizle önce
    const allCells = document.querySelectorAll('td.schedule-cell');
    if (allCells.length === 0) {
        console.error("Tabloda hiç hücre bulunamadı!");
        return;
    } else {
        console.log(`Toplam ${allCells.length} hücre bulundu`);
    }
    
    // Mevcut program verilerini bir grup halinde düzenle (aynı dersin ardışık blokları için)
    const programBloklari = {};
    
    // Programdaki her hücreyi işle
    for (const key in programVerisi) {
        if (programVerisi.hasOwnProperty(key)) {
            const [gun, saat] = key.split('_');
            const dersId = programVerisi[key];
            const gunInt = parseInt(gun);
            const saatInt = parseInt(saat);
            
            // Bu gün için blok zaten başlatılmış mı?
            if (!programBloklari[gunInt]) {
                programBloklari[gunInt] = [];
            }
            
            // Mevcut bloklar arasında bu dersin devamı var mı?
            let blokBulundu = false;
            for (let i = 0; i < programBloklari[gunInt].length; i++) {
                const blok = programBloklari[gunInt][i];
                
                // Eğer aynı ders ve son saatin hemen ardışık saati ise
                if (blok.dersId === dersId && blok.bitisSaat === saatInt - 1) {
                    // Mevcut bloğun bitiş saatini güncelle
                    blok.bitisSaat = saatInt;
                    blokBulundu = true;
                    break;
                }
                
                // Ya da aynı ders ve ilk saatin hemen önceki saati ise
                if (blok.dersId === dersId && blok.baslangicSaat === saatInt + 1) {
                    // Mevcut bloğun başlangıç saatini güncelle
                    blok.baslangicSaat = saatInt;
                    blokBulundu = true;
                    break;
                }
            }
            
            // Eğer mevcut bloklarda bulunamadıysa yeni blok oluştur
            if (!blokBulundu) {
                programBloklari[gunInt].push({
                    dersId: dersId,
                    baslangicSaat: saatInt,
                    bitisSaat: saatInt
                });
            }
            
            // Form değerini güncelle
            const formElement = document.getElementById(`ders_${gun}_${saat}`);
            if (formElement) {
                formElement.value = dersId;
            }
        }
    }
    
    // Blokları ekrana yerleştir
    for (const gun in programBloklari) {
        if (programBloklari.hasOwnProperty(gun)) {
            const gunBloklari = programBloklari[gun];
            
            for (const blok of gunBloklari) {
                // Blok başlangıç hücresini bul
                const baslangicHucre = document.querySelector(`.schedule-cell[data-gun="${gun}"][data-saat="${blok.baslangicSaat}"]`);
                if (!baslangicHucre) continue;
                
                // Ders adını al
                const dersOption = document.querySelector(`#dersSelector option[value="${blok.dersId}"]`) ||
                                  document.querySelector(`.ders-karti[data-ders-id="${blok.dersId}"]`);
                
                if (!dersOption) {
                    console.error(`Ders bilgisi bulunamadı: ${blok.dersId}`);
                    continue;
                }
                
                const dersAdi = dersOption.tagName === 'OPTION' ? 
                                dersOption.text : 
                                dersOption.getAttribute('data-ders-adi');
                
                // Saat hesaplaması
                const baslangic = formatTimeFromIndex(blok.baslangicSaat);
                const bitis = formatTimeFromIndex(blok.bitisSaat + 1);
                
                // Blok süresi (dakika olarak)
                const sureDakika = (blok.bitisSaat - blok.baslangicSaat + 1) * 30;
                
                // Renk indeksini belirle
                const renkIndex = parseInt(blok.dersId) % 10;
                
                // Ana hücreyi güncelle
                baslangicHucre.setAttribute('data-ders-id', blok.dersId);
                baslangicHucre.setAttribute('data-baslangic', blok.baslangicSaat);
                baslangicHucre.setAttribute('data-bitis', blok.bitisSaat);
                baslangicHucre.classList.add(`ders-renk-${renkIndex}`);
                
                // Tek hücrelik blok mu kontrolü
                if (blok.baslangicSaat === blok.bitisSaat) {
                    // Ana hücre içeriğini oluştur - Tek hücrelik blok (daha küçük yazı boyutu)
                    baslangicHucre.innerHTML = `
                        <div class="ders-blok ders-renk-${renkIndex}" style="border-radius: 8px;">
                            <div class="ders-blok-baslik" style="font-size: 9px; margin-bottom: 1px; line-height: 1.1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 95%;">${dersAdi}</div>
                            <div class="ders-blok-saat" style="background-color: rgba(0, 0, 0, 0.15); padding: 1px 3px; border-radius: 3px; margin: 1px 0; font-size: 8px; line-height: 1.1;">
                                <strong>${baslangic}</strong>-${bitis}
                            </div>
                            <div class="ders-blok-sure" style="font-size: 7px; margin-top: 1px; line-height: 1;">${sureDakika}dk</div>
                            <div class="ders-blok-resize" data-gun="${gun}" data-baslangic="${blok.baslangicSaat}" data-bitis="${blok.bitisSaat}"></div>
                        </div>
                    `;
                } else {
                    // Birden fazla hücre kaplayan blok - Ekran Görüntüsü 12'deki gibi tek parça
                    // Önce diğer hücreleri görünmez yap
                    for (let saat = blok.baslangicSaat + 1; saat <= blok.bitisSaat; saat++) {
                        const hucre = document.querySelector(`.schedule-cell[data-gun="${gun}"][data-saat="${saat}"]`);
                        if (hucre) {
                            // Hücre bilgilerini güncelle ama görünmez yap
                            hucre.setAttribute('data-ders-id', blok.dersId);
                            hucre.classList.add('devam-hucresi', 'hidden-cell');
                            hucre.style.border = "none";
                            hucre.style.padding = "0";
                            hucre.style.margin = "0";
                            hucre.style.height = "0";
                            hucre.innerHTML = '';
                        }
                    }
                    
                    // Ana hücrenin yüksekliğini ayarla - tam blok olarak görünsün
                    const totalHeight = ((blok.bitisSaat - blok.baslangicSaat + 1) * 100) + '%';
                    
                    // Ana hücre içeriğini oluştur - Tam tek blok görünümü
                    baslangicHucre.innerHTML = `
                        <div class="ders-blok ders-renk-${renkIndex}" 
                             style="position: absolute; 
                                    left: 0; 
                                    top: 0; 
                                    right: 0; 
                                    bottom: 0; 
                                    height: ${totalHeight}; 
                                    border-radius: 8px; 
                                    z-index: 5; 
                                    display: flex; 
                                    flex-direction: column; 
                                    justify-content: center; 
                                    align-items: center; 
                                    text-align: center;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <div class="ders-blok-baslik" 
                                 style="font-weight: bold; 
                                        font-size: 14px; 
                                        white-space: nowrap; 
                                        overflow: hidden; 
                                        text-overflow: ellipsis; 
                                        width: 100%; 
                                        padding: 0 8px; 
                                        margin-bottom: 5px;">${dersAdi}</div>
                            <div class="ders-blok-saat" 
                                 style="background-color: rgba(0, 0, 0, 0.15); 
                                        padding: 3px 8px; 
                                        border-radius: 4px; 
                                        margin: 3px 0; 
                                        font-size: 13px;">
                                <strong>${baslangic}</strong> - ${bitis}
                            </div>
                            <div class="ders-blok-sure" 
                                 style="font-size: 12px; 
                                        margin-top: 4px;">${sureDakika} dk</div>
                            <div class="ders-blok-resize" 
                                 data-gun="${gun}" 
                                 data-baslangic="${blok.baslangicSaat}" 
                                 data-bitis="${blok.bitisSaat}"></div>
                        </div>
                    `;
                }
            }
        }
    }
}

/**
 * Saat indeksini formatlı saat:dakika olarak dönüştür
 */
function formatTimeFromIndex(index) {
    const saat = Math.floor(index / 2) + 8; // 8:00'dan başla
    const dakika = (index % 2) === 0 ? "00" : "30";
    return `${saat < 10 ? '0' + saat : saat}:${dakika}`;
}

/**
 * Önizleme modunu aç/kapat
 */
function togglePreview() {
    const scheduleTable = document.getElementById('scheduleTable');
    scheduleTable.classList.toggle('preview-mode');
    
    const previewButton = document.getElementById('previewToggleBtn');
    if (scheduleTable.classList.contains('preview-mode')) {
        previewButton.innerHTML = '<i class="fas fa-edit me-1"></i> Düzenleme Moduna Dön';
        previewButton.classList.replace('btn-primary', 'btn-secondary');
        document.getElementById('saveScheduleBtn').disabled = true;
        
        // Ders kartlarını devre dışı bırak
        document.querySelectorAll('.ders-karti').forEach(kart => {
            kart.setAttribute('draggable', 'false');
            kart.classList.add('disabled');
        });
        
        // Bilgi metnini güncelle
        document.getElementById('dragDropInfo').textContent = 'Önizleme modunda düzenleme yapamazsınız';
    } else {
        previewButton.innerHTML = '<i class="fas fa-eye me-1"></i> Önizleme Modu';
        previewButton.classList.replace('btn-secondary', 'btn-primary');
        document.getElementById('saveScheduleBtn').disabled = false;
        
        // Ders kartlarını etkinleştir
        document.querySelectorAll('.ders-karti').forEach(kart => {
            kart.setAttribute('draggable', 'true');
            kart.classList.remove('disabled');
        });
        
        // Bilgi metnini sıfırla
        document.getElementById('dragDropInfo').textContent = 'Ders kartına tıklayıp takvimde seçim yapın veya dersleri sürükleyip bırakın';
    }
}

/**
 * Ders filtreleme işlemlerini başlat
 */
function initDersFiltreleme() {
    // Filtre butonları
    const filtreButonlari = document.querySelectorAll('.ders-filtre-buton');
    if (filtreButonlari.length === 0) return;

    filtreButonlari.forEach(buton => {
        buton.addEventListener('click', function() {
            // Tüm butonları devre dışı bırak
            filtreButonlari.forEach(b => b.classList.remove('active'));
            
            // Bu butonu aktif yap
            this.classList.add('active');
            
            // Seçilen filtreyi uygula
            const filtreGrup = this.getAttribute('data-filtre');
            filterDersKartlari(filtreGrup);
        });
    });
    
    // Ders kartlarını filtrele
    function filterDersKartlari(grup) {
        const dersKartlari = document.querySelectorAll('.ders-karti');
        
        dersKartlari.forEach(kart => {
            if (grup === 'tumunu-goster') {
                kart.style.display = 'block';
                return;
            }
            
            const dersGrup = kart.getAttribute('data-ders-grup');
            kart.style.display = (dersGrup === grup) ? 'block' : 'none';
        });
    }
}

/**
 * Tüm programı temizle
 */
function clearSchedule() {
    showConfirmModal('Programı Temizle', 'Tüm ders programını temizlemek istediğinizden emin misiniz? Bu işlem geri alınamaz.', function() {
        // Modern takvim temizleme - ders bloklarını kaldır
        const lessonBlocks = document.querySelectorAll('.lesson-block');
        lessonBlocks.forEach(block => block.remove());
        
        // Eski takvim temizleme - sınıflar kullanılıyorsa desteklemek için
        const cells = document.querySelectorAll('td.schedule-cell');
        cells.forEach(function(cell) {
            // Ders renklerini temizle
            for (let i = 0; i < 10; i++) {
                cell.classList.remove(`ders-renk-${i}`);
            }
            
            // Diğer sınıfları temizle
            cell.classList.remove('devam-hucresi');
            cell.classList.remove('selection-start');
            cell.classList.remove('selection-highlight');
            
            // Hücreyi temizle
            cell.innerHTML = '';
            cell.removeAttribute('data-ders-id');
            cell.removeAttribute('data-baslangic');
            cell.removeAttribute('data-bitis');
            
            // Form değerini temizle
            const gun = cell.getAttribute('data-gun');
            const saat = cell.getAttribute('data-saat');
            const input = document.getElementById(`ders_${gun}_${saat}`);
            if (input) input.value = '';
        });
        
        // Tüm gizli input alanlarını temizle (yeni takvim için)
        for (let gun = 0; gun < 7; gun++) {
            for (let saat = 0; saat < 35; saat++) { // 8:00-24:00 arası maks 32 yarım saatlik dilim (güvenli olması için 35)
                const input = document.getElementById(`ders_${gun}_${saat}`);
                if (input) input.value = '';
            }
        }
        
        // Seçim durumunu sıfırla
        if (document.getElementById('scheduleTable')) {
            document.getElementById('scheduleTable').classList.remove('selection-mode');
        }
        
        // Ders kartı seçimlerini kaldır
        document.querySelectorAll('.ders-karti.selected').forEach(k => {
            k.classList.remove('selected');
        });
        
        // Bilgi metnini sıfırla
        if (document.getElementById('dragDropInfo')) {
            document.getElementById('dragDropInfo').textContent = 'Ders kartına tıklayıp takvimde seçim yapın veya dersleri sürükleyip bırakın';
        }
        
        // Form oluştur ve temizle parametresi ekleyerek gönder
        const temizleInput = document.createElement('input');
        temizleInput.type = 'hidden';
        temizleInput.name = 'temizle';
        temizleInput.value = '1';
        
        const form = document.getElementById('scheduleForm');
        form.appendChild(temizleInput);
        form.submit();
        
        // Kullanıcıya işlemin başarılı olduğunu bildir
        alert('Program başarıyla temizlendi');
    });
}
