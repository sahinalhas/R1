/**
 * YKS Çalışma Programı Takip Sistemi - Chart.js Tema Ayarları
 * Modern ve zarif grafik temaları
 */

// Chart.js için ortak stil ayarları
const chartCommonOptions = {
  // Renk paleti
  colors: {
    primary: 'rgba(59, 130, 246, 0.8)', // Mavi
    secondary: 'rgba(16, 185, 129, 0.8)', // Yeşil
    warning: 'rgba(245, 158, 11, 0.8)', // Turuncu
    danger: 'rgba(239, 68, 68, 0.8)', // Kırmızı
    info: 'rgba(6, 182, 212, 0.8)', // Turkuaz
    purple: 'rgba(168, 85, 247, 0.8)', // Mor
    gray: 'rgba(107, 114, 128, 0.8)', // Gri
    light: 'rgba(243, 244, 246, 0.8)' // Açık Gri
  },

  // Tema ayarları
  getTheme: function(isDarkMode = false) {
    return {
      fontFamily: "'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
      fontSize: 12,
      fontColor: isDarkMode ? '#e5e7eb' : '#374151',
      gridColor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)',
      borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
      backgroundColor: isDarkMode ? '#1f2937' : '#ffffff',
      tooltipBackgroundColor: isDarkMode ? '#374151' : '#ffffff',
      tooltipBorderColor: isDarkMode ? '#4b5563' : '#e5e7eb',
      animationDuration: 750
    };
  }
};

/**
 * Chart.js global ayarları
 */
function setupChartGlobalDefaults(isDarkMode = false) {
  const theme = chartCommonOptions.getTheme(isDarkMode);
  
  Chart.defaults.font.family = theme.fontFamily;
  Chart.defaults.font.size = theme.fontSize;
  Chart.defaults.color = theme.fontColor;
  
  Chart.defaults.animation.duration = theme.animationDuration;
  Chart.defaults.animation.easing = 'easeOutQuart';
  
  // Tooltip Ayarları
  Chart.defaults.plugins.tooltip.backgroundColor = theme.tooltipBackgroundColor;
  Chart.defaults.plugins.tooltip.titleColor = theme.fontColor;
  Chart.defaults.plugins.tooltip.bodyColor = theme.fontColor;
  Chart.defaults.plugins.tooltip.borderColor = theme.tooltipBorderColor;
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.cornerRadius = 6;
  Chart.defaults.plugins.tooltip.displayColors = true;
  Chart.defaults.plugins.tooltip.boxPadding = 4;
  Chart.defaults.plugins.tooltip.usePointStyle = true;
  Chart.defaults.plugins.tooltip.bodyFont = {
    family: theme.fontFamily,
    size: theme.fontSize
  };
  Chart.defaults.plugins.tooltip.titleFont = {
    family: theme.fontFamily,
    size: theme.fontSize
  };
  
  // Ölçek Ayarları
  Chart.defaults.scales.linear.grid.color = theme.gridColor;
  Chart.defaults.scales.linear.grid.lineWidth = 1;
  Chart.defaults.scales.linear.border.color = theme.borderColor;
  
  Chart.defaults.scales.category.grid.color = theme.gridColor;
  Chart.defaults.scales.category.grid.lineWidth = 1;
  Chart.defaults.scales.category.border.color = theme.borderColor;
  
  // Legend Ayarları
  Chart.defaults.plugins.legend.labels.font = {
    family: theme.fontFamily,
    size: theme.fontSize
  };
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.legend.labels.boxWidth = 8;
  Chart.defaults.plugins.legend.labels.padding = 15;
}

/**
 * İlerleme grafiği ayarları
 */
