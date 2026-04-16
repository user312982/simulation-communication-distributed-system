Proyek simulasi Sistem Terdistribusi ini berfokus pada visualisasi dan perbandingan dua model komunikasi antar-node: *Request-Response* dan *Publish-Subscribe*. Inti lalu lintas pesan dalam simulasi ini secara nyata digerakkan oleh protokol **MQTT** menggunakan broker **Eclipse Mosquitto** yang berjalan di dalam **Docker**, serta diintegrasikan melalui *library* Python `paho-mqtt`. Keseluruhan sistem dan antarmuka interaktifnya dibangun menggunakan **Python** (dengan **Tkinter** untuk GUI), dan dilengkapi dengan mekanisme *fallback* ke mode *In-Memory* secara otomatis apabila *broker* MQTT tidak tersedia.

dengan selalu memenuhi capaian dibawah ini:

Instruksi Tugas: Simulasi Interaktif Model Komunikasi dalam Sistem Terdistribusi
Tujuan:
 Untuk mendapatkan pemahaman praktis tentang dampak dari model 
komunikasi yang berbeda terhadap aliran data dan interaksi dalam sistem 
terdistribusi, Anda diwajibkan untuk membuat simulasi interaktif 
menggunakan pemrograman ataupun simulasi.
Instruksi:
Membuat
 simulasi Model Komunikasi: Pilih setidaknya dua model komunikasi yang 
berbeda, seperti Request-Response, Publish-Subscribe, Message Passing, 
atau Remote Procedure Call (RPC), hal ini bertujuan untuk memperlihatkan
 cara kerja  sistem dalam simulasi Anda.
Komponen 
Sistem: Definisikan komponen-komponen utama dari sistem terdistribusi 
Anda. Ini bisa termasuk node, perangkat, server, atau entitas yang 
relevan dalam proses komunikasi.
Implementasi Logika
 Interaksi: Tulis kode yang menggambarkan logika interaksi dengan akurat
 untuk setiap model komunikasi. Tentukan bagaimana pesan dikirimkan, 
diterima, dan diproses dalam sistem simulasi Anda.
Representasi
 Visual: Buat representasi visual dari sistem terdistribusi dan proses 
komunikasinya. Ini bisa melibatkan antarmuka grafis, animasi, diagram, 
atau visualisasi apa pun yang membantu pengguna memahami aliran data.
Interaksi
 Pengguna: Desain elemen-elemen yang memungkinkan pengguna berinteraksi 
dengan simulasi. Ini bisa mencakup tombol, bidang input, slider, atau 
cara lain untuk memicu tindakan komunikasi dan mengamati respons sistem.
Mekanisme
 Perbandingan: Implementasikan cara untuk pengguna untuk membandingkan 
perilaku model komunikasi yang berbeda. Pertimbangkan menampilkan metrik
 seperti, urutan pesan, throughput sistem, atau parameter lain yang 
relevan.
Dokumentasi dan Penjelasan: Berikan 
dokumentasi yang jelas yang menyertai simulasi Anda dan menjelaskan 
tujuannya, model komunikasi yang dipilih, logika simulasi, instruksi 
interaksi pengguna, dan cara menginterpretasi hasil simulasi.
Tools dan Bahasa Pemrograman:
Anda
 bebas memilih bahasa pemrograman dan alat simulasi yang Anda kuasai. 
Pilihan bisa mencakup Python (dengan pustaka seperti Tkinter), alat 
pengembangan web, perangkat lunak simulasi, atau platform lain yang 
cocok.


Kriteria Penilaian:

Tugas Anda akan dinilai berdasarkan kriteria-kriteria berikut:
Akurasi implementasi model komunikasi.
Kualitas representasi visual dan desain interaksi pengguna.
Kekelaran dan kelengkapan dokumentasi yang menyertai.
Kedalaman analisis dalam membandingkan perilaku model komunikasi yang berbeda.
Kreativitas dan inovasi dalam mensimulasikan skenario dunia nyata.

Pemilihan Model Komunikasi
Peserta
 memilih dua atau lebih model komunikasi dan membenarkan pilihannya 
berdasarkan pemahaman yang jelas tentang karakteristiknya dan 
relevansinya terhadap tugas.

Komponen Sistem
Peserta
 mendefinisikan dan menjelaskan komponen-komponen kunci dari sistem 
terdistribusi, memperlihatkan pemahaman yang jelas tentang bagaimana 
komponen-komponen ini berinteraksi dalam simulasi.

Implementasi Logika Interaksi
Peserta
 secara akurat mengimplementasikan logika interaksi untuk setiap model 
komunikasi, memperlihatkan bagaimana pesan dikirimkan, diterima, dan 
diproses dalam simulasi.

Representasi Visual
Peserta
 menciptakan representasi visual yang menarik dan informatif tentang 
sistem terdistribusi dan proses komunikasinya, meningkatkan pemahaman.

Desain Interaksi Pengguna
Peserta merancang elemen interaksi pengguna yang intuitif, terdesain dengan baik, dan efektif memfasilitasi proses simulasi.

Mekanisme Perbandingan
Peserta
 mengimplementasikan mekanisme perbandingan yang efektif untuk 
membandingkan perilaku model komunikasi yang berbeda, menyediakan metrik
 dan wawasan yang jelas untuk analisis.

Dokumentasi dan Penjelasan
Peserta
 menyediakan dokumentasi yang jelas dan komprehensif yang menjelaskan 
tujuan simulasi, model komunikasi, interaksi pengguna, dan cara 

Kreativitas dan Relevansi Dunia Nyata
Peserta
 menunjukkan kreativitas luar biasa dengan memasukkan skenario atau 
tantangan dunia nyata, meningkatkan relevansi dan kedalaman simulasi.