/**
 * YKS Çalışma Programı Takip Sistemi - Ana JavaScript Dosyası
 */

// Sayfa yüklendiğinde çalışacak fonksiyon
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap bileşenlerini etkinleştir
    enableBootstrapComponents();
    
    // DataTable'ları etkinleştir
    initDataTables();
    
    // Flash mesajları için kapanma fonksiyonu
    initFlashMessages();
    
    // Form doğrulama işlemlerini etkinleştir
    initFormValidation();
    
    // Sidebar'ı etkinleştir
    initSidebar();
    
    // Öğrenci hızlı arama formunu etkinleştir
    initOgrenciHizliArama();
});

/**
 * Bootstrap bileşenlerini etkinleştir
 */
function enableBootstrapComponents() {
    // Tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Collapse
    var collapseElementList = [].slice.call(document.querySelectorAll('.collapse'));
    collapseElementList.map(function (collapseEl) {
        return new bootstrap.Collapse(collapseEl, {
            toggle: false
        });
    });
    
    // Modal titreme sorununu düzeltme
    fixModalFlickerIssue();
}

/**
 * Modal titreme sorununu düzelt
 */
function fixModalFlickerIssue() {
    // Tüm modallara event listener ekle
    document.querySelectorAll('.modal').forEach(function(modal) {
        // Modal açılırken
        modal.addEventListener('show.bs.modal', function() {
            // Modal titreme problemini düzeltmek için
            document.body.classList.add('modal-open-fix');
            
            // Modal içindeki hover efektlerini devre dışı bırak
            var modalContent = modal.querySelector('.modal-content');
            if (modalContent) {
                modalContent.classList.add('no-hover-effects');
            }
            
            // Silme butonunda hover efektlerini devre dışı bırak
            var deleteButtons = modal.querySelectorAll('.btn-danger');
            deleteButtons.forEach(function(btn) {
                btn.classList.add('no-hover-transform');
            });
        });
        
        // Modal kapanırken
        modal.addEventListener('hidden.bs.modal', function() {
            document.body.classList.remove('modal-open-fix');
            
            // Modal içindeki hover efektlerini tekrar etkinleştir
            var modalContent = modal.querySelector('.modal-content');
            if (modalContent) {
                modalContent.classList.remove('no-hover-effects');
            }
            
            // Silme butonunda hover efektlerini tekrar etkinleştir
            var deleteButtons = modal.querySelectorAll('.btn-danger');
            deleteButtons.forEach(function(btn) {
                btn.classList.remove('no-hover-transform');
            });
        });
    });
}

/**
 * DataTable bileşenlerini etkinleştir
 */
function initDataTables() {
    // Öğrenci tablosu
    if (document.getElementById('ogrenciTable')) {
        $('#ogrenciTable').DataTable({
            "language": {
                "url": "//cdn.datatables.net/plug-ins/1.10.24/i18n/Turkish.json"
            },
            "responsive": true,
            "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tümü"]],
            "pageLength": 25,
            "order": [[1, "asc"]] // Numara sütununa göre sırala
        });
    }
    
    // Ders tablosu
    if (document.getElementById('dersTable')) {
        $('#dersTable').DataTable({
            "language": {
                "url": "//cdn.datatables.net/plug-ins/1.10.24/i18n/Turkish.json"
            },
            "responsive": true,
            "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tümü"]],
            "pageLength": 25
        });
    }
    
    // Konu tablosu
    if (document.getElementById('konuTable')) {
        $('#konuTable').DataTable({
            "language": {
                "url": "//cdn.datatables.net/plug-ins/1.10.24/i18n/Turkish.json"
            },
            "responsive": true,
            "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tümü"]],
            "pageLength": 25,
            "ordering": true,
            "columnDefs": [
                { "orderable": false, "targets": -1 } // Son sütun (aksiyonlar) sıralanamaz
            ]
        });
    }
    
    // Deneme sonuçları tablosu
    if (document.getElementById('denemeSonucTable')) {
        $('#denemeSonucTable').DataTable({
            "language": {
                "url": "//cdn.datatables.net/plug-ins/1.10.24/i18n/Turkish.json"
            },
            "responsive": true,
            "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tümü"]],
            "pageLength": 10,
            "order": [[1, "desc"]] // Tarih sütununa göre azalan sırala
        });
    }
}

