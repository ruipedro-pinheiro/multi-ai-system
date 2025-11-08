#!/usr/bin/env python3
"""Test SmartRouter - Verify intelligent AI selection"""
from orchestrator.smart_router import SmartRouter


def test_code_task():
    """Test: Code task should select Claude"""
    router = SmartRouter()
    
    message = "I need a Python script with crontab for backing up my database"
    available_ais = ['claude', 'gpt', 'gemini']
    
    selected = router.select_ais(message, available_ais)
    print(f"\n📝 Message: {message}")
    print(f"✅ Selected AIs: {selected}")
    
    explanation = router.explain_selection(message, selected)
    print(f"🧠 Intent: {explanation['intent']}")
    print(f"💡 Reasoning: {explanation['reasoning']}")
    
    # Code task should include Claude (code expert)
    assert 'claude' in selected, "Claude should be selected for code tasks"
    # Cron/backup keywords should include Gemini (sysadmin/infrastructure)
    assert 'gemini' in selected, "Gemini should be selected for cron/backup"
    print("✅ PASS: Code task correctly routed to Claude + Gemini\n")


def test_creative_task():
    """Test: Creative task should select GPT"""
    router = SmartRouter()
    
    message = "Help me write a creative blog post about AI collaboration"
    available_ais = ['claude', 'gpt', 'gemini']
    
    selected = router.select_ais(message, available_ais)
    print(f"📝 Message: {message}")
    print(f"✅ Selected AIs: {selected}")
    
    explanation = router.explain_selection(message, selected)
    print(f"🧠 Intent: {explanation['intent']}")
    print(f"💡 Reasoning: {explanation['reasoning']}")
    
    # Creative writing should include GPT
    assert 'gpt' in selected, "GPT should be selected for creative writing"
    print("✅ PASS: Creative task correctly routed to GPT\n")


def test_legal_compliance():
    """Test: Legal/RGPD should select Gemini"""
    router = SmartRouter()
    
    message = "Check if my backup strategy is RGPD compliant"
    available_ais = ['claude', 'gpt', 'gemini']
    
    selected = router.select_ais(message, available_ais)
    print(f"📝 Message: {message}")
    print(f"✅ Selected AIs: {selected}")
    
    explanation = router.explain_selection(message, selected)
    print(f"🧠 Intent: {explanation['intent']}")
    print(f"💡 Reasoning: {explanation['reasoning']}")
    
    # Legal/compliance should include Gemini
    assert 'gemini' in selected, "Gemini should be selected for legal/RGPD"
    print("✅ PASS: Legal task correctly routed to Gemini\n")


def test_multi_intent():
    """Test: Multi-intent message (code + legal + creative)"""
    router = SmartRouter()
    
    message = """
    I need help with:
    1. Writing a Python backup script
    2. Making sure it's RGPD compliant
    3. Suggesting creative alternatives to traditional cron jobs
    """
    available_ais = ['claude', 'gpt', 'gemini']
    
    selected = router.select_ais(message, available_ais, max_ais=3)
    print(f"📝 Message: {message[:80]}...")
    print(f"✅ Selected AIs: {selected}")
    
    explanation = router.explain_selection(message, selected)
    print(f"🧠 Intent: {explanation['intent']}")
    print(f"💡 Reasoning: {explanation['reasoning']}")
    
    # Multi-intent should select multiple AIs
    assert len(selected) >= 2, "Multi-intent should select at least 2 AIs"
    assert 'claude' in selected, "Should include Claude for code"
    assert 'gemini' in selected, "Should include Gemini for RGPD"
    print("✅ PASS: Multi-intent correctly routed to multiple AIs\n")


def test_limited_ais():
    """Test: Works with limited AI availability"""
    router = SmartRouter()
    
    message = "Write creative Python code"
    available_ais = ['claude']  # Only Claude available
    
    selected = router.select_ais(message, available_ais)
    print(f"📝 Message: {message}")
    print(f"🔒 Available: {available_ais}")
    print(f"✅ Selected AIs: {selected}")
    
    # Should still work with single AI
    assert len(selected) == 1, "Should select single AI when only one available"
    assert selected[0] == 'claude', "Should select the only available AI"
    print("✅ PASS: Gracefully handles limited AI availability\n")


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 TESTING SMART ROUTER - INTELLIGENT AI SELECTION")
    print("=" * 60)
    
    test_code_task()
    test_creative_task()
    test_legal_compliance()
    test_multi_intent()
    test_limited_ais()
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED! SmartRouter works correctly!")
    print("=" * 60)
