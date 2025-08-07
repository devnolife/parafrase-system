# ultimate_hybrid_paraphraser.py
"""
Ultimate Hybrid Paraphraser System - Consolidated All-in-One Solution
Combines: Smart Routing + Balanced Mode + Turnitin Detection + Advanced AI
Consolidated from: smart_hybrid_paraphraser.py + balanced_hybrid_paraphraser.py + main_paraphrase_system.py
Author: DevNoLife
Version: 3.0 - Ultimate Edition
"""

import os
import json
import re
import time
import random
from datetime import datetime
from pathlib import Path
import docx
from docx.shared import RGBColor
from docx.enum.text import WD_COLOR_INDEX
import shutil
from collections import defaultdict
import requests
import hashlib
from difflib import SequenceMatcher

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-dotenv not found. Install with: pip install python-dotenv")
    print("💡 Using system environment variables...")

# Gemini AI imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        # Fallback to requests-based API
        GEMINI_AVAILABLE = "requests"
    except:
        GEMINI_AVAILABLE = False

class UltimateHybridParaphraser:
    def __init__(self, synonym_file='sinonim.json', gemini_api_key=None, mode='smart'):
        print("🚀 Initializing Ultimate Hybrid Paraphraser v3.0...")
        print("🎯 Consolidated System: Smart + Balanced + Turnitin Detection")
        
        # Core configuration
        self.mode = mode  # 'smart', 'balanced', 'aggressive', 'turnitin_safe'
        self.synonym_file = synonym_file
        
        # Initialize local paraphrase system (from main_paraphrase_system.py)
        self._initialize_local_system()
        
        # Gemini AI configuration
        self.gemini_api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY") or "AIzaSyAABOimEqGMOJUnB302ARIB_tzUVxl5JDA"
        self.gemini_client = None
        self._initialize_gemini_client()
        
        # Cost tracking and caching
        self.cost_tracker = {
            'local_calls': 0,
            'ai_calls': 0,
            'ai_tokens_used': 0,
            'estimated_cost_usd': 0.0,
            'cache_hits': 0,
            'local_vs_ai_comparison': [],
            'turnitin_detections': 0,
            'mode_switches': 0
        }
        
        self.ai_cache = {}
        
        # Mode-specific configurations
        self.configs = {
            'smart': {
                'local_confidence_threshold': 0.25,
                'complexity_threshold': 0.7,
                'plagiarism_risk_threshold': 0.8,
                'min_paragraph_length': 40,
                'ai_usage_target': 0.3,  # 30% AI usage
                'cost_optimization': True
            },
            'balanced': {
                'local_confidence_threshold': 0.15,
                'complexity_threshold': 0.4,
                'plagiarism_risk_threshold': 0.6,
                'min_paragraph_length': 25,
                'ai_usage_target': 0.5,  # 50% AI usage
                'cost_optimization': False,
                'comparison_mode': True
            },
            'aggressive': {
                'local_confidence_threshold': 0.1,
                'complexity_threshold': 0.3,
                'plagiarism_risk_threshold': 0.5,
                'min_paragraph_length': 15,
                'ai_usage_target': 0.8,  # 80% AI usage
                'cost_optimization': False
            },
            'turnitin_safe': {
                'local_confidence_threshold': 0.35,
                'complexity_threshold': 0.8,
                'plagiarism_risk_threshold': 0.9,
                'min_paragraph_length': 50,
                'ai_usage_target': 0.6,  # 60% AI usage
                'turnitin_detection': True,
                'similarity_database_check': True
            }
        }
        
        self.current_config = self.configs.get(mode, self.configs['smart'])
        
        # Academic and priority patterns
        self.ai_priority_patterns = [
            r'menurut\s+\w+\s*\(\d{4}\)',
            r'berdasarkan\s+penelitian',
            r'definisi\s+\w+\s+adalah',
            r'konsep\s+\w+\s+merupakan',
            r'teori\s+\w+\s+menyatakan',
            r'sistem\s+informasi\s+adalah',
            r'penelitian\s+\w+',
            r'analisis\s+\w+',
            r'metode\s+\w+',
            r'hasil\s+\w+'
        ]
        
        # Turnitin detection patterns (for turnitin_safe mode)
        self.turnitin_risk_patterns = [
            r'penelitian\s+ini\s+menunjukkan',
            r'hasil\s+penelitian\s+menunjukkan',
            r'berdasarkan\s+hasil\s+analisis',
            r'dapat\s+disimpulkan\s+bahwa',
            r'menurut\s+\w+\s+\(\d{4}\)',
            r'definisi\s+\w+\s+adalah',
        ]
        
        print(f"✅ Mode: {mode.upper()}")
        print(f"✅ Local system: {len(self.synonyms)} synonyms, {len(self.phrase_replacements)} phrases")
        print(f"✅ Gemini AI: {'Configured' if self.gemini_client else 'Not available'}")
        print(f"✅ AI usage target: {self.current_config['ai_usage_target']*100:.0f}%")
        print("✅ Ultimate Hybrid Paraphraser ready!")
    
    def _initialize_local_system(self):
        """Initialize local paraphrasing system (from main_paraphrase_system.py)"""
        # Load synonyms
        self.synonyms = self.load_synonyms(self.synonym_file) if self.synonym_file else {}
        
        # Indonesian stopwords
        self.stopwords = {
            'yang', 'dan', 'di', 'ke', 'dari', 'dalam', 'untuk', 'pada',
            'dengan', 'adalah', 'akan', 'atau', 'juga', 'telah', 'dapat',
            'tidak', 'ada', 'ini', 'itu', 'saya', 'kami', 'kita', 'mereka',
            'sudah', 'belum', 'masih', 'sangat', 'sekali', 'lebih', 'bahwa',
            'karena', 'jika', 'maka', 'saja', 'hanya', 'bisa', 'semua', 'akan'
        }
        
        # Enhanced phrase replacements
        self.phrase_replacements = {
            'bertujuan untuk': ['dimaksudkan untuk', 'ditujukan untuk', 'bermaksud untuk', 'berupaya untuk'],
            'penelitian ini': ['studi ini', 'kajian ini', 'riset ini', 'investigasi ini'],
            'hasil penelitian': ['temuan riset', 'output kajian', 'hasil studi', 'temuan penelitian'],
            'dapat': ['mampu', 'bisa', 'sanggup', 'dapat'],
            'menggunakan': ['memakai', 'memanfaatkan', 'mempergunakan', 'mengaplikasikan'],
            'menunjukkan': ['memperlihatkan', 'mengindikasikan', 'mendemonstrasikan', 'membuktikan'],
            'mengurangi': ['menurunkan', 'meminimalisir', 'menimimalisasi', 'memperkecil'],
            'meningkatkan': ['menaikkan', 'memperbesar', 'mengoptimalkan', 'memaksimalkan'],
            'tingkat': ['level', 'taraf', 'derajat', 'kadar'],
            'sistem': ['metode', 'cara', 'teknik', 'prosedur', 'mekanisme'],
            'pendekatan': ['metode', 'cara', 'teknik', 'strategi'],
            'menghasilkan': ['menciptakan', 'membuat', 'memproduksi', 'melahirkan'],
            'mempertahankan': ['menjaga', 'memelihara', 'mempertahan', 'melestarikan'],
            'berbeda': ['tidak sama', 'berlainan', 'bervariasi', 'beragam'],
            'struktur': ['susunan', 'bentuk', 'format', 'konstruksi'],
            'pilihan': ['opsi', 'alternatif', 'seleksi', 'variasi'],
            'dokumen': ['naskah', 'berkas', 'file', 'manuscript'],
            'akademik': ['ilmiah', 'pendidikan', 'universitas', 'kampus'],
            'otomatis': ['automatik', 'mandiri', 'sendiri', 'auto'],
            'oleh karena itu': ['maka dari itu', 'dengan demikian', 'karena hal tersebut', 'akibatnya'],
            'selain itu': ['di samping itu', 'tambahan pula', 'lebih lanjut', 'furthermore'],
            'berdasarkan': ['menurut', 'berlandaskan', 'atas dasar', 'sesuai dengan'],
            'sehingga': ['yang mengakibatkan', 'sampai', 'hingga', 'alhasil'],
            'dengan cara': ['melalui', 'lewat', 'via', 'menggunakan cara'],
            'dalam hal': ['mengenai', 'terkait', 'berkaitan dengan', 'perihal'],
            'untuk': ['guna', 'bagi', 'demi', 'agar'],
        }
        
        # Sentence restructuring patterns
        self.restructuring_patterns = [
            (r'(\w+)\s+menggunakan\s+(\w+)', r'\2 digunakan oleh \1'),
            (r'(\w+)\s+mengembangkan\s+(\w+)', r'\2 dikembangkan oleh \1'),
            (r'(\w+)\s+menganalisis\s+(\w+)', r'\2 dianalisis oleh \1'),
            (r'^([A-Z]\w+)\s+ini\s+([a-z]\w+)', r'Pada \1 ini, \2'),
            (r'sangat\s+(\w+)', r'\1 sekali'),
            (r'lebih\s+(\w+)', r'\1 yang lebih'),
        ]
    
    def _initialize_gemini_client(self):
        """Initialize Gemini AI client"""
        if GEMINI_AVAILABLE == True:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
                self.api_method = 'genai'
                print(f"✅ Gemini client initialized (google-generativeai)")
            except Exception as e:
                print(f"⚠️  Google GenAI failed: {e}")
                self.gemini_client = None
                self.api_method = 'requests'
        elif GEMINI_AVAILABLE == "requests":
            self.api_method = 'requests'
            self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        else:
            self.gemini_client = None
            self.api_method = None
    
    def load_synonyms(self, filename):
        """Load synonym database from JSON file"""
        if not filename or not os.path.exists(filename):
            print("⚠️  No synonym file provided or file not found")
            return {}
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            synonyms = defaultdict(list)
            count = 0
            
            for word, info in data.items():
                if isinstance(info, dict) and 'sinonim' in info:
                    synonym_list = info['sinonim']
                    if isinstance(synonym_list, list) and len(synonym_list) > 0:
                        all_words = [word] + synonym_list
                        for w in all_words:
                            clean_w = w.lower().strip()
                            synonyms[clean_w] = [s.lower().strip() for s in all_words if s.lower().strip() != clean_w]
                        count += 1
            
            return dict(synonyms)
            
        except Exception as e:
            print(f"❌ Error loading synonyms: {e}")
            return {}
    
    def switch_mode(self, new_mode):
        """Dynamically switch processing mode"""
        if new_mode in self.configs:
            old_mode = self.mode
            self.mode = new_mode
            self.current_config = self.configs[new_mode]
            self.cost_tracker['mode_switches'] += 1
            print(f"🔄 Mode switched: {old_mode} → {new_mode}")
            return True
        else:
            print(f"❌ Invalid mode: {new_mode}. Available: {list(self.configs.keys())}")
            return False
    
    # ===== CORE PARAPHRASING METHODS (from main_paraphrase_system.py) =====
    
    def get_synonyms(self, word):
        """Get synonyms for a word"""
        return self.synonyms.get(word.lower().strip(), [])
    
    def calculate_similarity(self, text1, text2):
        """Calculate similarity percentage between two texts using multiple methods"""
        # Method 1: Word-based Jaccard similarity
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 and not words2:
            return 100.0
        if not words1 or not words2:
            return 0.0
        
        jaccard_sim = len(words1.intersection(words2)) / len(words1.union(words2)) * 100
        
        # Method 2: SequenceMatcher for structural similarity
        sequence_sim = SequenceMatcher(None, text1.lower(), text2.lower()).ratio() * 100
        
        # Method 3: Semantic similarity (key concepts)
        concepts1 = self.extract_key_concepts(text1)
        concepts2 = self.extract_key_concepts(text2)
        
        if concepts1 and concepts2:
            concept_sim = len(concepts1.intersection(concepts2)) / len(concepts1.union(concepts2)) * 100
        else:
            concept_sim = jaccard_sim
        
        # Weighted combination: 50% Jaccard, 30% Sequence, 20% Semantic
        final_similarity = (jaccard_sim * 0.5) + (sequence_sim * 0.3) + (concept_sim * 0.2)
        
        return round(final_similarity, 2)
    
    def extract_key_concepts(self, text):
        """Extract key concepts from text for semantic analysis"""
        words = re.findall(r'\w+', text.lower())
        meaningful_words = [
            word for word in words 
            if (word not in self.stopwords and 
                len(word) > 4 and 
                word.isalpha())
        ]
        return set(meaningful_words)
    
    def phrase_replacement_strategy(self, text):
        """Replace phrases with alternatives"""
        modified_text = text
        replacements_made = []
        
        # Sort phrases by length (longer first) to avoid partial replacements
        sorted_phrases = sorted(self.phrase_replacements.items(), key=lambda x: len(x[0]), reverse=True)
        
        for phrase, alternatives in sorted_phrases:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            match = pattern.search(modified_text)
            
            if match:
                replacement = random.choice(alternatives)
                # Preserve original case
                if match.group().istitle():
                    replacement = replacement.capitalize()
                elif match.group().isupper():
                    replacement = replacement.upper()
                
                modified_text = pattern.sub(replacement, modified_text, count=1)
                replacements_made.append({
                    'type': 'phrase',
                    'original': phrase,
                    'replacement': replacement,
                    'position': match.start()
                })
        
        return modified_text, replacements_made
    
    def word_synonym_strategy(self, text, replacement_ratio=0.4):
        """Replace individual words with synonyms"""
        words = re.findall(r'\b\w+\b|\W+', text)  # Keep punctuation
        modified_words = []
        replacements_made = []
        
        for i, word in enumerate(words):
            if re.match(r'\w+', word):  # It's a word
                clean_word = word.lower()
                
                if (clean_word not in self.stopwords and 
                    len(clean_word) > 3 and 
                    random.random() < replacement_ratio):
                    
                    synonyms = self.get_synonyms(clean_word)
                    if synonyms:
                        suitable_synonyms = [
                            syn for syn in synonyms 
                            if len(syn) >= 3 and syn != clean_word
                        ]
                        
                        if suitable_synonyms:
                            chosen_synonym = random.choice(suitable_synonyms)
                            
                            # Preserve case
                            if word.istitle():
                                chosen_synonym = chosen_synonym.capitalize()
                            elif word.isupper():
                                chosen_synonym = chosen_synonym.upper()
                            
                            modified_words.append(chosen_synonym)
                            replacements_made.append({
                                'type': 'word',
                                'original': word,
                                'replacement': chosen_synonym,
                                'position': i
                            })
                        else:
                            modified_words.append(word)
                    else:
                        modified_words.append(word)
                else:
                    modified_words.append(word)
            else:
                modified_words.append(word)
        
        return ''.join(modified_words), replacements_made
    
    def sentence_restructuring_strategy(self, text):
        """Apply sentence restructuring patterns"""
        modified_text = text
        changes_made = []
        
        for pattern, replacement in self.restructuring_patterns:
            if re.search(pattern, modified_text, re.IGNORECASE):
                old_text = modified_text
                modified_text = re.sub(pattern, replacement, modified_text, flags=re.IGNORECASE)
                if old_text != modified_text:
                    changes_made.append({
                        'type': 'restructure',
                        'pattern': pattern,
                        'replacement': replacement
                    })
        
        return modified_text, changes_made
    
    def is_academic_text(self, text):
        """Detect if text is academic/formal writing"""
        academic_indicators = [
            'penelitian', 'menurut', 'berdasarkan', 'hasil', 'analisis',
            'teori', 'konsep', 'definisi', 'metode', 'pendekatan',
            'sistem', 'implementasi', 'evaluasi', 'kajian', 'studi',
            'universitas', 'jurnal', 'referensi', 'pustaka', 'akademik'
        ]
        
        text_lower = text.lower()
        indicator_count = sum(1 for indicator in academic_indicators if indicator in text_lower)
        
        return indicator_count >= 3
    
    def academic_paraphrasing_strategy(self, text):
        """Specialized paraphrasing for academic text"""
        academic_replacements = {
            'penelitian ini menunjukkan': ['studi ini mengindikasikan', 'riset ini memperlihatkan', 'kajian ini mendemonstrasikan'],
            'hasil penelitian': ['temuan riset', 'output studi', 'hasil kajian', 'temuan investigasi'],
            'metode penelitian': ['metodologi riset', 'pendekatan penelitian', 'teknik investigasi'],
            'tujuan penelitian': ['objektif studi', 'sasaran riset', 'target kajian'],
            'menganalisis': ['mengkaji', 'menelaah', 'menginvestigasi', 'mengeksplorasi'],
            'mengidentifikasi': ['mengenali', 'menemukan', 'mendeteksi', 'melacak'],
            'mengembangkan': ['membangun', 'menciptakan', 'merancang', 'menyusun'],
            'mengevaluasi': ['menilai', 'mengukur', 'menaksir', 'menganalisis'],
            'dengan demikian': ['oleh karena itu', 'maka dari itu', 'akibatnya', 'konsekuensinya'],
            'selanjutnya': ['berikutnya', 'kemudian', 'setelah itu', 'tahap selanjutnya'],
            'sebagai tambahan': ['lebih lanjut', 'di samping itu', 'selain itu', 'furthermore'],
            'signifikan': ['bermakna', 'berarti', 'substansial', 'penting'],
            'optimal': ['terbaik', 'maksimal', 'ideal', 'efektif'],
            'efisien': ['produktif', 'ekonomis', 'hemat', 'streamlined'],
        }
        
        modified_text = text
        changes_made = []
        
        for phrase, alternatives in academic_replacements.items():
            if phrase in modified_text.lower():
                replacement = random.choice(alternatives)
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                if pattern.search(modified_text):
                    modified_text = pattern.sub(replacement, modified_text, count=1)
                    changes_made.append({
                        'type': 'academic_phrase',
                        'original': phrase,
                        'replacement': replacement
                    })
        
        return modified_text, changes_made
    
    def calculate_paragraph_complexity(self, text):
        """Calculate complexity score for smart routing"""
        words = text.split()
        sentences = text.split('.')
        
        # Length factor
        length_score = min(len(words) / 100, 1.0)
        
        # Academic vocabulary density
        academic_words = [
            'penelitian', 'analisis', 'metode', 'sistem', 'implementasi',
            'evaluasi', 'teori', 'konsep', 'pendekatan', 'metodologi',
            'definisi', 'klasifikasi', 'kategori', 'karakteristik'
        ]
        academic_density = sum(1 for word in words if word.lower() in academic_words) / len(words)
        
        # Citation/reference density
        citation_count = len(re.findall(r'\(\d{4}\)|et al|vol\.|no\.', text))
        citation_score = min(citation_count / 3, 1.0)
        
        # Technical pattern density
        pattern_score = sum(1 for pattern in self.ai_priority_patterns if re.search(pattern, text.lower())) / len(self.ai_priority_patterns)
        
        # Average sentence length
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        sentence_complexity = min(avg_sentence_length / 25, 1.0)
        
        # Weighted complexity score
        complexity = (
            length_score * 0.2 +
            academic_density * 0.3 +
            citation_score * 0.2 +
            pattern_score * 0.2 +
            sentence_complexity * 0.1
        )
        
        return min(complexity, 1.0)
    
    def _get_plagiarism_status(self, similarity):
        """Get plagiarism risk status based on similarity"""
        if similarity >= 80:
            return "🔴 HIGH RISK - Perlu parafrase lebih lanjut"
        elif similarity >= 60:
            return "🟡 MEDIUM RISK - Cukup baik, bisa diperbaiki"
        elif similarity >= 40:
            return "🟢 LOW RISK - Parafrase baik"
        else:
            return "✅ VERY LOW RISK - Excellent paraphrase"
    
    # ===== LOCAL PARAPHRASING ENGINE =====
    
    def generate_local_paraphrase(self, text, aggressiveness=0.5):
        """Generate paraphrase using local methods only"""
        if not text or not text.strip():
            return {
                'paraphrase': '',
                'similarity': 100.0,
                'plagiarism_reduction': 0.0,
                'changes_made': 0,
                'change_details': [],
                'method': 'local',
                'status': '❌ No text provided'
            }
        
        current_text = text.strip()
        all_changes = []
        
        # Enhanced strategy selection based on text characteristics
        text_length = len(current_text.split())
        is_academic_text = self.is_academic_text(current_text)
        
        # Strategy 1: Phrase replacement (most effective)
        current_text, phrase_changes = self.phrase_replacement_strategy(current_text)
        all_changes.extend(phrase_changes)
        
        # Strategy 2: Word synonym replacement with adaptive ratio
        if is_academic_text:
            replacement_ratio = min(0.3 + (aggressiveness * 0.4), 0.8)
        else:
            replacement_ratio = min(0.2 + (aggressiveness * 0.5), 0.7)
            
        current_text, word_changes = self.word_synonym_strategy(current_text, replacement_ratio)
        all_changes.extend(word_changes)
        
        # Strategy 3: Sentence restructuring (for longer texts and higher aggressiveness)
        if text_length > 50 and aggressiveness > 0.4 and random.random() > 0.3:
            current_text, struct_changes = self.sentence_restructuring_strategy(current_text)
            all_changes.extend(struct_changes)
        
        # Strategy 4: Academic-specific paraphrasing
        if is_academic_text and aggressiveness > 0.5:
            current_text, academic_changes = self.academic_paraphrasing_strategy(current_text)
            all_changes.extend(academic_changes)
        
        # Calculate metrics
        similarity = self.calculate_similarity(text, current_text)
        plagiarism_reduction = 100 - similarity
        
        return {
            'paraphrase': current_text,
            'similarity': round(similarity, 2),
            'plagiarism_reduction': round(plagiarism_reduction, 2),
            'changes_made': len(all_changes),
            'change_details': all_changes,
            'method': 'local',
            'status': self._get_plagiarism_status(similarity),
            'text_type': 'academic' if is_academic_text else 'general',
            'original_length': text_length,
            'paraphrase_length': len(current_text.split())
        }
    
    # ===== AI INTEGRATION (Smart & Balanced) =====
    
    def create_cache_key(self, text):
        """Create cache key for AI results"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()[:16]
    
    def should_use_ai_smart(self, paragraph_text, local_result):
        """Smart routing decision: Local or AI? (from smart_hybrid_paraphraser.py)"""
        # Always try local first - if it's good enough, don't use AI
        if local_result['plagiarism_reduction'] >= self.current_config['local_confidence_threshold'] * 100:
            return False, "Local result sufficient"
        
        # Check paragraph length
        word_count = len(paragraph_text.split())
        if word_count < self.current_config['min_paragraph_length']:
            return False, "Paragraph too short"
        
        # Calculate complexity
        complexity = self.calculate_paragraph_complexity(paragraph_text)
        
        # High complexity → Use AI
        if complexity >= self.current_config['complexity_threshold']:
            return True, f"High complexity ({complexity:.2f})"
        
        # Check for academic patterns that benefit from AI
        pattern_matches = sum(1 for pattern in self.ai_priority_patterns if re.search(pattern, paragraph_text.lower()))
        if pattern_matches >= 2:
            return True, f"Multiple academic patterns ({pattern_matches})"
        
        # High plagiarism risk based on local analysis
        if local_result['similarity'] >= self.current_config['plagiarism_risk_threshold'] * 100:
            return True, f"High plagiarism risk ({local_result['similarity']:.1f}%)"
        
        return False, "Local processing adequate"
    
    def should_use_ai_balanced(self, paragraph_text, local_result, paragraph_index, total_paragraphs):
        """Balanced routing: aim for target AI usage (from balanced_hybrid_paraphraser.py)"""
        target_ai_ratio = self.current_config['ai_usage_target']
        
        # Force some paragraphs to use AI for comparison
        ai_probability = target_ai_ratio  # Base probability
        
        # Increase probability for academic content
        complexity = self.calculate_paragraph_complexity(paragraph_text)
        if complexity > 0.5:
            ai_probability += 0.2
        
        # Pattern matching bonus
        pattern_matches = sum(1 for pattern in self.ai_priority_patterns if re.search(pattern, paragraph_text.lower()))
        if pattern_matches > 0:
            ai_probability += 0.1 * pattern_matches
        
        # Length bonus
        word_count = len(paragraph_text.split())
        if word_count > 50:
            ai_probability += 0.1
        
        # Deterministic "random" selection based on paragraph index
        random_factor = (paragraph_index * 7) % 100 / 100
        
        if random_factor < ai_probability:
            return True, f"Balanced selection (prob: {ai_probability:.2f})"
        
        # Traditional criteria (lowered thresholds)
        if local_result['plagiarism_reduction'] < self.current_config['local_confidence_threshold'] * 100:
            return True, f"Low local performance ({local_result['plagiarism_reduction']:.1f}%)"
        
        # Check paragraph length (lowered threshold)
        if word_count < self.current_config['min_paragraph_length']:
            return False, "Paragraph too short"
        
        # Complexity check (lowered threshold)
        if complexity >= self.current_config['complexity_threshold']:
            return True, f"Moderate complexity ({complexity:.2f})"
        
        # Academic patterns (more generous)
        if pattern_matches >= 1:
            return True, f"Academic pattern detected ({pattern_matches})"
        
        return False, "Local processing preferred"
    
    def should_use_ai_turnitin_safe(self, paragraph_text, local_result):
        """Turnitin-safe routing: extra careful approach"""
        # Check for Turnitin risk patterns
        risk_patterns = sum(1 for pattern in self.turnitin_risk_patterns if re.search(pattern, paragraph_text.lower()))
        if risk_patterns >= 2:
            return True, f"High Turnitin risk patterns ({risk_patterns})"
        
        # Higher thresholds for turnitin_safe mode
        if local_result['plagiarism_reduction'] < self.current_config['local_confidence_threshold'] * 100:
            return True, f"Insufficient local reduction ({local_result['plagiarism_reduction']:.1f}%)"
        
        # More complex texts need AI
        complexity = self.calculate_paragraph_complexity(paragraph_text)
        if complexity >= self.current_config['complexity_threshold']:
            return True, f"High complexity for Turnitin ({complexity:.2f})"
        
        # Conservative approach for academic content
        if self.is_academic_text(paragraph_text) and local_result['similarity'] > 70:
            return True, f"Academic content with high similarity ({local_result['similarity']:.1f}%)"
        
        return False, "Turnitin-safe: Local adequate"
    
    def decide_ai_usage(self, paragraph_text, local_result, paragraph_index=0, total_paragraphs=1):
        """Central AI decision logic based on current mode"""
        if self.mode == 'smart':
            return self.should_use_ai_smart(paragraph_text, local_result)
        elif self.mode == 'balanced':
            return self.should_use_ai_balanced(paragraph_text, local_result, paragraph_index, total_paragraphs)
        elif self.mode == 'aggressive':
            # Always use AI unless very short
            word_count = len(paragraph_text.split())
            if word_count >= self.current_config['min_paragraph_length']:
                return True, "Aggressive mode: Always AI"
            return False, "Too short for aggressive mode"
        elif self.mode == 'turnitin_safe':
            return self.should_use_ai_turnitin_safe(paragraph_text, local_result)
        else:
            # Fallback to smart
            return self.should_use_ai_smart(paragraph_text, local_result)
    
    def call_gemini_api(self, paragraphs_batch):
        """Call Gemini API for batch processing with multiple methods"""
        if self.api_method == 'genai' and self.gemini_client:
            return self._call_gemini_genai(paragraphs_batch)
        elif self.api_method == 'requests':
            return self._call_gemini_requests(paragraphs_batch)
        else:
            print("❌ No Gemini API method available")
            return None
    
    def _call_gemini_genai(self, paragraphs_batch):
        """Call Gemini using google-generativeai package"""
        try:
            prompt = self.create_gemini_prompt(paragraphs_batch)
            
            generation_config = genai.GenerationConfig(
                temperature=0.4,
                top_k=50,
                top_p=0.9,
                max_output_tokens=6144,
            )
            
            for attempt in range(3):
                try:
                    response = self.gemini_client.generate_content(
                        prompt,
                        generation_config=generation_config,
                    )
                    
                    if response.text and response.text.strip():
                        # Track usage
                        self.cost_tracker['ai_calls'] += 1
                        tokens_used = len(prompt + response.text) // 4
                        self.cost_tracker['ai_tokens_used'] += tokens_used
                        self.cost_tracker['estimated_cost_usd'] += tokens_used * 0.000001
                        
                        return self.parse_gemini_response(response.text, paragraphs_batch)
                    
                except Exception as e:
                    print(f"⚠️  Gemini GenAI attempt {attempt + 1} failed: {e}")
                    if attempt < 2:
                        time.sleep(3 ** attempt)
            
            return None
            
        except Exception as e:
            print(f"❌ Gemini GenAI error: {e}")
            return None
    
    def _call_gemini_requests(self, paragraphs_batch):
        """Call Gemini using requests (fallback method)"""
        try:
            prompt = self.create_gemini_prompt(paragraphs_batch)
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.4,
                    "topK": 50,
                    "topP": 0.9,
                    "maxOutputTokens": 6144,
                }
            }
            
            for attempt in range(3):
                try:
                    response = requests.post(
                        f"{self.gemini_api_url}?key={self.gemini_api_key}",
                        headers=headers,
                        json=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'candidates' in result and result['candidates']:
                            ai_response = result['candidates'][0]['parts'][0]['text']
                            
                            # Track usage
                            self.cost_tracker['ai_calls'] += 1
                            tokens_used = len(prompt + ai_response) // 4
                            self.cost_tracker['ai_tokens_used'] += tokens_used
                            self.cost_tracker['estimated_cost_usd'] += tokens_used * 0.000002
                            
                            return self.parse_gemini_response(ai_response, paragraphs_batch)
                    
                    else:
                        print(f"⚠️  Gemini API error {response.status_code}: {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"⚠️  API call attempt {attempt + 1} failed: {e}")
                    if attempt < 2:
                        time.sleep(2 ** attempt)
            
            return None
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return None
    
    def create_gemini_prompt(self, paragraphs_batch):
        """Create optimized prompt for Gemini API"""
        mode_instructions = {
            'smart': 'Fokus pada efisiensi biaya dengan hasil berkualitas tinggi.',
            'balanced': 'Berikan hasil terbaik untuk perbandingan dengan metode lokal.',
            'aggressive': 'Maksimalkan pengurangan plagiarisme tanpa mempertimbangkan biaya.',
            'turnitin_safe': 'Pastikan hasil aman dari deteksi Turnitin dengan transformasi mendalam.'
        }
        
        prompt = f"""Kamu adalah expert paraphrasing untuk teks akademik bahasa Indonesia. 

