"""
XDev Prompt Module Refactoring Plan
Split prompt.py (2,748 lines) into focused modules
"""

from pathlib import Path

class PromptModuleRefactor:
    """Plan for splitting the massive prompt.py file"""
    
    REFACTOR_PLAN = {
        "prompt_basic.py": {
            "classes": ["PromptCombiner", "PromptWeighter", "PromptCleaner"],
            "description": "Basic prompt operations - combine, weight, clean",
            "target_category": "XDev/Prompt/Basic",
            "estimated_lines": 400
        },
        
        "prompt_analysis.py": {
            "classes": ["PromptAnalyzer", "PromptRandomizer"],
            "description": "Prompt analysis and randomization tools", 
            "target_category": "XDev/Prompt/Analysis",
            "estimated_lines": 350
        },
        
        "prompt_templates.py": {
            "classes": ["PersonBuilder", "StyleBuilder"],
            "description": "Template-based prompt builders",
            "target_category": "XDev/Prompt/Templates", 
            "estimated_lines": 600
        },
        
        "prompt_advanced.py": {
            "classes": ["PromptMatrix", "PromptInterpolator", "PromptScheduler", 
                       "PromptAttention", "PromptChainOfThought", "PromptFewShot"],
            "description": "Advanced prompt engineering techniques",
            "target_category": "XDev/Prompt/Advanced",
            "estimated_lines": 1000
        },
        
        "prompt_llm_enhanced.py": {
            "classes": ["LLMPersonBuilder", "LLMStyleBuilder"],
            "description": "LLM-enhanced prompt generation tools",
            "target_category": "XDev/LLM/Character",
            "estimated_lines": 400
        }
    }
    
    @classmethod
    def print_refactor_plan(cls):
        """Print the refactoring plan"""
        print("🔧 PROMPT.PY REFACTORING PLAN")
        print("=" * 50)
        
        total_estimated = 0
        for filename, details in cls.REFACTOR_PLAN.items():
            total_estimated += details["estimated_lines"]
            print(f"\n📁 {filename}")
            print(f"   Classes: {', '.join(details['classes'])}")
            print(f"   Purpose: {details['description']}")
            print(f"   Category: {details['target_category']}")
            print(f"   Est. Lines: {details['estimated_lines']}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Original: 2,748 lines (1 file)")
        print(f"   Refactored: ~{total_estimated} lines ({len(cls.REFACTOR_PLAN)} files)")
        print(f"   Reduction: ~{2748 - total_estimated} lines ({((2748 - total_estimated) / 2748 * 100):.1f}%)")

if __name__ == "__main__":
    PromptModuleRefactor.print_refactor_plan()