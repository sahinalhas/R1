/**
 * YKS Çalışma Programı Takip Sistemi - Grafikler
 */

// Sayfa yüklendiğinde grafikleri başlat
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
});

/**
 * Tüm grafikleri başlat
 */
function initializeCharts() {
    // Ders İlerleme Grafiği
    initDersIlerlemeChart();
    
    // Deneme Sonuçları Grafiği
    initDenemeSonucChart();
    
    // Deneme TYT Netler Grafiği
    initTytNetlerChart();
    
    // Genel İlerleme Grafiği
    initGenelIlerlemeChart();
}

/**
 * Ders İlerleme Grafiği
 */
function initDersIlerlemeChart() {
    const chartElement = document.getElementById('dersIlerlemeChart');
    if (!chartElement) return;
    
    // Veri yapısını kontrol et
    if (typeof dersAdi === 'undefined' || typeof ilerlemeYuzde === 'undefined') return;
    
    // Grafiği oluştur
    new Chart(chartElement, {
        type: 'bar',
        data: {
            labels: dersAdi,
            datasets: [{
                label: 'Tamamlanma Yüzdesi (%)',
                data: ilerlemeYuzde,
                backgroundColor: 'rgba(65, 105, 225, 0.6)',
                borderColor: 'rgba(65, 105, 225, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Deneme Sonuçları Grafiği
 */
function initDenemeSonucChart() {
    const chartElement = document.getElementById('denemeSonucChart');
    if (!chartElement) return;
    
    // Veri yapısını kontrol et
    if (typeof tarihler === 'undefined' || typeof tyt_puanlar === 'undefined' || 
        typeof say_puanlar === 'undefined' || typeof ea_puanlar === 'undefined' || 
        typeof soz_puanlar === 'undefined') return;
    
    // Grafiği oluştur
    new Chart(chartElement, {
        type: 'line',
        data: {
            labels: tarihler,
            datasets: [
                {
                    label: 'TYT',
                    data: tyt_puanlar,
                    borderColor: 'rgba(65, 105, 225, 1)',
                    backgroundColor: 'rgba(65, 105, 225, 0.2)',
                    tension: 0.1,
                    fill: false
                },
                {
                    label: 'SAY',
                    data: say_puanlar,
                    borderColor: 'rgba(60, 179, 113, 1)',
                    backgroundColor: 'rgba(60, 179, 113, 0.2)',
                    tension: 0.1,
                    fill: false
                },
                {
                    label: 'EA',
                    data: ea_puanlar,
                    borderColor: 'rgba(255, 127, 80, 1)',
                    backgroundColor: 'rgba(255, 127, 80, 0.2)',
                    tension: 0.1,
                    fill: false
                },
                {
                    label: 'SÖZ',
                    data: soz_puanlar,
                    borderColor: 'rgba(147, 112, 219, 1)',
                    backgroundColor: 'rgba(147, 112, 219, 0.2)',
                    tension: 0.1,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    min: function() {
                        // Minimum değeri bul ve biraz altından başla
                        const allValues = [].concat(
                            tyt_puanlar, say_puanlar, ea_puanlar, soz_puanlar
                        ).filter(val => val !== null && val !== undefined);
                        
                        if (allValues.length === 0) return 0;
                        const min = Math.min(...allValues);
                        return Math.max(0, Math.floor(min / 50) * 50); // 50'nin katlarına yuvarla
                    }(),
                    max: function() {
                        // Maximum değeri bul ve biraz üstünden bitir
                        const allValues = [].concat(
                            tyt_puanlar, say_puanlar, ea_puanlar, soz_puanlar
                        ).filter(val => val !== null && val !== undefined);
                        
                        if (allValues.length === 0) return 500;
                        const max = Math.max(...allValues);
                        return Math.min(600, Math.ceil(max / 50) * 50 + 50); // 50'nin katlarına yuvarla
                    }()
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            }
        }
    });
}

/**
 * TYT Netleri Grafiği
 */
function initTytNetlerChart() {
    const chartElement = document.getElementById('tytNetlerChart');
    if (!chartElement) return;
    
    // Veri yapısını kontrol et
    if (typeof tarihler === 'undefined' || typeof tyt_turkce_netler === 'undefined' || 
        typeof tyt_sosyal_netler === 'undefined' || typeof tyt_matematik_netler === 'undefined' || 
        typeof tyt_fen_netler === 'undefined') return;
    
    // Grafiği oluştur
    new Chart(chartElement, {
        type: 'line',
        data: {
            labels: tarihler,
            datasets: [
                {
                    label: 'Türkçe',
                    data: tyt_turkce_netler,
                    borderColor: 'rgba(255, 99, 71, 1)',
                    backgroundColor: 'rgba(255, 99, 71, 0.2)',
                    tension: 0.1,
                    fill: false
                },
                {
                    label: 'Sosyal',
                    data: tyt_sosyal_netler,
                    borderColor: 'rgba(255, 165, 0, 1)',
                    backgroundColor: 'rgba(255, 165, 0, 0.2)',
                    tension: 0.1,
                    fill: false
                },
                {
                    label: 'Matematik',
                    data: tyt_matematik_netler,
                    borderColor: 'rgba(65, 105, 225, 1)',
                    backgroundColor: 'rgba(65, 105, 225, 0.2)',
                    tension: 0.1,
                    fill: false
                },
                {
                    label: 'Fen',
                    data: tyt_fen_netler,
                    borderColor: 'rgba(60, 179, 113, 1)',
                    backgroundColor: 'rgba(60, 179, 113, 0.2)',
                    tension: 0.1,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 40
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + ' net';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Genel İlerleme Grafiği (Anasayfa için)
 */
function initGenelIlerlemeChart() {
    const chartElement = document.getElementById('genelIlerlemeChart');
    if (!chartElement) return;
    
    // Veri yapısını kontrol et
    if (typeof genelIlerlemeData === 'undefined') return;
    
    // Verileri hazırla
    const labels = genelIlerlemeData.map(item => item.etiket);
    const data = genelIlerlemeData.map(item => item.deger);
    const colors = genelIlerlemeData.map(item => item.renk || 'rgba(65, 105, 225, 0.6)');
    
    // Grafiği oluştur
    new Chart(chartElement, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(color => color.replace('0.6', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const label = context.label;
                            return label + ': ' + value + '%';
                        }
                    }
                }
            }
        }
    });
}
