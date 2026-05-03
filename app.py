import streamlit as st
import pandas as pd
from datetime import time, datetime
import calendar
import io

# --- LOGIKA PERHITUNGAN TETAP SAMA ---
def hitung_durasi_keterlambatan(teks, tanggal, bulan, tahun):
    try:
        # Fungsi ini sekarang menggunakan bulan dan tahun yang dinamis sesuai input
        hari_ke = calendar.weekday(tahun, bulan, tanggal)
        if hari_ke == 6: return None 
    except: return None
    if pd.isna(teks) or str(teks).strip() in ["", "-"]: return 480
    jam_clean = str(teks).strip()[:5]
    try:
        if ":" in jam_clean:
            jam_dt = pd.to_datetime(jam_clean, format='%H:%M').time()
            jadwal_masuk = time(8, 0)
            if jam_dt > jadwal_masuk:
                return (jam_dt.hour * 60 + jam_dt.minute) - (8 * 60)
            return 0
        return 480
    except: return 480

# --- TAMPILAN WEB ---
st.set_page_config(page_title="JAVA Attend", page_icon="🌐")

st.title("🌐 JAVA Attend")
st.subheader("Javanet Attendance Log Processor")

# --- MODIFIKASI: PEMILIHAN PERIODE OTOMATIS & MANUAL ---
now = datetime.now()
col1, col2 = st.columns(2)

with col1:
    bulan_pilihan = st.selectbox(
        "Pilih Bulan Laporan", 
        range(1, 13), 
        index=now.month - 1, 
        format_func=lambda x: calendar.month_name[x]
    )

with col2:
    tahun_pilihan = st.number_input("Pilih Tahun", min_value=2024, max_value=2030, value=now.year)

uploaded_file = st.file_uploader("Pilih file log fingerprint (.xls / .xlsx)", type=["xls", "xlsx"])

if uploaded_file is not None:
    if st.button("Proses Sekarang"):
        try:
            # Membaca file yang diupload
            df_raw = pd.read_excel(uploaded_file, sheet_name='Lap. Log Absen', header=None)
            
            data_rekap = []
            for i in range(4, len(df_raw), 2):
                nama_karyawan = df_raw.iloc[i, 10] 
                if pd.isna(nama_karyawan): continue
                log_absensi = df_raw.iloc[i+1, 0:31] 
                entry = {'Nama Karyawan': nama_karyawan}
                total = 0
                for idx, jam_str in enumerate(log_absensi):
                    tgl = idx + 1
                    # Menggunakan variabel bulan dan tahun pilihan user
                    menit = hitung_durasi_keterlambatan(jam_str, tgl, bulan_pilihan, tahun_pilihan)
                    entry[tgl] = menit
                    if menit is not None: total += menit
                entry['Total Menit'] = total
                data_rekap.append(entry)

            report_final = pd.DataFrame(data_rekap)
            
            # Konversi ke Excel di memori (untuk didownload)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                report_final.to_excel(writer, index=False, sheet_name='Rekap')
            
            st.success(f"Berhasil diproses untuk periode {calendar.month_name[bulan_pilihan]} {tahun_pilihan}!")
            st.download_button(
                label="📥 Download Hasil Rekap",
                data=output.getvalue(),
                file_name=f"REKAP_JAVA_ATTEND_{calendar.month_name[bulan_pilihan]}_{tahun_pilihan}.xlsx",
                mime="application/vnd.ms-excel"
            )
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
