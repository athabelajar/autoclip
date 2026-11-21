# AutoClip + Claude: Panduan Singkat (Bahasa Indonesia)

Versi AutoClip ini bisa memakai **Anthropic Claude** sebagai AI untuk memilih dan memberi judul klip.

## Soal biaya

- **Aplikasinya gratis** (lisensi MIT) dan berjalan di komputer sendiri.
- **Pemakaian Claude API berbayar** per token, ditagih oleh Anthropic ke akun Console Anda.
  Langganan Claude.ai (Pro/Max) **tidak** bisa dipakai untuk API.
- Perkiraan kasar per video 1 jam: Haiku 5.5 sekitar $0,02, Sonnet 5.5 sekitar $0,40, Opus 5.5 sekitar $0,80.

## 1. Buat API key

1. Buka https://console.anthropic.com dan daftar/masuk.
2. Isi saldo (Billing), lalu buat key di **Settings → API Keys**. Key diawali `sk-ant-`.
3. Simpan key ini baik-baik. Jangan dibagikan dan jangan di-commit ke GitHub.

## 2a. Aplikasi desktop

Buka **Pengaturan → Penyedia & Model**, pilih **Anthropic**, tempel key, pilih model
(`claude-haiku-5-5` paling murah), lalu **Tes koneksi** dan **Simpan**.
Key disimpan di backend lokal, tidak dikirim ke tampilan web.

## 2b. Mode server / Docker / skrip

Salin `env.example` menjadi `.env`, lalu isi:

```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-haiku-5-5
CLAUDE_EFFORT=low
```

`CLAUDE_EFFORT` mengatur seberapa keras Claude berpikir: `low` paling hemat, `high` lebih teliti.

## Kalau ada masalah

| Pesan | Artinya |
| --- | --- |
| 401 / authentication | Key salah atau sudah dihapus |
| 402 / credit / billing | Saldo Console habis |
| 429 / rate limit | Terlalu banyak permintaan; aplikasi otomatis mencoba lagi |
| 529 / overloaded | Server Anthropic sedang sibuk; coba lagi sebentar |
