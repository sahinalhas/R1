// User types
export interface User {
  id: number;
  email: string;
  tam_ad: string;
}

export interface LoginResponse {
  success: boolean;
  data?: {
    token: string;
    user: User;
  };
  error?: string;
}

// Student types
export interface Student {
  id: number;
  numara: string;
  ad: string;
  soyad: string;
  tam_ad: string;
  sinif: string;
  cinsiyet: string;
  telefon?: string;
  eposta?: string;
  genel_ilerleme: number;
}

// Meeting types
export interface Meeting {
  id: number;
  ogrenci_id?: number;
  tarih: string;
  baslangic_saati: string;
  bitis_saati: string;
  gorusulen_kisi: string;
  kisi_rolu?: string;
  yakinlik_derecesi?: string;
  gorusme_konusu: string;
  calisma_alani?: string;
  ozet?: string;
}

// Activity types
export interface Activity {
  id: number;
  etkinlik_tarihi: string;
  calisma_yontemi: string;
  aciklama: string;
  hedef_turu: string;
  faaliyet_turu: string;
  ogretmen_sayisi: number;
  veli_sayisi: number;
  erkek_ogrenci_sayisi: number;
  kiz_ogrenci_sayisi: number;
}

// Dashboard stats
export interface DashboardStats {
  ogrenci_sayisi: number;
  bu_ay_gorusme_sayisi: number;
  bu_ay_etkinlik_sayisi: number;
  ortalama_ilerleme: number;
}

// API Response wrapper
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}