/**
 * Flash mesajları için otomatik kapanma ve kapatma butonu
 */
function initFlashMessages() {
    // Flash mesajlarının otomatik kapanması
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-important)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000); // 5 saniye
    
    // Kapatma butonları
    var closeButtons = document.querySelectorAll('.alert .btn-close');
    closeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var alert = button.closest('.alert');
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    });
}

/**
 * Form doğrulama işlemlerini etkinleştir
 */
function initFormValidation() {
    // HTML5 form validation
    var forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Silme işlemi için onay göster
 * @param {string} message - Gösterilecek onay mesajı
 * @returns {boolean} - Onay verildi mi?
 */
function confirmDelete(message) {
    return confirm(message || 'Bu kaydı silmek istediğinizden emin misiniz?');
}

/**
 * Tarih formatını DD.MM.YYYY şeklinde biçimlendir
 * @param {Date} date - Format edilecek tarih
 * @returns {string} - Biçimlendirilmiş tarih
 */
function formatDate(date) {
    if (!date) return '';
    var d = new Date(date);
    var day = d.getDate().toString().padStart(2, '0');
    var month = (d.getMonth() + 1).toString().padStart(2, '0');
    var year = d.getFullYear();
    return day + '.' + month + '.' + year;
}

/**
 * Saat formatını HH:MM şeklinde biçimlendir
 * @param {string} timeStr - Format edilecek saat (HH:MM formatında)
 * @returns {string} - Biçimlendirilmiş saat
 */
function formatTime(timeStr) {
    if (!timeStr) return '';
    var timeParts = timeStr.split(':');
    var hours = timeParts[0].padStart(2, '0');
    var minutes = timeParts[1].padStart(2, '0');
    return hours + ':' + minutes;
}

/**
 * Yüzde biçimlendir (ondalık basamakları düzenle)
 * @param {number} percent - Biçimlendirilecek yüzde
 * @param {number} decimals - Gösterilecek ondalık basamak sayısı
 * @returns {string} - Biçimlendirilmiş yüzde
 */
function formatPercent(percent, decimals = 1) {
    if (isNaN(percent)) return '0%';
    return percent.toFixed(decimals) + '%';
}

/**
 * Onay modal penceresini göster
 * @param {string} title - Modal başlığı
 * @param {string} message - Modal mesajı
 * @param {function} callback - Onay verildiğinde çağrılacak fonksiyon
 */
function showConfirmModal(title, message, callback) {
    // Modal ID'si
    var modalId = 'confirmModal';
    
    // Varolan modalı kaldır
    var existingModal = document.getElementById(modalId);
    if (existingModal) {
        existingModal.remove();
    }
    
    // Yeni modal oluştur
    var modalHtml = `
    <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="${modalId}Label">${title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Kapat"></button>
                </div>
                <div class="modal-body">
                    ${message}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Vazgeç</button>
                    <button type="button" class="btn btn-primary" id="${modalId}Confirm">Onaylıyorum</button>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Modal'ı body'e ekle
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Modal nesnesini oluştur
    var modal = new bootstrap.Modal(document.getElementById(modalId));
    
    // Onay butonuna tıklandığında
    document.getElementById(`${modalId}Confirm`).addEventListener('click', function() {
        modal.hide();
        if (typeof callback === 'function') {
            callback();
        }
    });
    
    // Modal'ı göster
    modal.show();
}

/**
 * Soldaki kenar çubuğunu etkinleştir
 */
function initSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const mobileOverlay = document.querySelector('.mobile-overlay');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    
    if (!sidebar || !mainContent) return;
    
    const isMobile = window.innerWidth < 768;
    
    // Sidebar genişlik değişimi kontrolü (desktop)
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('sidebar-collapsed');
            mainContent.classList.toggle('main-content-expanded');
            
            // Arrow icon yönünü değiştir
            const icon = this.querySelector('i');
            if (icon) {
                if (sidebar.classList.contains('sidebar-collapsed')) {
                    icon.classList.remove('fa-chevron-left');
                    icon.classList.add('fa-chevron-right');
                } else {
                    icon.classList.remove('fa-chevron-right');
                    icon.classList.add('fa-chevron-left');
                }
            }
        });
    }
    
    // Mobil cihazlarda menü açma butonu
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            sidebar.classList.add('mobile-active');
            if (mobileOverlay) {
                mobileOverlay.classList.add('active');
            }
        });
    }
    
    // Mobil cihazlarda overlay tıklandığında
    if (mobileOverlay) {
        mobileOverlay.addEventListener('click', function() {
            sidebar.classList.remove('mobile-active');
            mobileOverlay.classList.remove('active');
        });
    }
    
    // Pencere boyutu değiştiğinde kontrol et
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 768 && sidebar.classList.contains('mobile-active')) {
            sidebar.classList.remove('mobile-active');
            if (mobileOverlay) {
                mobileOverlay.classList.remove('active');
            }
        }
    });
    
    // Alt menü toggle butonlarını etkinleştir
    document.querySelectorAll('.ogrenci-menu-toggle').forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Öğrenci menüsünün görsel olarak aktif olması için 'active' sınıfını ekle/kaldır
            this.classList.toggle('active');
            
            // En yakın parent sidebar-nav-item'ı bul
            const parentItem = this.closest('.sidebar-nav-item');
            if (parentItem) {
                // Alt menüyü bul ve göster/gizle
                const submenu = parentItem.querySelector('.sidebar-submenu');
                if (submenu) {
                    submenu.classList.toggle('show');
                    
                    // Submenu icon'unu döndür
                    const icon = this.querySelector('.submenu-icon');
                    if (icon) {
                        if (submenu.classList.contains('show')) {
                            icon.style.transform = 'rotate(180deg)';
                        } else {
                            icon.style.transform = 'rotate(0deg)';
                        }
                    }
                }
            }
        });
    });
    
    // Öğrenci menüsü seçili olduğunda otomatik aç
    const activeStudentContainer = document.querySelector('.active-student-container');
    if (activeStudentContainer) {
        // Öğrenci bölümüne otomatik olarak active sınıfı ekle
        const toggle = activeStudentContainer.querySelector('.ogrenci-menu-toggle');
        if (toggle) {
            toggle.classList.add('active');
            
            // Icon'u döndür
            const icon = toggle.querySelector('.submenu-icon');
            if (icon) {
                icon.style.transform = 'rotate(180deg)';
            }
        }
        
        // Alt menünün içinde aktif bir öğe varsa otomatik olarak aç
        const submenu = activeStudentContainer.querySelector('.sidebar-submenu');
        const activeSubmenuItem = submenu ? submenu.querySelector('.sidebar-submenu-item.active') : null;
        
        if (activeSubmenuItem && submenu && !submenu.classList.contains('show')) {
            submenu.classList.add('show');
        }
    }
}

/**
 * Öğrenci hızlı arama formunu etkinleştir
 */
function initOgrenciHizliArama() {
    const form = document.getElementById('ogrenciHizliAramaForm');
    const input = document.getElementById('ogrenciNo');
    
    if (!form || !input) return;
    
    // Enter tuşuna basıldığında sayfayı otomatik yenileyelim
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            form.submit();
        }
    });
    
    // Input'a otomatik focus ver
    setTimeout(() => {
        input.focus();
    }, 500);
}
