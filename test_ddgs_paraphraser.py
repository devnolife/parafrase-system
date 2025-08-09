#!/usr/bin/env python3
"""
Test script for Smart Efficient Paraphraser with DDGS functionality
"""

from smart_efficient_paraphraser import SmartEfficientParaphraser

def test_single_text_with_search():
    """Test paraphrasing a single text with search context"""
    print("🧪 Testing DDGS Enhanced Paraphrasing")
    print("=" * 50)
    
    # Initialize paraphraser
    paraphraser = SmartEfficientParaphraser(synonym_file='sinonim.json')
    
    # Test text (academic style)
    test_text = "Penelitian ini bertujuan untuk menganalisis dampak teknologi AI terhadap pendidikan modern."
    
    print(f"📝 Original text: {test_text}")
    print()
    
    # Test with search enabled
    print("🔍 Testing with search enabled:")
    result_with_search = paraphraser.paraphrase_text(test_text, use_search=True)
    
    print(f"✅ Paraphrased: {result_with_search['paraphrase']}")
    print(f"📊 Method used: {result_with_search['method']}")
    print(f"📈 Similarity: {result_with_search['similarity']}%")
    print(f"🎯 Search context: {result_with_search.get('search_context', 'None')}")
    print()
    
    # Test with search disabled for comparison
    print("🚫 Testing with search disabled:")
    result_without_search = paraphraser.paraphrase_text(test_text, use_search=False)
    
    print(f"✅ Paraphrased: {result_without_search['paraphrase']}")
    print(f"📊 Method used: {result_without_search['method']}")
    print(f"📈 Similarity: {result_without_search['similarity']}%")
    print()
    
    # Compare results
    print("🔍 Comparison:")
    print(f"Search context improved paraphrasing: {'Yes' if result_with_search['changes_made'] > result_without_search['changes_made'] else 'No'}")
    print(f"Changes with search: {result_with_search['changes_made']}")
    print(f"Changes without search: {result_without_search['changes_made']}")
    
    return True

def test_search_functionality():
    """Test the search functionality directly"""
    print("\n🔍 Testing Search Functionality")
    print("=" * 40)
    
    paraphraser = SmartEfficientParaphraser(synonym_file='sinonim.json')
    
    if not paraphraser.ddgs_available:
        print("❌ DDGS not available for testing")
        return False
    
    # Test search
    query = "teknologi AI pendidikan"
    print(f"🎯 Searching for: {query}")
    
    search_results = paraphraser.search_related_content(query)
    
    if search_results:
        print(f"✅ Found {len(search_results)} results")
        for i, result in enumerate(search_results[:2]):  # Show first 2
            print(f"  {i+1}. {result['title'][:50]}...")
            print(f"     Relevance: {result['relevance_score']}%")
            print(f"     Length: {result['content_length']} chars")
    else:
        print("❌ No search results found")
    
    return True

if __name__ == "__main__":
    try:
        test_search_functionality()
        test_single_text_with_search()
        print("\n🎉 Testing completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()