function getProgressChartConfig(labels, data, isDarkMode = false) {
  const theme = chartCommonOptions.getTheme(isDarkMode);
  
  return {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Tamamlama Yüzdesi',
        data: data,
        fill: {
          target: 'origin',
          above: 'rgba(59, 130, 246, 0.1)',
        },
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderColor: chartCommonOptions.colors.primary,
        borderWidth: 2,
        tension: 0.4,
        pointBackgroundColor: '#ffffff',
        pointBorderColor: chartCommonOptions.colors.primary,
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: '#ffffff',
        pointHoverBorderColor: chartCommonOptions.colors.primary,
        pointHoverBorderWidth: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: {
            display: false,
            drawBorder: false
          },
          ticks: {
            padding: 10
          }
        },
        y: {
          grid: {
            color: theme.gridColor,
            borderDash: [3, 3],
            drawBorder: false,
            zeroLineColor: theme.gridColor
          },
          ticks: {
            padding: 10,
            stepSize: 20,
            callback: function(value) {
              return value + '%';
            }
          },
          suggestedMin: 0,
          suggestedMax: 100
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return context.parsed.y + '%';
            }
          }
        }
      },
      interaction: {
        mode: 'index',
        intersect: false
      },
      elements: {
        line: {
          tension: 0.4
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    }
  };
}

/**
 * Deneme sonuçları grafiği ayarları
 */
function getDenemeSonucChartConfig(labels, tytData, aytData, isDarkMode = false) {
  const theme = chartCommonOptions.getTheme(isDarkMode);
  
  return {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'TYT Puanı',
          data: tytData,
          backgroundColor: chartCommonOptions.colors.primary,
          borderColor: chartCommonOptions.colors.primary,
          borderWidth: 1,
          borderRadius: 4,
          barPercentage: 0.6,
          categoryPercentage: 0.7
        },
        {
          label: 'AYT Puanı',
          data: aytData,
          backgroundColor: chartCommonOptions.colors.secondary,
          borderColor: chartCommonOptions.colors.secondary,
          borderWidth: 1,
          borderRadius: 4,
          barPercentage: 0.6,
          categoryPercentage: 0.7
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: {
            display: false,
            drawBorder: false
          },
          ticks: {
            padding: 10
          }
        },
        y: {
          grid: {
            color: theme.gridColor,
            borderDash: [3, 3],
            drawBorder: false
          },
          ticks: {
            padding: 10
          }
        }
      },
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: {
            boxWidth: 12,
            useBorderRadius: true,
            borderRadius: 2
          }
        },
      },
      interaction: {
        mode: 'index',
        intersect: false
      },
      animation: {
        duration: 1000
      }
    }
  };
}

/**
 * Ders Dağılımı Pasta Grafiği Ayarları
 */
function getDersDagilimiChartConfig(labels, data, isDarkMode = false) {
  const theme = chartCommonOptions.getTheme(isDarkMode);
  
  // Pastel renkler hazırla (8 ders için)
  const pastelColors = [
    chartCommonOptions.colors.primary,
    chartCommonOptions.colors.secondary,
    chartCommonOptions.colors.warning,
    chartCommonOptions.colors.purple,
    chartCommonOptions.colors.danger,
    chartCommonOptions.colors.info,
    'rgba(236, 72, 153, 0.8)', // Pembe
    'rgba(124, 58, 237, 0.8)' // Mor
  ];
  
  return {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: pastelColors,
        borderColor: theme.backgroundColor,
        borderWidth: 2,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            boxWidth: 12,
            padding: 15
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.raw || 0;
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
              return `${label}: ${percentage}% (${value} saat)`;
            }
          }
        }
      },
      cutout: '60%',
      animation: {
        animateRotate: true,
        animateScale: true
      }
    }
  };
}

/**
 * TYT Netleri Radar Grafiği Ayarları
 */