MODE: {self.mode.upper()} - {mode_instructions.get(self.mode, '')}

MISI: Parafrase paragraf berikut untuk mengurangi plagiarisme secara signifikan sambil mempertahankan makna akademik yang tepat.

STRATEGI PARAPHRASING:
✅ Gunakan sinonim yang tepat dan kontekstual
✅ Ubah struktur kalimat (aktif↔pasif, urutan klausa)
✅ Ganti frasa akademik dengan variasi yang setara
✅ Ubah konstruksi gramatikal tanpa mengubah makna
✅ Pertahankan tone formal dan akademik
✅ PENTING: Hasil harus natural dan mudah dibaca

TARGET: Minimal 40-70% pengurangan similarity

FORMAT JAWABAN:
PARAGRAF_[NOMOR]:
[Hasil parafrase yang natural dan akademis]

PARAGRAF YANG PERLU DIPARAFRASE:
"""
        
        for i, paragraph in enumerate(paragraphs_batch, 1):
            prompt += f"\nPARAGRAF_{i}:\n{paragraph['text']}\n"
        
        prompt += "\n🎯 MULAI PARAPHRASING SEKARANG (Sesuai mode dan target):"
        
        return prompt
    
    def parse_gemini_response(self, ai_response, original_paragraphs):
        """Parse Gemini response back to structured format"""
        results = []
        
        try:
            # Split response by paragraph markers
            sections = re.split(r'PARAGRAF_(\d+):', ai_response)
            
            for i in range(1, len(sections), 2):
                if i + 1 < len(sections):
                    paragraph_num = int(sections[i]) - 1
                    paraphrased_text = sections[i + 1].strip()
                    
                    # Clean up the response
                    paraphrased_text = re.sub(r'^[-•*]\s*', '', paraphrased_text)
                    paraphrased_text = re.sub(r'\n+', ' ', paraphrased_text)
                    paraphrased_text = paraphrased_text.strip()
                    
                    if paragraph_num < len(original_paragraphs) and paraphrased_text:
                        original_text = original_paragraphs[paragraph_num]['text']
                        
                        # Calculate similarity
                        similarity = self.calculate_similarity(original_text, paraphrased_text)
                        
                        result = {
                            'paraphrase': paraphrased_text,
                            'similarity': round(similarity, 2),
                            'plagiarism_reduction': round(100 - similarity, 2),
                            'changes_made': 1,
                            'method': f'gemini_{self.mode}',
                            'status': self._get_plagiarism_status(similarity),
                            'original_length': len(original_text.split()),
                            'paraphrase_length': len(paraphrased_text.split())
                        }
                        
                        results.append(result)
            
            return results
            
        except Exception as e:
            print(f"⚠️  Error parsing Gemini response: {e}")
            return []
    
    # ===== MAIN PROCESSING ENGINE =====
    
    def process_paragraph_ultimate(self, paragraph_text, paragraph_index=0, total_paragraphs=1, aggressiveness=0.5):
        """Ultimate paragraph processing with mode-aware routing and comparison"""
        
        # Step 1: Always get local result first
        local_result = self.generate_local_paraphrase(paragraph_text, aggressiveness)
        self.cost_tracker['local_calls'] += 1
        
        # Step 2: Decide if AI is needed based on current mode
        use_ai, reason = self.decide_ai_usage(paragraph_text, local_result, paragraph_index, total_paragraphs)
        
        if not use_ai:
            local_result['method'] = f'local_{self.mode}'
            local_result['routing_reason'] = reason
            return local_result
        
        # Step 3: Check AI cache first
        cache_key = self.create_cache_key(paragraph_text)
        if cache_key in self.ai_cache:
            self.cost_tracker['cache_hits'] += 1
            ai_result = self.ai_cache[cache_key].copy()
            ai_result['method'] = f'ai_cached_{self.mode}'
            ai_result['routing_reason'] = reason
            
            # For balanced mode, still compare with local
            if self.mode == 'balanced' and self.current_config.get('comparison_mode', False):
                self._log_comparison(local_result, ai_result, paragraph_index)
            
            return ai_result
        
        # Step 4: Use AI
        print(f"    🤖 Using AI ({self.mode}): {reason}")
        
        ai_results = self.call_gemini_api([{'text': paragraph_text}])
        
        if ai_results and len(ai_results) > 0:
            ai_result = ai_results[0]
            ai_result['routing_reason'] = reason
            
            # Cache the AI result
            self.ai_cache[cache_key] = ai_result.copy()
            
            # Mode-specific result selection
            final_result = self._select_best_result(local_result, ai_result, paragraph_index)
            return final_result
        
        # Step 5: Fallback to local if AI fails
        local_result['method'] = f'local_fallback_{self.mode}'
        local_result['routing_reason'] = f"{reason} (AI failed)"
        return local_result
    
    def _select_best_result(self, local_result, ai_result, paragraph_index):
        """Select the best result based on current mode"""
        
        if self.mode == 'aggressive':
            # Always prefer AI in aggressive mode
            ai_result['method'] = f'ai_{self.mode}'
            return ai_result
        
        elif self.mode == 'balanced':
            # Compare results and log
            comparison = self._log_comparison(local_result, ai_result, paragraph_index)
            
            # Choose better result
            if ai_result['plagiarism_reduction'] > local_result['plagiarism_reduction']:
                ai_result['method'] = f'ai_{self.mode}_winner'
                ai_result['improvement'] = ai_result['plagiarism_reduction'] - local_result['plagiarism_reduction']
                return ai_result
            else:
                local_result['method'] = f'local_{self.mode}_winner'
                local_result['improvement'] = local_result['plagiarism_reduction'] - ai_result['plagiarism_reduction']
                return local_result
        
        elif self.mode == 'smart':
            # Smart selection: prefer AI only if significantly better
            improvement_threshold = 10  # AI must be 10% better
            if ai_result['plagiarism_reduction'] > local_result['plagiarism_reduction'] + improvement_threshold:
                ai_result['method'] = f'ai_{self.mode}_better'
                ai_result['improvement'] = ai_result['plagiarism_reduction'] - local_result['plagiarism_reduction']
                return ai_result
            else:
                local_result['method'] = f'local_{self.mode}_sufficient'
                local_result['ai_attempted'] = True
                return local_result
        
        elif self.mode == 'turnitin_safe':
            # Turnitin-safe: prefer the result with lower similarity (higher reduction)
            if ai_result['similarity'] < local_result['similarity']:
                ai_result['method'] = f'ai_{self.mode}_safer'
                return ai_result
            else:
                local_result['method'] = f'local_{self.mode}_safer'
                return local_result
        
        else:
            # Default: choose better result
            if ai_result['plagiarism_reduction'] > local_result['plagiarism_reduction']:
                ai_result['method'] = f'ai_{self.mode}_default'
                return ai_result
            else:
                local_result['method'] = f'local_{self.mode}_default'
                return local_result
    
    def _log_comparison(self, local_result, ai_result, paragraph_index):
        """Log comparison for balanced mode analysis"""
        comparison = {
            'paragraph_index': paragraph_index,
            'local_reduction': local_result['plagiarism_reduction'],
            'ai_reduction': ai_result['plagiarism_reduction'],
            'improvement': ai_result['plagiarism_reduction'] - local_result['plagiarism_reduction'],
            'winner': 'ai' if ai_result['plagiarism_reduction'] > local_result['plagiarism_reduction'] else 'local',
            'local_similarity': local_result['similarity'],
            'ai_similarity': ai_result['similarity']
        }
        self.cost_tracker['local_vs_ai_comparison'].append(comparison)
        
        print(f"    📊 Comparison: Local {local_result['plagiarism_reduction']:.1f}% vs AI {ai_result['plagiarism_reduction']:.1f}%")
        
        return comparison
    
    def generate_multiple_options(self, text, num_options=3):
        """Generate multiple paraphrase options using different approaches"""
        if not text or not text.strip():
            return []
        
        options = []
        
        # Save original mode
        original_mode = self.mode
        
        # Option 1: Local only (baseline)
        local_result = self.generate_local_paraphrase(text, aggressiveness=0.5)
        local_result['option_number'] = 1
        local_result['option_type'] = 'local_baseline'
        options.append(local_result)
        
        # Option 2: Smart mode (if not already in smart mode)
        if self.mode != 'smart':
            self.switch_mode('smart')
            smart_result = self.process_paragraph_ultimate(text, aggressiveness=0.6)
            smart_result['option_number'] = 2
            smart_result['option_type'] = 'smart_hybrid'
            options.append(smart_result)
        
        # Option 3: Balanced mode (if available)
        if num_options >= 3 and GEMINI_AVAILABLE:
            self.switch_mode('balanced')
            balanced_result = self.process_paragraph_ultimate(text, aggressiveness=0.7)
            balanced_result['option_number'] = 3
            balanced_result['option_type'] = 'balanced_hybrid'
            options.append(balanced_result)
        
        # Option 4: Aggressive mode (if requested)
        if num_options >= 4 and GEMINI_AVAILABLE:
            self.switch_mode('aggressive')
            aggressive_result = self.process_paragraph_ultimate(text, aggressiveness=0.8)
            aggressive_result['option_number'] = 4
            aggressive_result['option_type'] = 'aggressive_ai'
            options.append(aggressive_result)
        
        # Restore original mode
        self.switch_mode(original_mode)
        
        # Sort by plagiarism reduction (best first)
        options.sort(key=lambda x: x['plagiarism_reduction'], reverse=True)
        
        # Re-number after sorting
        for i, option in enumerate(options):
            option['option_number'] = i + 1
            option['rank'] = i + 1
        
        return options[:num_options]
    
    def analyze_text_characteristics(self, text):
        """Analyze text characteristics for better processing recommendations"""
        if not text:
            return {}
        
        words = text.split()
        sentences = text.split('.')
        
        characteristics = {
            'length': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'avg_sentence_length': len(words) / len([s for s in sentences if s.strip()]) if sentences else 0,
            'complexity_score': self.calculate_paragraph_complexity(text),
            'is_academic': self.is_academic_text(text),
            'academic_indicators': sum(1 for indicator in ['penelitian', 'analisis', 'metode', 'sistem'] if indicator in text.lower()),
            'citation_count': len(re.findall(r'\(\d{4}\)', text)),
            'technical_patterns': sum(1 for pattern in self.ai_priority_patterns if re.search(pattern, text.lower())),
            'turnitin_risk_patterns': sum(1 for pattern in self.turnitin_risk_patterns if re.search(pattern, text.lower()))
        }
        
        # Recommendations based on characteristics
        if characteristics['complexity_score'] > 0.7:
            characteristics['recommended_mode'] = 'aggressive'
            characteristics['recommended_aggressiveness'] = 0.8
        elif characteristics['is_academic'] and characteristics['technical_patterns'] >= 2:
            characteristics['recommended_mode'] = 'balanced'
            characteristics['recommended_aggressiveness'] = 0.6
        elif characteristics['turnitin_risk_patterns'] >= 2:
            characteristics['recommended_mode'] = 'turnitin_safe'
            characteristics['recommended_aggressiveness'] = 0.7
        else:
            characteristics['recommended_mode'] = 'smart'
            characteristics['recommended_aggressiveness'] = 0.5
        
        return characteristics
    
    def get_processing_statistics(self):
        """Get comprehensive processing statistics"""
        stats = {
            'current_mode': self.mode,
            'cost_tracker': self.cost_tracker.copy(),
            'cache_size': len(self.ai_cache),
            'total_processed': self.cost_tracker['local_calls'],
            'ai_usage_ratio': 0,
            'cost_per_paragraph': 0,
            'average_improvement': 0
        }
        
        # Calculate AI usage ratio
        if stats['total_processed'] > 0:
            stats['ai_usage_ratio'] = self.cost_tracker['ai_calls'] / stats['total_processed']
        
        # Calculate cost per paragraph
        if stats['total_processed'] > 0:
            stats['cost_per_paragraph'] = self.cost_tracker['estimated_cost_usd'] / stats['total_processed']
        
        # Calculate average AI improvement
        if self.cost_tracker['local_vs_ai_comparison']:
            improvements = [c['improvement'] for c in self.cost_tracker['local_vs_ai_comparison']]
            stats['average_improvement'] = sum(improvements) / len(improvements)
        
        return stats


def main():
    """Demo function for Ultimate Hybrid Paraphraser"""
    print("=" * 80)
    print("🎯 ULTIMATE HYBRID PARAPHRASER v3.0")
    print("🚀 Consolidated System: Smart + Balanced + Turnitin Detection + AI")
    print("=" * 80)
    
    # Initialize system with different modes
    print("\n🔧 Testing different modes...")
    
    # Test text (academic sample)
    test_text = """Penelitian ini bertujuan untuk mengembangkan sistem parafrase otomatis yang dapat mengurangi tingkat plagiarisme dalam dokumen akademik. Sistem menggunakan pendekatan berbasis aturan dan sinonim untuk menghasilkan variasi kalimat yang mempertahankan makna asli tetapi berbeda dalam struktur dan pilihan kata."""
    
    print(f"\n📝 TEKS ASLI:")
    print(f"'{test_text}'")
    
    # Test different modes
    modes_to_test = ['smart', 'balanced', 'aggressive', 'turnitin_safe']
    
    for mode in modes_to_test:
        if mode in ['balanced', 'aggressive'] and not GEMINI_AVAILABLE:
            print(f"\n⚠️  Skipping {mode} mode - Gemini AI not available")
            continue
            
        print(f"\n{'='*20} MODE: {mode.upper()} {'='*20}")
        
        # Initialize processor for this mode
        processor = UltimateHybridParaphraser(
            synonym_file='sinonim.json',
            mode=mode
        )
        
        # Process the text
        result = processor.process_paragraph_ultimate(test_text, aggressiveness=0.6)
        
        print(f"✅ HASIL ({mode.upper()}):")
        print(f"   Parafrase: '{result['paraphrase']}'")
        print(f"   Similarity: {result['similarity']}%")
        print(f"   Reduction: {result['plagiarism_reduction']}%")
        print(f"   Method: {result['method']}")
        print(f"   Status: {result['status']}")
        if 'routing_reason' in result:
            print(f"   Routing: {result['routing_reason']}")
        
        # Show statistics
        stats = processor.get_processing_statistics()
        print(f"\n📊 STATISTIK {mode.upper()}:")
        print(f"   AI Usage: {stats['ai_usage_ratio']*100:.1f}%")
        print(f"   Cache Hits: {stats['cost_tracker']['cache_hits']}")
        print(f"   Estimated Cost: ${stats['cost_tracker']['estimated_cost_usd']:.4f}")
    
    print("\n" + "="*80)
    print("🎉 Ultimate Hybrid Paraphraser Demo Completed!")
    print("💡 All modes consolidated into single powerful system")
    print("="*80)


if __name__ == "__main__":
    main()
