# full_gemini_paraphraser.py
"""
Full Gemini AI Paraphraser - Enhanced Quality System
Focus: High-quality paraphrasing using full Gemini AI with content protection
Features:
- Full Gemini AI for superior sentence quality
- Protection for titles, author names, and important headings
- Academic document optimization
- Smart content preservation

Author: DevNoLife
Version: 1.0 - Full AI Edition
"""

import os
import json
import re
import time
from datetime import datetime
from pathlib import Path
import docx
from collections import defaultdict
import requests
from difflib import SequenceMatcher
import glob

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

class FullGeminiParaphraser:
    def __init__(self, synonym_file='sinonim.json', gemini_api_key=None):
        print("🚀 Initializing Full Gemini Paraphraser v1.0...")
        print("🎯 Focus: High-Quality AI Paraphrasing with Content Protection")
        
        # API Configuration
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key:
            print("❌ GEMINI_API_KEY not found! Set it in environment variables or .env file")
            raise ValueError("Gemini API key is required")
        
        # Initialize Gemini client
        self._initialize_gemini_client()
        
        # Load synonym database for reference (not primary paraphrasing)
        self.synonyms = self.load_synonyms(synonym_file)
        print(f"📚 Loaded {len(self.synonyms)} synonym groups")
        
        # Content protection patterns
        self.protection_patterns = {
            'titles': [
                r'^BAB\s+[IVX]+.*',  # Chapter titles
                r'^CHAPTER\s+\d+.*',
                r'^Bab\s+\d+.*',
                r'^\d+\.\s*[A-Z][^.]*$',  # Numbered titles without ending punctuation
                r'^[A-Z][A-Z\s]{5,}$',  # ALL CAPS titles
            ],
            'author_names': [
                r'Author:\s*(.+)',
                r'Penulis:\s*(.+)', 
                r'Oleh:\s*(.+)',
                r'^([A-Z][a-z]+\s+[A-Z][a-z]+(\s+[A-Z][a-z]+)*)$',  # Proper names
            ],
            'headings': [
                r'^\d+\.\d+.*',  # 1.1 Heading format
                r'^\d+\.\d+\.\d+.*',  # 1.1.1 Subheading format
                r'^[A-Z]\.\s+[A-Z].*',  # A. Heading format
                r'^ABSTRAK$|^ABSTRACT$|^PENDAHULUAN$|^KESIMPULAN$',
                r'^DAFTAR\s+(ISI|PUSTAKA|GAMBAR|TABEL)',
            ],
            'citations': [
                r'\(.+?\d{4}.+?\)',  # (Author, 2024)
                r'\[.+?\]',  # [1], [Author, 2024]
                r'(Menurut|According to).+?\(\d{4}\)',
            ],
            'formulas': [
                r'[A-Za-z]\s*=\s*[^.]{1,50}',  # Mathematical formulas
                r'\$.*?\$',  # LaTeX formulas
            ],
            'tables_figures': [
                r'^Tabel\s+\d+.*',
                r'^Gambar\s+\d+.*',
                r'^Figure\s+\d+.*',
                r'^Table\s+\d+.*',
            ]
        }
        
        # Cost tracking
        self.cost_tracker = {
            'total_api_calls': 0,
            'total_tokens_used': 0,
            'total_cost_usd': 0.0,
            'paragraphs_processed': 0,
            'protected_content': 0
        }
        
        # Processing statistics
        self.stats = {
            'start_time': datetime.now(),
            'total_similarity_reduction': 0,
            'protected_items': [],
            'quality_scores': []
        }
        
        print("✅ Full Gemini Paraphraser initialized successfully!")

    def _initialize_gemini_client(self):
        """Initialize Gemini AI client"""
        if GEMINI_AVAILABLE == True:
            try:
                genai.configure(api_key=self.gemini_api_key)
                # Use the most advanced model available
                self.gemini_client = genai.GenerativeModel('gemini-2.0-flash-thinking-exp')
                self.api_method = 'genai'
                print(f"✅ Gemini client initialized (gemini-2.0-flash-thinking-exp)")
            except Exception as e:
                try:
                    # Fallback to standard model
                    self.gemini_client = genai.GenerativeModel('gemini-1.5-pro')
                    self.api_method = 'genai'
                    print(f"✅ Gemini client initialized (gemini-1.5-pro fallback)")
                except Exception as e2:
                    print(f"⚠️  Google GenAI failed: {e2}")
                    self.gemini_client = None
                    self.api_method = 'requests'
        elif GEMINI_AVAILABLE == "requests":
            self.api_method = 'requests'
            self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        else:
            raise ValueError("Gemini AI not available. Please install google-generativeai")

    def load_synonyms(self, filename):
        """Load synonym database from JSON file"""
        if not filename or not os.path.exists(filename):
            print("⚠️  No synonym file provided or file not found")
            return {}
        
        try:
            # Try components directory first
            if not os.path.exists(filename):
                components_path = os.path.join('components', filename)
                if os.path.exists(components_path):
                    filename = components_path
            
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

    def is_protected_content(self, text):
        """Check if content should be protected from paraphrasing"""
        text = text.strip()
        
        # Check each protection category
        for category, patterns in self.protection_patterns.items():
            for pattern in patterns:
                if re.match(pattern, text, re.IGNORECASE):
                    self.stats['protected_items'].append({
                        'text': text[:100],  # First 100 chars for logging
                        'category': category,
                        'pattern': pattern
                    })
                    return True, category
        
        return False, None

    def create_full_gemini_prompt(self, text, context="academic"):
        """Create comprehensive prompt for full Gemini AI paraphrasing"""
        
        prompt = f"""Anda adalah expert akademis dalam paraphrasing bahasa Indonesia dengan spesialisasi pada teks ilmiah dan penelitian.

MISI UTAMA: Parafrase teks berikut untuk menghasilkan kualitas tulisan akademis yang superior dengan pengurangan plagiarisme maksimal sambil mempertahankan makna dan konteks yang tepat.

STRATEGI PARAPHRASING ADVANCED:
✅ SINONIM KONTEKSTUAL: Gunakan sinonim yang tepat sesuai konteks akademis
✅ TRANSFORMASI STRUKTURAL: Ubah struktur kalimat secara mendalam (aktif↔pasif, subordinasi↔koordinasi)
✅ VARIASI FRASA AKADEMIS: Ganti terminologi akademis dengan variasi yang setara namun berbeda
✅ REKONSTRUKSI GRAMATIKAL: Ubah konstruksi gramatikal tanpa mengubah substansi
✅ OPTIMASI FLOW: Pastikan alur kalimat natural dan mudah dibaca
✅ TONE AKADEMIS: Pertahankan registrer formal dan scientific writing style
✅ COHERENCE: Jaga koherensi antar kalimat dan paragraf

TARGET KUALITAS:
- Pengurangan similarity: 50-80%
- Readability score: Tinggi (mudah dipahami)
- Academic tone: Dipertahankan
- Meaning preservation: 100%

KONTEKS: {context}

ATURAN KHUSUS:
- JANGAN ubah nama orang, tempat, atau istilah teknis spesifik
- PERTAHANKAN angka, tanggal, dan data statistik
- JAGA konsistensi terminologi dalam satu dokumen
- Hasil harus terdengar natural bagi pembaca Indonesia

TEKS YANG AKAN DIPARAFRASE:
"{text}"

INSTRUKSI RESPONSE:
Berikan HANYA hasil parafrase tanpa penjelasan tambahan. Hasil harus berupa paragraf yang flow dan natural."""

        return prompt

    def call_gemini_ai(self, prompt, max_retries=3):
        """Call Gemini AI API with error handling and retry logic"""
        for attempt in range(max_retries):
            try:
                if self.api_method == 'genai':
                    response = self.gemini_client.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.7,  # Balanced creativity
                            max_output_tokens=4000,
                            top_p=0.8,
                            top_k=40
                        )
                    )
                    
                    if response and response.text:
                        self.cost_tracker['total_api_calls'] += 1
                        # Estimate token usage (rough calculation)
                        estimated_tokens = len(prompt.split()) + len(response.text.split())
                        self.cost_tracker['total_tokens_used'] += estimated_tokens
                        return response.text.strip()
                
                elif self.api_method == 'requests':
                    headers = {
                        'Content-Type': 'application/json',
                    }
                    
                    payload = {
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": 0.7,
                            "maxOutputTokens": 4000,
                            "topP": 0.8,
                            "topK": 40
                        }
                    }
                    
                    response = requests.post(
                        f"{self.gemini_api_url}?key={self.gemini_api_key}",
                        headers=headers,
                        json=payload,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'candidates' in data and len(data['candidates']) > 0:
                            text = data['candidates'][0]['content']['parts'][0]['text']
                            self.cost_tracker['total_api_calls'] += 1
                            estimated_tokens = len(prompt.split()) + len(text.split())
                            self.cost_tracker['total_tokens_used'] += estimated_tokens
                            return text.strip()
                    else:
                        print(f"❌ API Error {response.status_code}: {response.text}")
                        
            except Exception as e:
                print(f"⚠️  Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        print("❌ All Gemini API attempts failed")
        return None

    def calculate_similarity(self, text1, text2):
        """Enhanced similarity calculation"""
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
        
        # Method 3: Phrase-level similarity
        phrases1 = set(text1.lower().split())
        phrases2 = set(text2.lower().split())
        phrase_sim = len(phrases1.intersection(phrases2)) / len(phrases1.union(phrases2)) * 100
        
        # Weighted combination: 40% Jaccard, 40% Sequence, 20% Phrase
        final_similarity = (jaccard_sim * 0.4) + (sequence_sim * 0.4) + (phrase_sim * 0.2)
        
        return round(final_similarity, 2)

    def paraphrase_text(self, text, context="academic"):
        """Main paraphrasing method using full Gemini AI"""
        
        # Check if content should be protected
        is_protected, category = self.is_protected_content(text)
        if is_protected:
            print(f"🛡️  Protected content detected ({category}): {text[:50]}...")
            self.cost_tracker['protected_content'] += 1
            return {
                'paraphrase': text,  # Return original
                'original': text,
                'similarity': 100.0,
                'plagiarism_reduction': 0.0,
                'method': 'protected_content',
                'category': category,
                'status': 'PROTECTED'
            }
        
        # Create comprehensive prompt
        prompt = self.create_full_gemini_prompt(text, context)
        
        # Call Gemini AI
        print(f"🤖 Processing with Full Gemini AI...")
        paraphrased = self.call_gemini_ai(prompt)
        
        if not paraphrased:
            print("❌ AI processing failed, returning original text")
            return {
                'paraphrase': text,
                'original': text,
                'similarity': 100.0,
                'plagiarism_reduction': 0.0,
                'method': 'ai_failed',
                'status': 'FAILED'
            }
        
        # Calculate similarity and quality metrics
        similarity = self.calculate_similarity(text, paraphrased)
        plagiarism_reduction = 100 - similarity
        
        # Update statistics
        self.cost_tracker['paragraphs_processed'] += 1
        self.stats['total_similarity_reduction'] += plagiarism_reduction
        
        # Quality assessment
        quality_score = self.assess_quality(text, paraphrased)
        self.stats['quality_scores'].append(quality_score)
        
        result = {
            'paraphrase': paraphrased,
            'original': text,
            'similarity': similarity,
            'plagiarism_reduction': plagiarism_reduction,
            'method': 'full_gemini_ai',
            'quality_score': quality_score,
            'status': self._get_status(similarity),
            'word_count_original': len(text.split()),
            'word_count_paraphrase': len(paraphrased.split())
        }
        
        return result

    def assess_quality(self, original, paraphrased):
        """Assess the quality of paraphrasing"""
        score = 0
        
        # Length similarity (good paraphrase should have similar length)
        len_ratio = min(len(paraphrased), len(original)) / max(len(paraphrased), len(original))
        score += len_ratio * 25
        
        # Word diversity (how many different words used)
        orig_words = set(original.lower().split())
        para_words = set(paraphrased.lower().split())
        diversity = len(para_words - orig_words) / len(orig_words) if orig_words else 0
        score += min(diversity, 1) * 25
        
        # Sentence structure variety (different sentence patterns)
        orig_sentences = len(re.findall(r'[.!?]+', original))
        para_sentences = len(re.findall(r'[.!?]+', paraphrased))
        structure_score = 25 if orig_sentences == para_sentences else 15
        score += structure_score
        
        # Readability (avoid overly complex sentences)
        avg_word_len = sum(len(word) for word in paraphrased.split()) / len(paraphrased.split()) if paraphrased.split() else 0
        readability = max(0, 25 - (avg_word_len - 6) * 2)  # Penalize very long words
        score += readability
        
        return round(score, 2)

    def _get_status(self, similarity):
        """Get processing status based on similarity"""
        if similarity >= 70:
            return 'HIGH_SIMILARITY'
        elif similarity >= 40:
            return 'MEDIUM_SIMILARITY'
        elif similarity >= 20:
            return 'LOW_SIMILARITY'
        else:
            return 'VERY_LOW_SIMILARITY'

    def process_document(self, input_path, output_path=None):
        """Process entire document with full AI paraphrasing"""
        print(f"🎯 Processing document: {input_path}")
        print("🤖 Using Full Gemini AI for superior quality...")
        
        if not os.path.exists(input_path):
            print(f"❌ File not found: {input_path}")
            return None
        
        # Generate output path if not provided
        if not output_path:
            base_name = Path(input_path).stem
            ext = Path(input_path).suffix
            # Save to completed folder
            completed_dir = "completed"
            os.makedirs(completed_dir, exist_ok=True)
            output_path = os.path.join(completed_dir, f"{base_name}_paraphrased{ext}")
        
        try:
            # Load document
            doc = docx.Document(input_path)
            results = []
            total_paragraphs = len([p for p in doc.paragraphs if p.text.strip()])
            
            print(f"📄 Found {total_paragraphs} paragraphs to process")
            
            for i, paragraph in enumerate(doc.paragraphs):
                if not paragraph.text.strip():
                    continue
                
                print(f"🔄 Processing paragraph {i+1}/{total_paragraphs}")
                
                # Process paragraph
                result = self.paraphrase_text(paragraph.text.strip())
                results.append(result)
                
                # Update paragraph with paraphrased text (if not protected)
                if result['method'] != 'protected_content':
                    paragraph.text = result['paraphrase']
                
                # Add some delay to avoid rate limiting
                time.sleep(0.5)
            
            # Save processed document
            doc.save(output_path)
            print(f"✅ Document saved: {output_path}")
            
            # Generate detailed report
            report = self.generate_report(results, input_path, output_path)
            
            return {
                'output_path': output_path,
                'results': results,
                'report': report,
                'statistics': self.get_statistics()
            }
            
        except Exception as e:
            print(f"❌ Error processing document: {e}")
            return None

    def generate_report(self, results, input_path, output_path):
        """Generate detailed processing report"""
        report = {
            'processing_info': {
                'input_file': input_path,
                'output_file': output_path,
                'processing_time': str(datetime.now() - self.stats['start_time']),
                'timestamp': datetime.now().isoformat()
            },
            'summary': {
                'total_paragraphs': len(results),
                'protected_content': sum(1 for r in results if r.get('method') == 'protected_content'),
                'successfully_paraphrased': sum(1 for r in results if r.get('method') == 'full_gemini_ai'),
                'average_similarity_reduction': round(
                    sum(r.get('plagiarism_reduction', 0) for r in results) / len(results), 2
                ) if results else 0,
                'average_quality_score': round(
                    sum(r.get('quality_score', 0) for r in results if 'quality_score' in r) / 
                    len([r for r in results if 'quality_score' in r]), 2
                ) if any('quality_score' in r for r in results) else 0
            },
            'costs': self.cost_tracker,
            'protected_items': self.stats['protected_items'],
            'quality_distribution': self._get_quality_distribution(results)
        }
        
        # Save report to JSON
        report_path = f"report_{Path(output_path).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Report saved: {report_path}")
        return report

    def _get_quality_distribution(self, results):
        """Get quality score distribution"""
        quality_scores = [r.get('quality_score', 0) for r in results if 'quality_score' in r]
        if not quality_scores:
            return {}
        
        return {
            'excellent': sum(1 for q in quality_scores if q >= 80),
            'good': sum(1 for q in quality_scores if 60 <= q < 80),
            'fair': sum(1 for q in quality_scores if 40 <= q < 60),
            'poor': sum(1 for q in quality_scores if q < 40),
            'average': round(sum(quality_scores) / len(quality_scores), 2),
            'highest': max(quality_scores),
            'lowest': min(quality_scores)
        }

    def get_statistics(self):
        """Get processing statistics"""
        return {
            'runtime': str(datetime.now() - self.stats['start_time']),
            'total_api_calls': self.cost_tracker['total_api_calls'],
            'total_tokens_used': self.cost_tracker['total_tokens_used'],
            'paragraphs_processed': self.cost_tracker['paragraphs_processed'],
            'protected_content': self.cost_tracker['protected_content'],
            'average_quality': round(
                sum(self.stats['quality_scores']) / len(self.stats['quality_scores']), 2
            ) if self.stats['quality_scores'] else 0,
            'total_similarity_reduction': round(
                self.stats['total_similarity_reduction'] / max(1, self.cost_tracker['paragraphs_processed']), 2
            )
        }
    
    def process_all_documents(self, input_dir="documents", output_dir="completed"):
        """Process all documents from input directory"""
        print(f"🚀 Processing all documents from: {input_dir}")
        print(f"📁 Output directory: {output_dir}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all Word documents
        doc_patterns = ["*.docx", "*.doc"]
        doc_files = []
        
        for pattern in doc_patterns:
            doc_files.extend(glob.glob(os.path.join(input_dir, pattern)))
        
        if not doc_files:
            print(f"❌ No documents found in {input_dir}")
            return []
        
        print(f"📄 Found {len(doc_files)} documents to process")
        
        results = []
        for i, doc_path in enumerate(doc_files, 1):
            print(f"\n🔄 Processing document {i}/{len(doc_files)}: {Path(doc_path).name}")
            
            # Generate output path
            base_name = Path(doc_path).stem
            ext = Path(doc_path).suffix
            output_path = os.path.join(output_dir, f"{base_name}_paraphrased{ext}")
            
            # Process document
            result = self.process_document(doc_path, output_path)
            
            if result:
                result['input_file'] = doc_path
                result['document_number'] = i
                results.append(result)
                print(f"✅ Completed: {Path(output_path).name}")
            else:
                print(f"❌ Failed to process: {Path(doc_path).name}")
            
            # Add delay between documents to avoid rate limiting
            if i < len(doc_files):
                print("⏳ Waiting 3 seconds before next document...")
                time.sleep(3)
        
        # Generate summary report
        summary_report = self.generate_batch_summary(results, input_dir, output_dir)
        
        print(f"\n🎉 Batch processing completed!")
        print(f"✅ Processed: {len(results)}/{len(doc_files)} documents")
        print(f"📊 Summary report: {summary_report['report_path']}")
        
        return results
    
    def generate_batch_summary(self, results, input_dir, output_dir):
        """Generate summary report for batch processing"""
        summary = {
            'batch_info': {
                'input_directory': input_dir,
                'output_directory': output_dir,
                'total_documents': len(results),
                'processing_date': datetime.now().isoformat(),
                'total_processing_time': str(datetime.now() - self.stats['start_time'])
            },
            'aggregate_statistics': {
                'total_paragraphs_processed': sum(r['report']['summary']['total_paragraphs'] for r in results if 'report' in r),
                'total_api_calls': sum(r['report']['costs']['total_api_calls'] for r in results if 'report' in r),
                'total_tokens_used': sum(r['report']['costs']['total_tokens_used'] for r in results if 'report' in r),
                'total_protected_content': sum(r['report']['summary']['protected_content'] for r in results if 'report' in r),
                'average_similarity_reduction': round(
                    sum(r['report']['summary']['average_similarity_reduction'] for r in results if 'report' in r) / len(results), 2
                ) if results else 0,
                'average_quality_score': round(
                    sum(r['report']['summary']['average_quality_score'] for r in results if 'report' in r) / len(results), 2
                ) if results else 0
            },
            'document_results': [
                {
                    'filename': Path(r['input_file']).name,
                    'output_file': Path(r['output_path']).name,
                    'paragraphs': r['report']['summary']['total_paragraphs'],
                    'similarity_reduction': r['report']['summary']['average_similarity_reduction'],
                    'quality_score': r['report']['summary']['average_quality_score']
                } for r in results if 'report' in r
            ]
        }
        
        # Save batch summary
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(output_dir, f"batch_summary_{timestamp}.json")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return {
            'summary': summary,
            'report_path': report_path
        }

def main():
    """Main processing function"""
    try:
        # Initialize paraphraser
        print("🚀 Full Gemini AI Paraphraser System")
        print("=" * 50)
        
        paraphraser = FullGeminiParaphraser(synonym_file='sinonim.json')
        
        # Process all documents from documents/ folder
        results = paraphraser.process_all_documents(
            input_dir="documents",
            output_dir="completed"
        )
        
        if results:
            print("\n🎉 All documents processed successfully!")
            
            # Display final statistics
            final_stats = paraphraser.get_statistics()
            print("\n📈 Final Statistics:")
            for key, value in final_stats.items():
                print(f"   {key}: {value}")
        else:
            print("❌ No documents were processed successfully")
        
    except Exception as e:
        print(f"❌ Processing error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()