function getTytNetlerChartConfig(labels, currentData, avgData, isDarkMode = false) {
  const theme = chartCommonOptions.getTheme(isDarkMode);
  
  return {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Son Deneme',
          data: currentData,
          backgroundColor: 'rgba(59, 130, 246, 0.2)',
          borderColor: chartCommonOptions.colors.primary,
          borderWidth: 2,
          pointBackgroundColor: chartCommonOptions.colors.primary,
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: chartCommonOptions.colors.primary,
          pointRadius: 4
        },
        {
          label: 'Ortalama Netler',
          data: avgData,
          backgroundColor: 'rgba(16, 185, 129, 0.2)',
          borderColor: chartCommonOptions.colors.secondary,
          borderWidth: 2,
          pointBackgroundColor: chartCommonOptions.colors.secondary, 
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: chartCommonOptions.colors.secondary,
          pointRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: {
            color: theme.gridColor
          },
          grid: {
            color: theme.gridColor
          },
          pointLabels: {
            font: {
              size: 12
            }
          },
          ticks: {
            backdropColor: 'transparent',
            font: {
              size: 10
            }
          }
        }
      },
      plugins: {
        legend: {
          position: 'top',
          align: 'center'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return context.dataset.label + ': ' + context.raw + ' net';
            }
          }
        }
      },
      elements: {
        line: {
          tension: 0.1
        }
      }
    }
  };
}

// Grafik temalarını güncelle
function updateChartThemes() {
  // Tüm grafikleri bul
  const charts = Object.values(Chart.instances);
  
  if (charts.length === 0) return;
  
  // Her grafik için tema ayarlarını güncelle
  const theme = chartCommonOptions.getTheme(false);
  
  // Global ayarları güncelle
  setupChartGlobalDefaults(false);
  
  // Her grafiği güncelle
  charts.forEach(chart => {
    // Ölçek renkleri güncelle
    if (chart.config && chart.config.options && chart.config.options.scales) {
      if (chart.config.options.scales.x) {
        // Gerekli grid ve border özelliklerini kontrol et
        if (!chart.config.options.scales.x.grid) chart.config.options.scales.x.grid = {};
        if (!chart.config.options.scales.x.border) chart.config.options.scales.x.border = {};
        
        chart.config.options.scales.x.grid.color = theme.gridColor;
        chart.config.options.scales.x.border.color = theme.borderColor;
      }
      if (chart.config.options.scales.y) {
        // Gerekli grid ve border özelliklerini kontrol et
        if (!chart.config.options.scales.y.grid) chart.config.options.scales.y.grid = {};
        if (!chart.config.options.scales.y.border) chart.config.options.scales.y.border = {};
        
        chart.config.options.scales.y.grid.color = theme.gridColor;
        chart.config.options.scales.y.border.color = theme.borderColor;
      }
      if (chart.config.options.scales.r) {
        // Gerekli grid ve angleLines özelliklerini kontrol et
        if (!chart.config.options.scales.r.grid) chart.config.options.scales.r.grid = {};
        if (!chart.config.options.scales.r.angleLines) chart.config.options.scales.r.angleLines = {};
        
        chart.config.options.scales.r.grid.color = theme.gridColor;
        chart.config.options.scales.r.angleLines.color = theme.gridColor;
      }
    }
    
    // Font renklerini güncelle
    if (chart.config && chart.config.options) {
      if (!chart.config.options.plugins) chart.config.options.plugins = {};
      if (!chart.config.options.plugins.tooltip) chart.config.options.plugins.tooltip = {};
      
      chart.config.options.plugins.tooltip.backgroundColor = theme.tooltipBackgroundColor;
      chart.config.options.plugins.tooltip.borderColor = theme.tooltipBorderColor;
      chart.config.options.plugins.tooltip.titleColor = theme.fontColor;
      chart.config.options.plugins.tooltip.bodyColor = theme.fontColor;
    }
    
    // Grafiği yeniden çiz
    chart.update();
  });
}

// Sayfa yüklendiğinde varsayılan grafik ayarlarını belirle
document.addEventListener('DOMContentLoaded', function() {
  setupChartGlobalDefaults(false);
});