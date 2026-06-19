# Automata Simulator
Tugas Teori Bahasa dan Automata

Program simulasi automata berbasis Web (FastAPI + HTML/CSS/JS) yang mengimplementasikan 4 fitur utama:

| Fitur | Keterangan | Algoritma |
|-------|-----------|-----------|
| 1 | Simulasi DFA | Deterministik step-by-step |
| 2 | Regex -> NFA | Thompson Construction |
| 3 | Minimasi DFA | Table-Filling (Myhill-Nerode) |
| 4 | Ekuivalensi DFA | Simultaneous State Traversal via BFS |

---

## Cara Menjalankan

```bash
# 1. Masuk ke folder project
cd automata_simulator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Jalankan aplikasi
python main.py

# Aplikasi akan membuka browser secara otomatis ke http://127.0.0.1:8000
```

---

## Struktur Folder

```
automata_simulator/
├── main.py                  # Entry point (FastAPI server)
├── requirements.txt         # Dependencies (fastapi, uvicorn, dll)
├── README.md
├── api/
│   └── routes/              # Endpoint API untuk DFA, NFA, Minimasi, Ekuivalensi
├── core/
│   ├── dfa.py               # Algoritma DFA (Simulasi, Minimasi, Ekuivalensi)
│   └── nfa.py               # Algoritma NFA (Regex -> NFA Thompson)
├── static/
│   ├── css/                 # Styling frontend (main.css)
│   └── js/                  # Modul frontend (app.js, dfa_panel.js, dll)
├── templates/
│   └── index.html           # File utama tampilan Web (HTML)
├── utils/
│   ├── graph_builder.py     # Konversi automata ke graph Cytoscape
│   └── parser.py            # Parsing input form DFA/NFA
└── tests/
    └── test_all.py          # Unit test fungsi logika automata
```

---

## Panduan Penggunaan

### Fitur 1 - Simulasi DFA
1. Masukkan Himpunan State (pisahkan dengan koma): q0,q1,q2
2. Masukkan Alphabet (pisahkan dengan koma): a,b
3. Masukkan State Awal: q0
4. Masukkan Accepting State: q2
5. Masukkan Fungsi Transisi (sumber,simbol,tujuan per baris): q0,a,q1
6. Klik Draw Diagram untuk melihat visualisasi
7. Masukkan string dan klik Run untuk menjalankan simulasi string

### Fitur 2 - Regex -> NFA
Operator yang didukung:
- | : Union (a|b = a atau b)
- * : Kleene Star (a* = nol atau lebih a)
- + : One or More (a+ = satu atau lebih a)
- ? : Zero or One (a? = nol atau satu a)
- (): Pengelompokan

### Fitur 3 - Minimasi DFA
Masukkan DFA dan klik Minimize DFA. Hasil menampilkan:
- Log terminal berisi langkah-langkah pengurangan state
- Mapping penggantian state lama ke baru
- Diagram DFA awal dan diagram DFA hasil minimasi

### Fitur 4 - Ekuivalensi DFA
Masukkan dua DFA dan klik Check Equivalence. Jika tidak ekuivalen, sistem akan menampilkan log beserta counterexample string yang membedakan keduanya, beserta visualisasi masing-masing DFA.
