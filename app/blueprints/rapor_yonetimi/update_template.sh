#!/bin/bash

# Bu script rapor şablonunu günceller

# Şablondaki tüm "rapor.rapor_verileri" ifadelerini "rapor_verileri" olarak değiştirir
sed -i 's/rapor\.rapor_verileri/rapor_verileri/g' app/blueprints/rapor_yonetimi/templates/rapor_yonetimi/rapor_detay.html