# cleanup_system.py
"""
System Cleanup and Organization Script
Organize the paraphrasing system files into proper structure
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

def create_clean_structure():
    """Create clean folder structure"""
    print("🗂️  CREATING CLEAN SYSTEM STRUCTURE")
    print("=" * 60)
    
    # Create directories
    directories = [
        "active_system",      # Current active files
        "archive",           # Old/deprecated files  
        "components",        # Individual components
        "tests",            # Test files
        "docs",             # Documentation
        "completed",        # Results folder
        "backups"           # Backups folder
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created: {directory}/")
    
    print("✅ Folder structure created!")

def categorize_files():
    """Categorize files based on their purpose and status"""
    
    file_categories = {
        "active_system": [
            "integrated_smart_paraphrase_system.py",  # MAIN SYSTEM
        ],
        
        "components": [
            "ultimate_hybrid_paraphraser.py",         # CORE ENGINE
            "smart_plagiarism_checker.py",            # PATTERN DETECTOR  
            "plagiarism_detector.py",                 # ONLINE DETECTOR
            "sinonim.json",                          # SYNONYM DATABASE
        ],
        
        "archive": [
            "paraphrase_system.py",                   # OLD SYSTEM
            "main_paraphrase_system.py",              # OLD MAIN
            "batch_word_paraphraser.py",              # BASIC SYSTEM
            "enhanced_paraphrase_system.py",          # INCOMPLETE
            "smart_hybrid_paraphraser.py",            # V2 HYBRID
            "balanced_hybrid_paraphraser.py",         # V2 BALANCED
            "turnitin_aware_paraphraser.py",          # SPECIFIC USE
            "smart_turnitin_detector.py",             # SPECIFIC DETECTOR
            "integrated_plagiarism_processor.py",     # PARTIAL INTEGRATION
            "enhanced_turnitin_gemini.py",            # OLD TURNITIN
            "lolos_turnitin.py",                     # OLD TURNITIN
            "anti_plagiat.py",                       # OLD SYSTEM
            "parsing.py",                            # UTILITY
        ],
        
        "tests": [
            "test.py",
            "quick_demo_system.py", 
            "test_completed_folder.py",
            "test_documents_priority.py",
        ],
        
        "docs": [
            "SYSTEM_ANALYSIS.md",
            "penjelasan.md",
        ]
    }
    
    return file_categories

def move_files_to_structure():
    """Move files to clean structure"""
    print("\n📁 ORGANIZING FILES INTO CLEAN STRUCTURE")
    print("=" * 60)
    
    categories = categorize_files()
    moved_count = 0
    
    for category, files in categories.items():
        print(f"\n📂 {category.upper()}:")
        
        for filename in files:
            if os.path.exists(filename):
                destination = os.path.join(category, filename)
                
                try:
                    # Copy instead of move to preserve originals
                    shutil.copy2(filename, destination)
                    print(f"  ✅ {filename} → {category}/")
                    moved_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to move {filename}: {e}")
            else:
                print(f"  ⚠️  File not found: {filename}")
    
    print(f"\n✅ Moved {moved_count} files to organized structure!")

def create_main_launcher():
    """Create simple main launcher script"""
    launcher_content = '''#!/usr/bin/env python3
# main.py - Simple Launcher for Paraphrase System
"""
🚀 SISTEM PARAFRASE TERINTEGRASI
Launcher untuk mengakses sistem parafrase lengkap
"""

import os
import sys

def main():
    print("🚀 SISTEM PARAFRASE TERINTEGRASI")
    print("=" * 50)
    print("🎯 Pilihan sistem yang tersedia:")
    print()
    print("1. 🏆 SISTEM LENGKAP (Recommended)")
    print("   → Deteksi online + pattern + parafrase + laporan")
    print("   → File: integrated_smart_paraphrase_system.py")
    print()
    print("2. 🔍 DETEKSI PLAGIARISME SAJA")
    print("   → Online detection: plagiarism_detector.py") 
    print("   → Pattern detection: smart_plagiarism_checker.py")
    print()
    print("3. 🤖 PARAFRASE SAJA")
    print("   → Core engine: ultimate_hybrid_paraphraser.py")
    print()
    
    try:
        choice = input("Pilih sistem (1-3) [default: 1]: ").strip() or "1"
        
        if choice == "1":
            print("\\n🏆 Menjalankan sistem lengkap...")
            exec(open("integrated_smart_paraphrase_system.py").read())
            
        elif choice == "2":
            sub_choice = input("Pilih deteksi (1: Online, 2: Pattern): ").strip()
            if sub_choice == "1":
                exec(open("plagiarism_detector.py").read())
            else:
                exec(open("smart_plagiarism_checker.py").read())
                
        elif choice == "3":
            print("\\n🤖 Menjalankan paraphraser...")
            exec(open("ultimate_hybrid_paraphraser.py").read())
            
        else:
            print("❌ Pilihan tidak valid")
            
    except KeyboardInterrupt:
        print("\\n👋 Program dihentikan")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
'''
    
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    print("\n🚀 Created main.py launcher!")

def create_readme():
    """Create comprehensive README"""
    readme_content = '''# 🚀 Sistem Parafrase Terintegrasi

## 📖 Deskripsi
Sistem parafrase lengkap dengan deteksi plagiarisme online dan offline, paraphrasing otomatis, dan manajemen dokumen.

## ⚡ Quick Start

### Metode 1: Launcher (Recommended)
```bash
python main.py
```

### Metode 2: Direct Run
```bash
python integrated_smart_paraphrase_system.py
```

## 📁 Struktur Folder

```
📂 parafrase-system/
├── 🚀 main.py                                    (Launcher)
├── 🏆 integrated_smart_paraphrase_system.py      (Sistem Utama)
├── 📂 components/                                (Komponen Inti)
│   ├── ultimate_hybrid_paraphraser.py
│   ├── smart_plagiarism_checker.py
│   ├── plagiarism_detector.py
│   └── sinonim.json
├── 📂 documents/                                 (Input Dokumen) 
├── 📂 completed/                                 (Hasil Akhir)
├── 📂 backups/                                   (Backup Otomatis)
├── 📂 archive/                                   (File Lama)
├── 📂 tests/                                     (File Testing)
└── 📂 docs/                                      (Dokumentasi)
```

## 🎯 Fitur Utama

- ✅ **Deteksi Plagiarisme Online** - Cek similarity dengan sumber internet
- ✅ **Analisis Pattern** - Deteksi pola akademik berbahaya
- ✅ **Parafrase AI** - Smart paraphrasing dengan multiple modes
- ✅ **Auto Backup** - Backup otomatis dokumen asli
- ✅ **Completed Folder** - Hasil siap compare (original vs paraphrased)
- ✅ **Comprehensive Reports** - Laporan JSON detail

## 🔧 Workflow

1. **Input**: Letakkan dokumen di `documents/` folder
2. **Detection**: Sistem scan plagiarisme online + pattern
3. **Analysis**: Identifikasi paragraf berisiko tinggi
4. **Paraphrasing**: Auto-parafrase bagian berbahaya
5. **Output**: Dokumen hasil + original di `completed/` folder

## 🏆 Sistem Utama

### `integrated_smart_paraphrase_system.py`
- Sistem terlengkap dan terbaru
- Menggabungkan semua fitur dalam satu workflow
- User-friendly dengan auto-selection
- Production ready

### Mode Processing:
- **Smart Mode**: Efficient, cost-optimized
- **Balanced Mode**: Best quality, balanced approach  
- **Aggressive Mode**: Maximum plagiarism reduction
- **Turnitin-Safe Mode**: Extra careful untuk Turnitin

## 📊 Komponen Pendukung

### `components/ultimate_hybrid_paraphraser.py`
- Core paraphrasing engine
- Local + AI hybrid approach
- Multiple operation modes
- Smart routing logic

### `components/plagiarism_detector.py`
- Online plagiarism detection
- Academic database integration
- Indonesian repository support
- Real-time similarity checking

### `components/smart_plagiarism_checker.py`
- Offline pattern analysis
- Academic writing pattern detection
- No internet required
- Fast local processing

## 📈 Output Files

### Completed Folder:
```
📂 completed/
├── 📄 DOCUMENT_ORIGINAL_20250807_123456.docx
└── 🤖 DOCUMENT_paraphrased_20250807_123456.docx
```

### Reports:
- `combined_analysis_[timestamp].json` - Analisis gabungan
- `paraphrase_report_[timestamp].json` - Detail paraphrasing
- `integrated_analysis_report_[timestamp].json` - Laporan lengkap

## 🔧 Requirements

```bash
pip install python-docx requests beautifulsoup4 google-generativeai python-dotenv
```

## 🚀 Usage Examples

### Basic Usage:
```bash
python main.py
# Select option 1 for full system
```

### Advanced Usage:
```python
from integrated_smart_paraphrase_system import IntegratedSmartParaphraseSystem

system = IntegratedSmartParaphraseSystem(mode='smart')
result = system.process_document_complete('document.docx', auto_paraphrase=True)
```

## 📋 File Archive

File-file lama tersimpan di folder `archive/` untuk referensi historical:
- `paraphrase_system.py` - Sistem original
- `main_paraphrase_system.py` - Versi lama  
- `smart_hybrid_paraphraser.py` - V2 hybrid
- Dan lainnya...

## 💡 Tips

1. **Letakkan dokumen utama** di folder `documents/` untuk prioritas tinggi
2. **Check completed folder** setelah processing untuk comparison
3. **Review highlights** pada dokumen hasil parafrase
4. **Simpan backup** yang dibuat otomatis sistem
5. **Gunakan mode aggressive** untuk dokumen dengan risiko tinggi

## ⚠️ Catatan

- File di `archive/` adalah versi lama dan tidak direkomendasikan
- Gunakan `integrated_smart_paraphrase_system.py` untuk semua kebutuhan
- Sistem memerlukan koneksi internet untuk deteksi online plagiarisme
- AI paraphrasing memerlukan Gemini API key (opsional)

---
📧 **Support**: Check SYSTEM_ANALYSIS.md untuk detail teknis lengkap
'''

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("📖 Created comprehensive README.md!")

def show_cleanup_summary():
    """Show cleanup summary"""
    print(f"\n" + "=" * 60)
    print("🎉 SYSTEM CLEANUP COMPLETED!")
    print("=" * 60)
    
    print("📊 SUMMARY:")
    print("✅ Created organized folder structure")
    print("✅ Categorized all files by purpose") 
    print("✅ Created main.py launcher")
    print("✅ Generated comprehensive README.md")
    print("✅ Documented system analysis")
    
    print(f"\n🎯 RECOMMENDED USAGE:")
    print("🚀 Run: python main.py")
    print("📖 Read: README.md")
    print("🔍 Analysis: SYSTEM_ANALYSIS.md")
    
    print(f"\n📁 CLEAN STRUCTURE:")
    print("🏆 Main System: integrated_smart_paraphrase_system.py")
    print("🔧 Components: components/ folder")
    print("📚 Archive: archive/ folder (old files)")
    print("📝 Tests: tests/ folder")
    print("📖 Docs: docs/ folder")

def main():
    """Main cleanup function"""
    print("🧹 PARAPHRASE SYSTEM CLEANUP & ORGANIZATION")
    print("🎯 Goal: Create clean, organized, user-friendly structure")
    print("=" * 60)
    
    try:
        # Step 1: Create structure
        create_clean_structure()
        
        # Step 2: Move files (copy to preserve originals)
        move_files_to_structure()
        
        # Step 3: Create launcher
        create_main_launcher()
        
        # Step 4: Create documentation
        create_readme()
        
        # Step 5: Show summary
        show_cleanup_summary()
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    main()