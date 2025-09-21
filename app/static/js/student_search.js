// Öğrenci arama ve seçme işlemleri
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('studentSearchInput');
    const searchResults = document.getElementById('searchResults');
    const searchSpinner = document.getElementById('searchSpinner');
    const selectedStudents = document.getElementById('selectedStudents');
    const noStudentsMessage = document.getElementById('noStudentsMessage');
    
    let selectedStudentsArray = [];
    let searchTimeout;
    
    // Arama işlemi
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            searchResults.style.display = 'none';
            searchSpinner.style.display = 'none';
            return;
        }
        
        searchSpinner.style.display = 'block';
        
        searchTimeout = setTimeout(() => {
            fetch(`/ilk-kayit-formu/kayit-formu/ogrenci-ara?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    searchSpinner.style.display = 'none';
                    
                    if (data.length === 0) {
                        searchResults.innerHTML = '<div class="p-3 text-center text-muted">Sonuç bulunamadı</div>';
                    } else {
                        searchResults.innerHTML = '';
                        
                        data.forEach(student => {
                            // Zaten eklenmiş öğrencileri kontrol et
                            const isAlreadySelected = selectedStudentsArray.some(s => s.id === student.id);
                            if (isAlreadySelected) return;
                            
                            const item = document.createElement('div');
                            item.className = 'search-result-item';
                            
                            // Arama kriterine göre vurgulamaları yapalım
                            const searchLower = query.toLowerCase();
                            let namePart = `<span class="search-result-name">${student.tam_ad}</span>`;
                            let numberPart = `<span class="search-result-number">${student.numara}</span>`;
                            let classPart = `<span class="search-result-class">${student.sinif}</span>`;
                            
                            // Sınıf vurgulaması (tam eşleşme veya kısmi eşleşme varsa)
                            if (student.sinif.toLowerCase() === searchLower) {
                                // Tam eşleşme - daha belirgin vurgula
                                classPart = `<span class="search-result-class" style="background-color: #d3f9d8; padding: 2px 6px; border-radius: 4px; color: #2b8a3e; font-weight: bold;">${student.sinif}</span>`;
                            } else if (student.sinif.toLowerCase().includes(searchLower)) {
                                // Kısmi eşleşme
                                classPart = `<span class="search-result-class" style="background-color: #e3fafc; padding: 2px 6px; border-radius: 4px; color: #0c8599;">${student.sinif}</span>`;
                            }
                            
                            item.innerHTML = `
                                ${numberPart}
                                ${namePart}
                                ${classPart}
                            `;
                            
                            item.addEventListener('click', () => {
                                addStudentToSelection(student);
                                searchResults.style.display = 'none';
                                searchInput.value = '';
                            });
                            
                            searchResults.appendChild(item);
                        });
                    }
                    
                    searchResults.style.display = 'block';
                })
                .catch(error => {
                    console.error('Arama hatası:', error);
                    searchSpinner.style.display = 'none';
                    searchResults.innerHTML = '<div class="p-3 text-center text-danger">Arama sırasında bir hata oluştu</div>';
                    searchResults.style.display = 'block';
                });
        }, 300);
    });
    
    // Öğrenci seçme/ekleme
    function addStudentToSelection(student) {
        // Öğrenciyi zaten eklenmiş mi diye kontrol et
        if (selectedStudentsArray.some(s => s.id === student.id)) return;
        
        selectedStudentsArray.push(student);
        updateStudentDisplay();
    }
    
    // Öğrenci çıkarma
    function removeStudentFromSelection(studentId) {
        selectedStudentsArray = selectedStudentsArray.filter(s => s.id !== studentId);
        updateStudentDisplay();
    }
    
    // Öğrenci listesini güncelleme
    function updateStudentDisplay() {
        if (selectedStudentsArray.length === 0) {
            noStudentsMessage.style.display = 'flex';
            selectedStudents.innerHTML = '';
            return;
        }
        
        noStudentsMessage.style.display = 'none';
        selectedStudents.innerHTML = '';
        
        selectedStudentsArray.forEach(student => {
            const card = document.createElement('div');
            card.className = 'student-card';
            card.dataset.id = student.id;
            
            // Cinsiyet gösterimini düzenle - daha esnek kontrol
            // Cinsiyet gösterimini düzenle - daha esnek kontrol ve stil eklemeleri
            const erkekPatterns = ["e", "E", "erkek", "ERKEK", "Erkek", "1", 1];
            const genderDisplay = erkekPatterns.includes(student.cinsiyet) ? "Erkek" : "Kız";
            const genderClass = erkekPatterns.includes(student.cinsiyet) ? "student-gender-erkek" : "student-gender-kiz";
            
            card.innerHTML = `
                <button type="button" class="student-card-remove" data-id="${student.id}">
                    <i class="fas fa-times"></i>
                </button>
                <div class="student-card-header-simple">
                    <h6 class="student-card-name">${student.tam_ad}</h6>
                    <div class="student-card-number">${student.numara}</div>
                </div>
                <div class="student-card-details">
                    <div class="student-card-class">${student.sinif}</div>
                    <div class="student-card-gender ${genderClass}">${genderDisplay}</div>
                </div>
                <input type="hidden" name="students[]" value="${student.id}">
            `;
            
            // Kaldırma butonuna işlev ekle
            const removeBtn = card.querySelector('.student-card-remove');
            removeBtn.addEventListener('click', function() {
                removeStudentFromSelection(parseInt(this.dataset.id));
            });
            
            selectedStudents.appendChild(card);
        });
    }
    
    // Sayfa dışına tıklandığında arama sonuçlarını kapat
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
});