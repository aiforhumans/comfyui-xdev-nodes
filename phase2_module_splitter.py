#!/usr/bin/env python3
"""
Phase 2B Automated Module Splitter
Intelligently splits large monolithic files into focused modules
"""

import re
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Set
import shutil

class ModuleSplitter:
    """Automated tool for splitting large node files into focused modules"""
    
    def __init__(self):
        # Class line ranges based on actual file analysis
        self.prompt_class_ranges = {
            "PromptCombiner": (14, 109),
            "PromptWeighter": (110, 254), 
            "PromptCleaner": (255, 412),
            "PromptAnalyzer": (413, 548),
            "PromptRandomizer": (549, 739),
            "PersonBuilder": (740, 941),
            "StyleBuilder": (942, 1187),
            "PromptMatrix": (1188, 1304),
            "PromptInterpolator": (1305, 1457),
            "PromptScheduler": (1458, 1591),
            "PromptAttention": (1592, 1779),
            "PromptChainOfThought": (1780, 1986),
            "PromptFewShot": (1987, 2230),
            "LLMPersonBuilder": (2231, 2523),
            "LLMStyleBuilder": (2524, 2794)
        }
        
        self.splitting_config = {
            "prompt.py": {
                "target_dir": "xdev_nodes/nodes/prompt",
                "modules": {
                    "prompt_core.py": {
                        "description": "Core prompt combination and weighting functionality",
                        "classes": ["PromptCombiner", "PromptWeighter", "PromptCleaner", "PromptAnalyzer", "PromptRandomizer"]
                    },
                    "prompt_builders.py": {
                        "description": "Template builders for persons and styles", 
                        "classes": ["PersonBuilder", "StyleBuilder", "PromptMatrix", "PromptInterpolator"]
                    },
                    "prompt_advanced.py": {
                        "description": "Advanced prompt engineering techniques",
                        "classes": ["PromptScheduler", "PromptAttention", "PromptChainOfThought", "PromptFewShot"]
                    },
                    "prompt_llm.py": {
                        "description": "LLM-enhanced prompt building tools",
                        "classes": ["LLMPersonBuilder", "LLMStyleBuilder"]
                    }
                }
            },
            
            "image.py": {
                "target_dir": "xdev_nodes/nodes/image", 
                "modules": {
                    "image_manipulation.py": {
                        "description": "Core image manipulation operations",
                        "node_patterns": [
                            r"class ImageResize\b",
                            r"class ImageCrop\b",
                            r"class ImageRotate\b",
                            r"class ImageBlend\b"
                        ]
                    },
                    "image_analysis.py": {
                        "description": "Image analysis and selection tools",
                        "node_patterns": [
                            r"class PickByBrightness\b"
                        ]
                    },
                    "image_tiling.py": {
                        "description": "Image splitting and tiling operations",
                        "node_patterns": [
                            r"class ImageSplit\b",
                            r"class ImageTile\b"
                        ]
                    }
                }
            }
        }
        
        self.backup_dir = Path("backups/phase2")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def split_file(self, source_file: str) -> Dict[str, any]:
        """Split a large file into focused modules"""
        
        if source_file not in self.splitting_config:
            return {"success": False, "error": f"No splitting config for {source_file}"}
        
        source_path = Path(f"xdev_nodes/nodes/{source_file}")
        if not source_path.exists():
            return {"success": False, "error": f"Source file {source_path} not found"}
        
        config = self.splitting_config[source_file]
        
        print(f"🔧 SPLITTING: {source_file}")
        print(f"📂 Target directory: {config['target_dir']}")
        print(f"📄 Modules to create: {len(config['modules'])}")
        
        # Backup original file
        backup_path = self.backup_dir / source_file
        shutil.copy2(source_path, backup_path)
        print(f"📁 Backup created: {backup_path}")
        
        # Read source content
        source_content = source_path.read_text(encoding='utf-8')
        
        # Extract common imports and utilities
        imports_section = self._extract_imports_section(source_content)
        
        # Split into modules
        results = {}
        for module_name, module_config in config["modules"].items():
            module_path = Path(config["target_dir"]) / module_name
            
            print(f"\n📝 Creating {module_name}:")
            print(f"   📋 {module_config['description']}")
            
            # Extract nodes for this module
            module_content = self._extract_module_content(
                source_content, 
                module_config,
                imports_section,
                module_config["description"]
            )
            
            # Write module file
            module_path.write_text(module_content, encoding='utf-8')
            
            # Count nodes in module
            node_count = len(module_config.get("classes", module_config.get("node_patterns", [])))
            print(f"   ✅ Created with {node_count} nodes")
            
            results[module_name] = {
                "path": str(module_path),
                "node_count": node_count,
                "description": module_config["description"]
            }
        
        return {
            "success": True,
            "source_file": source_file,
            "modules_created": results,
            "backup_location": str(backup_path)
        }
    
    def _extract_imports_section(self, content: str) -> str:
        """Extract import statements and common utilities"""
        lines = content.split('\n')
        imports = []
        in_imports = True
        
        for line in lines:
            stripped = line.strip()
            
            # Include imports, from statements, and initial comments
            if (stripped.startswith(('import ', 'from ', '#', '"""', "'''")) or 
                stripped == '' or
                stripped.startswith('sys.path') or
                stripped.startswith('__')):
                if in_imports:
                    imports.append(line)
            elif stripped.startswith('class ') and 'ValidationMixin' not in stripped:
                # Stop at first class definition (but allow ValidationMixin)
                in_imports = False
                break
            else:
                imports.append(line)
        
        return '\n'.join(imports)
    
    def _extract_module_content(self, source_content: str, module_config: Dict, 
                              imports_section: str, description: str) -> str:
        """Extract specific nodes and create module content"""
        
        # Start with imports and header
        module_lines = [
            f'"""',
            f'{description}',
            f'Part of the XDev Nodes modular architecture.',
            f'"""',
            f'',
            imports_section,
            f'',
            f'# ===== MODULE CONTENT ====='
        ]
        
        # Extract each class by line range (if available)
        if hasattr(self, 'prompt_class_ranges') and 'classes' in module_config:
            classes = module_config['classes']
            source_lines = source_content.split('\n')
            
            for class_name in classes:
                if class_name in self.prompt_class_ranges:
                    start_line, end_line = self.prompt_class_ranges[class_name]
                    # Convert to 0-based indexing
                    class_content = '\n'.join(source_lines[start_line-1:end_line])
                    
                    module_lines.extend([
                        '',
                        f'# ----- {class_name} -----',
                        class_content,
                        ''
                    ])
        else:
            # Fallback to pattern matching for other files
            node_patterns = module_config.get('node_patterns', [])
            for pattern in node_patterns:
                node_class = self._extract_class_definition(source_content, pattern)
                if node_class:
                    module_lines.extend([
                        '',
                        f'# ----- {pattern.replace("class ", "").replace("\\b", "")} -----',
                        node_class,
                        ''
                    ])
        
        return '\n'.join(module_lines)
    
    def _extract_class_definition(self, content: str, class_pattern: str) -> str:
        """Extract a complete class definition including all methods"""
        
        # Find the class start
        match = re.search(class_pattern, content, re.MULTILINE)
        if not match:
            return ""
        
        lines = content.split('\n')
        start_line = content[:match.start()].count('\n')
        
        # Find class boundaries - improved logic
        class_lines = []
        in_class = False
        base_indent = None
        found_class_start = False
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            
            # Check if this is our target class
            if re.search(class_pattern, line):
                in_class = True
                found_class_start = True
                base_indent = len(line) - len(line.lstrip())
                class_lines.append(line)
                continue
            
            if in_class and found_class_start:
                current_indent = len(line) - len(line.lstrip())
                
                # Continue if: empty line, comment, docstring, or indented more than class
                if (not line.strip() or  # Empty line
                    line.strip().startswith('#') or  # Comment
                    line.strip().startswith(('"""', "'''")) or  # Docstring
                    current_indent > base_indent or  # Indented content
                    line.strip().startswith('@')):  # Decorator for next class
                    class_lines.append(line)
                    continue
                
                # Check if we've hit another class or function at same level
                if (line.strip() and current_indent <= base_indent and 
                    (line.strip().startswith('class ') or 
                     line.strip().startswith('def ') or
                     line.strip().startswith('NODE_CLASS_MAPPINGS'))):
                    break
                
                # Otherwise include the line
                class_lines.append(line)
        
        return '\n'.join(class_lines)
    
    def cleanup_previous_split(self, source_file: str) -> None:
        """Remove previously generated modules for clean retry"""
        if source_file not in self.splitting_config:
            return
        
        config = self.splitting_config[source_file]
        target_dir = Path(config["target_dir"])
        
        if target_dir.exists():
            print(f"🧹 Cleaning previous split: {target_dir}")
            for module_name in config["modules"].keys():
                module_path = target_dir / module_name
                if module_path.exists():
                    module_path.unlink()
                    print(f"   🗑️ Removed {module_name}")

    def split_prompt_module(self) -> Dict[str, any]:
        """Split the prompt.py module (Phase 2B priority)"""
        print("🚀 PHASE 2B: PROMPT MODULE SPLITTING")
        print("=" * 60)
        
        # Clean up previous attempt
        self.cleanup_previous_split("prompt.py")
        
        return self.split_file("prompt.py")
    
    def split_image_module(self) -> Dict[str, any]:
        """Split the image.py module"""
        print("🚀 PHASE 2E: IMAGE MODULE SPLITTING") 
        print("=" * 60)
        return self.split_file("image.py")
    
    def validate_split_results(self, split_results: Dict[str, any]) -> Dict[str, any]:
        """Validate that the split was successful"""
        if not split_results["success"]:
            return split_results
        
        validation_results = {
            "validation_passed": True,
            "issues": [],
            "module_validations": {}
        }
        
        for module_name, module_info in split_results["modules_created"].items():
            module_path = Path(module_info["path"])
            
            # Check if file was created
            if not module_path.exists():
                validation_results["issues"].append(f"Module {module_name} not created")
                validation_results["validation_passed"] = False
                continue
            
            # Check if file has content
            content = module_path.read_text(encoding='utf-8')
            line_count = len(content.split('\n'))
            
            if line_count < 20:  # Minimum reasonable file size
                validation_results["issues"].append(f"Module {module_name} too small ({line_count} lines)")
                validation_results["validation_passed"] = False
            
            # Check for class definitions
            class_count = len(re.findall(r'^class \w+', content, re.MULTILINE))
            
            validation_results["module_validations"][module_name] = {
                "exists": module_path.exists(),
                "line_count": line_count,
                "class_count": class_count,
                "size_kb": round(len(content) / 1024, 1)
            }
        
        return validation_results

