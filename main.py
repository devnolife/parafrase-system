#!/usr/bin/env python3
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
            print("\n🏆 Menjalankan sistem lengkap...")
            # Import and run the integrated system
            from integrated_smart_paraphrase_system import main as integrated_main
            integrated_main()
            
        elif choice == "2":
            sub_choice = input("Pilih deteksi (1: Online, 2: Pattern): ").strip()
            if sub_choice == "1":
                from plagiarism_detector import main as detector_main
                detector_main()
            else:
                from smart_plagiarism_checker import main as checker_main
                checker_main()
                
        elif choice == "3":
            print("\n🤖 Menjalankan paraphraser...")
            from ultimate_hybrid_paraphraser import main as paraphraser_main
            paraphraser_main()
            
        else:
            print("❌ Pilihan tidak valid")
            
    except KeyboardInterrupt:
        print("\n👋 Program dihentikan")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