def main():
    """Execute Phase 2B automated module splitting"""
    splitter = ModuleSplitter()
    
    print("🤖 AUTOMATED MODULE SPLITTER - PHASE 2B")
    print("=" * 70)
    print("📋 Starting with highest priority: prompt.py (2,794 lines)")
    
    # Split prompt module (highest priority)
    prompt_results = splitter.split_prompt_module()
    
    if prompt_results["success"]:
        print(f"\n✅ PROMPT SPLITTING SUCCESSFUL")
        print(f"📁 Modules created: {len(prompt_results['modules_created'])}")
        
        # Validate results
        validation = splitter.validate_split_results(prompt_results)
        
        print(f"\n🔍 VALIDATION RESULTS:")
        if validation["validation_passed"]:
            print("✅ All validations passed")
        else:
            print("⚠️ Validation issues found:")
            for issue in validation["issues"]:
                print(f"  • {issue}")
        
        print(f"\n📊 MODULE SUMMARY:")
        for module_name, validation_info in validation["module_validations"].items():
            print(f"  📄 {module_name}:")
            print(f"    📏 Lines: {validation_info['line_count']}")
            print(f"    🏗️ Classes: {validation_info['class_count']}")
            print(f"    💾 Size: {validation_info['size_kb']} KB")
    
    else:
        print(f"❌ PROMPT SPLITTING FAILED: {prompt_results['error']}")
    
    print(f"\n🎯 PHASE 2B STATUS: {'COMPLETE' if prompt_results['success'] else 'FAILED'}")
    return prompt_results["success"]

if __name__ == "__main__":
    main()