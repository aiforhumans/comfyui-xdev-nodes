"""
Prompt Versioning and A/B Testing Framework for XDev Framework
Professional prompt management with version control, A/B testing, and performance analytics
"""

import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, Counter
from ...performance import performance_monitor, cached_operation
from ...mixins import ValidationMixin
from ...categories import NodeCategories

@dataclass
class PromptVersion:
    """Individual prompt version with metadata"""
    version_id: str
    prompt_text: str
    title: str
    description: str
    created_date: str
    author: str
    tags: List[str] = field(default_factory=list)
    parent_version: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    usage_count: int = 0
    rating: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ABTestResult:
    """A/B test result data"""
    test_id: str
    variant_a: str
    variant_b: str
    variant_a_score: float
    variant_b_score: float
    sample_size: int
    confidence_level: float
    winner: str
    improvement: float
    test_duration: str
    notes: str = ""

class XDEV_PromptVersionControl(ValidationMixin):
    """
    Professional prompt version control system with branching, merging, and history tracking.
    Manages prompt evolution and maintains complete revision history.
    """
    
    DISPLAY_NAME = "Prompt Version Control (XDev)"
    
    # In-memory storage (in real implementation, this would be persistent)
    _prompt_repository = {}
    _version_history = defaultdict(list)
    _branches = defaultdict(list)
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "action": (["create", "update", "branch", "merge", "history", "compare"], {"default": "create", "tooltip": "Version control action"}),
                "prompt_id": ("STRING", {"default": "", "tooltip": "Unique prompt identifier"}),
                "prompt_text": ("STRING", {"default": "", "multiline": True, "tooltip": "Prompt content"}),
            },
            "optional": {
                "version_title": ("STRING", {"default": "", "tooltip": "Version title/name"}),
                "version_description": ("STRING", {"default": "", "multiline": True, "tooltip": "Version description"}),
                "author": ("STRING", {"default": "XDev User", "tooltip": "Author name"}),
                "tags": ("STRING", {"default": "", "tooltip": "Comma-separated tags"}),
                "parent_version": ("STRING", {"default": "", "tooltip": "Parent version ID for branching"}),
                "branch_name": ("STRING", {"default": "main", "tooltip": "Branch name"}),
                "merge_strategy": (["auto", "manual", "favor_current", "favor_incoming"], {"default": "auto", "tooltip": "Merge strategy"}),
                "performance_score": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "tooltip": "Performance rating"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("result_prompt", "version_info", "operation_log", "repository_status")
    FUNCTION = "manage_versions"
    CATEGORY = f"{NodeCategories.PROMPTS}/Management"
    DESCRIPTION = "Professional prompt version control with branching and history tracking"
    
    @performance_monitor("version_control")
    @cached_operation(ttl=60)  # Shorter TTL for version control operations
    def manage_versions(self, action, prompt_id, prompt_text, version_title="", version_description="",
                       author="XDev User", tags="", parent_version="", branch_name="main",
                       merge_strategy="auto", performance_score=0.0, validate_input=True):
        
        if validate_input and not prompt_id.strip():
            return ("", "Error: Prompt ID is required", "", "")
        
        try:
            operation_log = []
            
            if action == "create":
                result = self._create_version(prompt_id, prompt_text, version_title, version_description,
                                            author, tags, branch_name, performance_score, operation_log)
            elif action == "update":
                result = self._update_version(prompt_id, prompt_text, version_title, version_description,
                                            author, tags, performance_score, operation_log)
            elif action == "branch":
                result = self._create_branch(prompt_id, parent_version, branch_name, operation_log)
            elif action == "merge":
                result = self._merge_branches(prompt_id, branch_name, merge_strategy, operation_log)
            elif action == "history":
                result = self._get_history(prompt_id, operation_log)
            elif action == "compare":
                result = self._compare_versions(prompt_id, parent_version, operation_log)
            else:
                return ("", f"Error: Unknown action '{action}'", "", "")
            
            # Generate status reports
            version_info = self._generate_version_info(prompt_id)
            repository_status = self._generate_repository_status()
            operation_report = "\\n".join(operation_log)
            
            return (result, version_info, operation_report, repository_status)
            
        except Exception as e:
            return ("", f"Error: {str(e)}", "", "")
    
    def _create_version(self, prompt_id: str, prompt_text: str, title: str, description: str,
                       author: str, tags: str, branch: str, score: float, log: List[str]) -> str:
        """Create new prompt version"""
        version_id = self._generate_version_id(prompt_id, prompt_text)
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Create version
        version = PromptVersion(
            version_id=version_id,
            prompt_text=prompt_text,
            title=title or f"Version {len(self._version_history[prompt_id]) + 1}",
            description=description,
            created_date=datetime.now().isoformat(),
            author=author,
            tags=tag_list,
            performance_metrics={"user_rating": score} if score > 0 else {},
            rating=score
        )
        
        # Store version
        self._prompt_repository[version_id] = version
        self._version_history[prompt_id].append(version_id)
        
        if branch not in self._branches[prompt_id]:
            self._branches[prompt_id].append(branch)
        
        log.append(f"Created version {version_id} for prompt {prompt_id}")
        log.append(f"Branch: {branch}")
        log.append(f"Author: {author}")
        
        return prompt_text
    
    def _update_version(self, prompt_id: str, prompt_text: str, title: str, description: str,
                       author: str, tags: str, score: float, log: List[str]) -> str:
        """Update existing prompt version"""
        # Get latest version
        if prompt_id not in self._version_history or not self._version_history[prompt_id]:
            return self._create_version(prompt_id, prompt_text, title, description, author, tags, "main", score, log)
        
        latest_version_id = self._version_history[prompt_id][-1]
        latest_version = self._prompt_repository[latest_version_id]
        
        # Create new version based on update
        new_version_id = self._generate_version_id(prompt_id, prompt_text)
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        updated_version = PromptVersion(
            version_id=new_version_id,
            prompt_text=prompt_text,
            title=title or latest_version.title,
            description=description or latest_version.description,
            created_date=datetime.now().isoformat(),
            author=author,
            tags=tag_list or latest_version.tags,
            parent_version=latest_version_id,
            performance_metrics={"user_rating": score} if score > 0 else latest_version.performance_metrics,
            rating=score or latest_version.rating
        )
        
        # Store updated version
        self._prompt_repository[new_version_id] = updated_version
        self._version_history[prompt_id].append(new_version_id)
        
        log.append(f"Updated prompt {prompt_id} with new version {new_version_id}")
        log.append(f"Previous version: {latest_version_id}")
        
        return prompt_text
    
    def _create_branch(self, prompt_id: str, parent_version: str, branch_name: str, log: List[str]) -> str:
        """Create new branch from existing version"""
        if not parent_version and prompt_id in self._version_history:
            parent_version = self._version_history[prompt_id][-1]
        
        if not parent_version or parent_version not in self._prompt_repository:
            log.append(f"Error: Parent version {parent_version} not found")
            return ""
        
        parent = self._prompt_repository[parent_version]
        
        # Create branch entry
        if branch_name not in self._branches[prompt_id]:
            self._branches[prompt_id].append(branch_name)
        
        log.append(f"Created branch '{branch_name}' from version {parent_version}")
        log.append(f"Prompt: {prompt_id}")
        
        return parent.prompt_text
    
    def _merge_branches(self, prompt_id: str, source_branch: str, strategy: str, log: List[str]) -> str:
        """Merge branches using specified strategy"""
        if prompt_id not in self._version_history or len(self._version_history[prompt_id]) < 2:
            log.append("Error: Not enough versions to merge")
            return ""
        
        # Get latest versions (simplified merge)
        versions = self._version_history[prompt_id]
        if len(versions) < 2:
            log.append("Error: Need at least 2 versions to merge")
            return ""
        
        current_version = self._prompt_repository[versions[-1]]
        previous_version = self._prompt_repository[versions[-2]]
        
        if strategy == "favor_current":
            merged_text = current_version.prompt_text
        elif strategy == "favor_incoming":
            merged_text = previous_version.prompt_text
        else:
            # Auto merge - combine both
            merged_text = f"{current_version.prompt_text}, {previous_version.prompt_text}"
        
        log.append(f"Merged branch '{source_branch}' using strategy '{strategy}'")
        log.append(f"Result length: {len(merged_text)} characters")
        
        return merged_text
    
    def _get_history(self, prompt_id: str, log: List[str]) -> str:
        """Get version history for prompt"""
        if prompt_id not in self._version_history:
            log.append(f"No history found for prompt {prompt_id}")
            return ""
        
        versions = self._version_history[prompt_id]
        if not versions:
            return ""
        
        # Return latest version text
        latest_version = self._prompt_repository[versions[-1]]
        
        log.append(f"Retrieved history for prompt {prompt_id}")
        log.append(f"Total versions: {len(versions)}")
        log.append(f"Latest version: {latest_version.version_id}")
        
        return latest_version.prompt_text
    
    def _compare_versions(self, prompt_id: str, version_a: str, log: List[str]) -> str:
        """Compare two versions"""
        if prompt_id not in self._version_history:
            log.append(f"No versions found for prompt {prompt_id}")
            return ""
        
        versions = self._version_history[prompt_id]
        if len(versions) < 2:
            log.append("Need at least 2 versions to compare")
            return ""
        
        # Get versions to compare
        if version_a and version_a in self._prompt_repository:
            version_1 = self._prompt_repository[version_a]
        else:
            version_1 = self._prompt_repository[versions[-2]]
        
        version_2 = self._prompt_repository[versions[-1]]
        
        # Simple comparison result
        comparison_result = f"COMPARISON:\\nVersion 1: {version_1.title}\\nVersion 2: {version_2.title}\\n"
        comparison_result += f"Length diff: {len(version_2.prompt_text) - len(version_1.prompt_text)} chars\\n"
        comparison_result += f"Rating diff: {version_2.rating - version_1.rating:.1f}"
        
        log.append(f"Compared versions for prompt {prompt_id}")
        log.append(f"Version 1: {version_1.version_id}")
        log.append(f"Version 2: {version_2.version_id}")
        
        return version_2.prompt_text
    
    def _generate_version_id(self, prompt_id: str, prompt_text: str) -> str:
        """Generate unique version ID"""
        content_hash = hashlib.md5(prompt_text.encode()).hexdigest()[:8]
        timestamp = str(int(time.time()))[-6:]
        return f"{prompt_id}_{timestamp}_{content_hash}"
    
    def _generate_version_info(self, prompt_id: str) -> str:
        """Generate version information"""
        if prompt_id not in self._version_history:
            return f"No versions found for {prompt_id}"
        
        versions = self._version_history[prompt_id]
        if not versions:
            return f"No versions found for {prompt_id}"
        
        latest_version = self._prompt_repository[versions[-1]]
        
        info = f"PROMPT: {prompt_id}\\n"
        info += f"Total Versions: {len(versions)}\\n"
        info += f"Current Version: {latest_version.version_id}\\n"
        info += f"Title: {latest_version.title}\\n"
        info += f"Author: {latest_version.author}\\n"
        info += f"Created: {latest_version.created_date}\\n"
        info += f"Rating: {latest_version.rating:.1f}/10\\n"
        
        if latest_version.tags:
            info += f"Tags: {', '.join(latest_version.tags)}\\n"
        
        return info
    
    def _generate_repository_status(self) -> str:
        """Generate repository status"""
        total_prompts = len(self._version_history)
        total_versions = sum(len(versions) for versions in self._version_history.values())
        total_branches = sum(len(branches) for branches in self._branches.values())
        
        status = f"REPOSITORY STATUS:\\n"
        status += f"Total Prompts: {total_prompts}\\n"
        status += f"Total Versions: {total_versions}\\n"
        status += f"Total Branches: {total_branches}\\n"
        
        if self._prompt_repository:
            avg_rating = sum(v.rating for v in self._prompt_repository.values() if v.rating > 0) / max(1, len([v for v in self._prompt_repository.values() if v.rating > 0]))
            status += f"Average Rating: {avg_rating:.1f}/10\\n"
        
        return status

class XDEV_ABTestManager(ValidationMixin):
    """
    Advanced A/B testing system for prompt optimization with statistical analysis.
    Compares prompt variants and provides performance insights.
    """
    
    DISPLAY_NAME = "A/B Test Manager (XDev)"
    
    # Test storage
    _active_tests = {}
    _test_results = {}
    _test_history = defaultdict(list)
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "action": (["create_test", "log_result", "analyze", "compare", "report"], {"default": "create_test", "tooltip": "A/B test action"}),
                "test_id": ("STRING", {"default": "", "tooltip": "Unique test identifier"}),
                "variant_a": ("STRING", {"default": "", "multiline": True, "tooltip": "Prompt variant A"}),
                "variant_b": ("STRING", {"default": "", "multiline": True, "tooltip": "Prompt variant B"}),
            },
            "optional": {
                "test_name": ("STRING", {"default": "", "tooltip": "Test name/title"}),
                "test_description": ("STRING", {"default": "", "multiline": True, "tooltip": "Test description"}),
                "variant_a_score": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "tooltip": "Variant A performance score"}),
                "variant_b_score": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "tooltip": "Variant B performance score"}),
                "sample_size": ("INT", {"default": 1, "min": 1, "max": 1000, "tooltip": "Number of test samples"}),
                "confidence_level": ("FLOAT", {"default": 0.95, "min": 0.5, "max": 0.99, "step": 0.01, "tooltip": "Statistical confidence level"}),
                "test_duration_days": ("INT", {"default": 7, "min": 1, "max": 30, "tooltip": "Test duration in days"}),
                "metric_type": (["user_rating", "performance", "effectiveness", "quality"], {"default": "user_rating", "tooltip": "Primary metric"}),
                "notes": ("STRING", {"default": "", "multiline": True, "tooltip": "Test notes"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "BOOLEAN")
    RETURN_NAMES = ("winning_prompt", "test_analysis", "statistical_report", "test_complete")
    FUNCTION = "manage_ab_test"
    CATEGORY = f"{NodeCategories.PROMPTS}/Management"
    DESCRIPTION = "Advanced A/B testing system for prompt optimization"
    
    @performance_monitor("ab_testing")
    @cached_operation(ttl=60)
    def manage_ab_test(self, action, test_id, variant_a, variant_b, test_name="", test_description="",
                      variant_a_score=0.0, variant_b_score=0.0, sample_size=1, confidence_level=0.95,
                      test_duration_days=7, metric_type="user_rating", notes="", validate_input=True):
        
        if validate_input and not test_id.strip():
            return ("", "Error: Test ID is required", "", False)
        
        try:
            if action == "create_test":
                result = self._create_ab_test(test_id, variant_a, variant_b, test_name, test_description,
                                            test_duration_days, metric_type, notes)
                
            elif action == "log_result":
                result = self._log_test_result(test_id, variant_a_score, variant_b_score, sample_size, notes)
                
            elif action == "analyze":
                result = self._analyze_test(test_id, confidence_level)
                
            elif action == "compare":
                result = self._compare_variants(test_id, variant_a, variant_b)
                
            elif action == "report":
                result = self._generate_test_report(test_id)
                
            else:
                return ("", f"Error: Unknown action '{action}'", "", False)
            
            # Generate analysis and reports
            test_analysis = self._generate_test_analysis(test_id)
            statistical_report = self._generate_statistical_report(test_id, confidence_level)
            test_complete = self._is_test_complete(test_id)
            
            return (result, test_analysis, statistical_report, test_complete)
            
        except Exception as e:
            return ("", f"Error: {str(e)}", "", False)
    
    def _create_ab_test(self, test_id: str, variant_a: str, variant_b: str, name: str,
                       description: str, duration_days: int, metric_type: str, notes: str) -> str:
        """Create new A/B test"""
        test_data = {
            "test_id": test_id,
            "name": name or f"Test {test_id}",
            "description": description,
            "variant_a": variant_a,
            "variant_b": variant_b,
            "created_date": datetime.now().isoformat(),
            "duration_days": duration_days,
            "metric_type": metric_type,
            "notes": notes,
            "results": [],
            "status": "active"
        }
        
        self._active_tests[test_id] = test_data
        return variant_a  # Return first variant to start with
    
    def _log_test_result(self, test_id: str, score_a: float, score_b: float, samples: int, notes: str) -> str:
        """Log test result data"""
        if test_id not in self._active_tests:
            return ""
        
        test_data = self._active_tests[test_id]
        
        result_entry = {
            "timestamp": datetime.now().isoformat(),
            "variant_a_score": score_a,
            "variant_b_score": score_b,
            "sample_size": samples,
            "notes": notes
        }
        
        test_data["results"].append(result_entry)
        
        # Return current winning variant
        if score_a > score_b:
            return test_data["variant_a"]
        else:
            return test_data["variant_b"]
    
    def _analyze_test(self, test_id: str, confidence_level: float) -> str:
        """Analyze test results and determine winner"""
        if test_id not in self._active_tests:
            return ""
        
        test_data = self._active_tests[test_id]
        results = test_data["results"]
        
        if not results:
            return test_data["variant_a"]  # Default to first variant
        
        # Calculate averages
        avg_a = sum(r["variant_a_score"] for r in results) / len(results)
        avg_b = sum(r["variant_b_score"] for r in results) / len(results)
        total_samples = sum(r["sample_size"] for r in results)
        
        # Determine winner
        if avg_a > avg_b:
            winner = "variant_a"
            improvement = ((avg_a - avg_b) / max(avg_b, 0.1)) * 100
            winning_prompt = test_data["variant_a"]
        else:
            winner = "variant_b"
            improvement = ((avg_b - avg_a) / max(avg_a, 0.1)) * 100
            winning_prompt = test_data["variant_b"]
        
        # Calculate confidence (simplified)
        confidence = min(0.99, confidence_level + (total_samples / 100) * 0.1)
        
        # Store result
        test_result = ABTestResult(
            test_id=test_id,
            variant_a=test_data["variant_a"][:50] + "...",
            variant_b=test_data["variant_b"][:50] + "...",
            variant_a_score=avg_a,
            variant_b_score=avg_b,
            sample_size=total_samples,
            confidence_level=confidence,
            winner=winner,
            improvement=improvement,
            test_duration=f"{len(results)} sessions",
            notes=f"Analysis completed at {confidence:.1%} confidence"
        )
        
        self._test_results[test_id] = test_result
        self._test_history[test_id].append(test_result)
        
        return winning_prompt
    
    def _compare_variants(self, test_id: str, variant_a: str, variant_b: str) -> str:
        """Compare two variants directly"""
        # Simple comparison metrics
        len_diff = len(variant_b) - len(variant_a)
        word_diff = len(variant_b.split()) - len(variant_a.split())
        
        # Return the longer variant as potentially more detailed
        if len_diff > 10:
            return variant_b
        elif len_diff < -10:
            return variant_a
        else:
            return variant_a  # Default to first variant if similar
    
    def _generate_test_report(self, test_id: str) -> str:
        """Generate comprehensive test report"""
        if test_id not in self._active_tests:
            return ""
        
        test_data = self._active_tests[test_id]
        
        if test_id in self._test_results:
            result = self._test_results[test_id]
            return f"Test completed. Winner: {result.winner} with {result.improvement:.1f}% improvement"
        else:
            return f"Test in progress. {len(test_data['results'])} results logged."
    
    def _generate_test_analysis(self, test_id: str) -> str:
        """Generate test analysis"""
        if test_id not in self._active_tests:
            return f"Test {test_id} not found"
        
        test_data = self._active_tests[test_id]
        results = test_data["results"]
        
        analysis = f"TEST ANALYSIS: {test_data['name']}\\n"
        analysis += f"{'='*40}\\n\\n"
        analysis += f"Test ID: {test_id}\\n"
        analysis += f"Status: {test_data['status']}\\n"
        analysis += f"Metric Type: {test_data['metric_type']}\\n"
        analysis += f"Results Logged: {len(results)}\\n"
        
        if results:
            avg_a = sum(r["variant_a_score"] for r in results) / len(results)
            avg_b = sum(r["variant_b_score"] for r in results) / len(results)
            total_samples = sum(r["sample_size"] for r in results)
            
            analysis += f"\\nPERFORMANCE:\\n"
            analysis += f"Variant A Average: {avg_a:.2f}\\n"
            analysis += f"Variant B Average: {avg_b:.2f}\\n"
            analysis += f"Total Samples: {total_samples}\\n"
            analysis += f"Performance Difference: {abs(avg_a - avg_b):.2f}\\n"
            
            if avg_a > avg_b:
                analysis += f"Current Leader: Variant A (+{((avg_a - avg_b) / max(avg_b, 0.1)) * 100:.1f}%)\\n"
            else:
                analysis += f"Current Leader: Variant B (+{((avg_b - avg_a) / max(avg_a, 0.1)) * 100:.1f}%)\\n"
        
        return analysis
    
    def _generate_statistical_report(self, test_id: str, confidence_level: float) -> str:
        """Generate statistical analysis report"""
        if test_id not in self._active_tests:
            return f"No statistical data for test {test_id}"
        
        test_data = self._active_tests[test_id]
        results = test_data["results"]
        
        if not results:
            return "No results to analyze"
        
        # Calculate statistics
        scores_a = [r["variant_a_score"] for r in results]
        scores_b = [r["variant_b_score"] for r in results]
        
        avg_a = sum(scores_a) / len(scores_a)
        avg_b = sum(scores_b) / len(scores_b)
        
        # Simple variance calculation
        var_a = sum((x - avg_a) ** 2 for x in scores_a) / max(len(scores_a) - 1, 1)
        var_b = sum((x - avg_b) ** 2 for x in scores_b) / max(len(scores_b) - 1, 1)
        
        report = f"STATISTICAL REPORT\\n"
        report += f"{'='*30}\\n\\n"
        report += f"Confidence Level: {confidence_level:.1%}\\n"
        report += f"Sample Size: {len(results)}\\n\\n"
        
        report += f"VARIANT A STATISTICS:\\n"
        report += f"Mean: {avg_a:.3f}\\n"
        report += f"Variance: {var_a:.3f}\\n"
        report += f"Min: {min(scores_a):.2f}\\n"
        report += f"Max: {max(scores_a):.2f}\\n\\n"
        
        report += f"VARIANT B STATISTICS:\\n"
        report += f"Mean: {avg_b:.3f}\\n"
        report += f"Variance: {var_b:.3f}\\n"
        report += f"Min: {min(scores_b):.2f}\\n"
        report += f"Max: {max(scores_b):.2f}\\n\\n"
        
        # Significance test (simplified)
        effect_size = abs(avg_a - avg_b) / max(0.1, (var_a + var_b) / 2)
        significance = "High" if effect_size > 0.8 else "Medium" if effect_size > 0.5 else "Low"
        
        report += f"SIGNIFICANCE:\\n"
        report += f"Effect Size: {effect_size:.3f}\\n"
        report += f"Significance: {significance}\\n"
        
        return report
    
    def _is_test_complete(self, test_id: str) -> bool:
        """Check if test is complete"""
        if test_id not in self._active_tests:
            return False
        
        test_data = self._active_tests[test_id]
        results = test_data["results"]
        
        # Simple completion criteria
        return len(results) >= 5 and test_id in self._test_results

class XDEV_PromptAnalytics(ValidationMixin):
    """
    Advanced prompt analytics and performance tracking system.
    Provides insights into prompt effectiveness and usage patterns.
    """
    
    DISPLAY_NAME = "Prompt Analytics (XDev)"
    
    # Analytics storage
    _usage_analytics = defaultdict(list)
    _performance_metrics = defaultdict(dict)
    _trend_data = defaultdict(list)
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "analysis_type": (["performance", "usage", "trends", "comparison", "optimization"], {"default": "performance", "tooltip": "Type of analysis"}),
                "prompt_id": ("STRING", {"default": "", "tooltip": "Prompt identifier to analyze"}),
            },
            "optional": {
                "time_period": (["day", "week", "month", "all"], {"default": "week", "tooltip": "Analysis time period"}),
                "metric_focus": (["effectiveness", "efficiency", "quality", "user_satisfaction"], {"default": "effectiveness", "tooltip": "Primary metric focus"}),
                "comparison_prompt": ("STRING", {"default": "", "tooltip": "Second prompt for comparison"}),
                "performance_score": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "tooltip": "Log performance score"}),
                "usage_count": ("INT", {"default": 1, "min": 1, "max": 1000, "tooltip": "Usage count to log"}),
                "user_feedback": ("STRING", {"default": "", "multiline": True, "tooltip": "User feedback"}),
                "context_tags": ("STRING", {"default": "", "tooltip": "Context tags for analysis"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("analytics_summary", "detailed_report", "recommendations", "trend_forecast")
    FUNCTION = "analyze_prompts"
    CATEGORY = f"{NodeCategories.PROMPTS}/Management"
    DESCRIPTION = "Advanced prompt analytics and performance tracking"
    
    @performance_monitor("prompt_analytics")
    @cached_operation(ttl=300)
    def analyze_prompts(self, analysis_type, prompt_id, time_period="week", metric_focus="effectiveness",
                       comparison_prompt="", performance_score=0.0, usage_count=1, user_feedback="",
                       context_tags="", validate_input=True):
        
        try:
            # Log data if provided
            if performance_score > 0 or usage_count > 1:
                self._log_analytics_data(prompt_id, performance_score, usage_count, user_feedback, context_tags)
            
            # Perform analysis based on type
            if analysis_type == "performance":
                result = self._analyze_performance(prompt_id, time_period, metric_focus)
            elif analysis_type == "usage":
                result = self._analyze_usage(prompt_id, time_period)
            elif analysis_type == "trends":
                result = self._analyze_trends(prompt_id, time_period)
            elif analysis_type == "comparison":
                result = self._compare_prompts(prompt_id, comparison_prompt, metric_focus)
            elif analysis_type == "optimization":
                result = self._optimization_analysis(prompt_id, metric_focus)
            else:
                result = self._general_analysis(prompt_id)
            
            # Generate reports
            detailed_report = self._generate_detailed_report(prompt_id, analysis_type, time_period)
            recommendations = self._generate_recommendations(prompt_id, analysis_type, metric_focus)
            trend_forecast = self._generate_trend_forecast(prompt_id, time_period)
            
            return (result, detailed_report, recommendations, trend_forecast)
            
        except Exception as e:
            return (f"Error: {str(e)}", "", "", "")
    
    def _log_analytics_data(self, prompt_id: str, score: float, usage: int, feedback: str, tags: str):
        """Log analytics data point"""
        data_point = {
            "timestamp": datetime.now().isoformat(),
            "score": score,
            "usage_count": usage,
            "feedback": feedback,
            "tags": [tag.strip() for tag in tags.split(",") if tag.strip()]
        }
        
        self._usage_analytics[prompt_id].append(data_point)
        
        # Update performance metrics
        if prompt_id not in self._performance_metrics:
            self._performance_metrics[prompt_id] = {
                "total_usage": 0,
                "average_score": 0.0,
                "total_scores": 0,
                "score_count": 0
            }
        
        metrics = self._performance_metrics[prompt_id]
        metrics["total_usage"] += usage
        
        if score > 0:
            metrics["total_scores"] += score
            metrics["score_count"] += 1
            metrics["average_score"] = metrics["total_scores"] / metrics["score_count"]
    
    def _analyze_performance(self, prompt_id: str, period: str, focus: str) -> str:
        """Analyze prompt performance"""
        if prompt_id not in self._performance_metrics:
            return f"No performance data available for {prompt_id}"
        
        metrics = self._performance_metrics[prompt_id]
        
        summary = f"PERFORMANCE ANALYSIS: {prompt_id}\\n"
        summary += f"Total Usage: {metrics['total_usage']}\\n"
        summary += f"Average Score: {metrics['average_score']:.2f}/10\\n"
        summary += f"Score Samples: {metrics['score_count']}\\n"
        
        # Performance grade
        avg_score = metrics['average_score']
        if avg_score >= 8.0:
            grade = "Excellent"
        elif avg_score >= 6.0:
            grade = "Good"
        elif avg_score >= 4.0:
            grade = "Average"
        else:
            grade = "Needs Improvement"
        
        summary += f"Performance Grade: {grade}\\n"
        
        return summary
    
    def _analyze_usage(self, prompt_id: str, period: str) -> str:
        """Analyze prompt usage patterns"""
        if prompt_id not in self._usage_analytics:
            return f"No usage data available for {prompt_id}"
        
        usage_data = self._usage_analytics[prompt_id]
        
        # Filter by time period (simplified)
        recent_data = usage_data[-7:] if period == "week" else usage_data[-30:] if period == "month" else usage_data
        
        total_usage = sum(d["usage_count"] for d in recent_data)
        avg_daily_usage = total_usage / max(len(recent_data), 1)
        
        summary = f"USAGE ANALYSIS: {prompt_id}\\n"
        summary += f"Total Usage ({period}): {total_usage}\\n"
        summary += f"Average Daily Usage: {avg_daily_usage:.1f}\\n"
        summary += f"Data Points: {len(recent_data)}\\n"
        
        # Usage trend
        if len(recent_data) >= 2:
            recent_usage = sum(d["usage_count"] for d in recent_data[-3:])
            earlier_usage = sum(d["usage_count"] for d in recent_data[:3])
            
            if recent_usage > earlier_usage:
                trend = "Increasing"
            elif recent_usage < earlier_usage:
                trend = "Decreasing"
            else:
                trend = "Stable"
            
            summary += f"Usage Trend: {trend}\\n"
        
        return summary
    
    def _analyze_trends(self, prompt_id: str, period: str) -> str:
        """Analyze performance trends"""
        if prompt_id not in self._usage_analytics:
            return f"No trend data available for {prompt_id}"
        
        usage_data = self._usage_analytics[prompt_id]
        scores = [d["score"] for d in usage_data if d["score"] > 0]
        
        if len(scores) < 3:
            return "Insufficient data for trend analysis"
        
        # Simple trend calculation
        recent_scores = scores[-3:]
        earlier_scores = scores[:3]
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        earlier_avg = sum(earlier_scores) / len(earlier_scores)
        
        trend_direction = "Improving" if recent_avg > earlier_avg else "Declining" if recent_avg < earlier_avg else "Stable"
        trend_magnitude = abs(recent_avg - earlier_avg)
        
        summary = f"TREND ANALYSIS: {prompt_id}\\n"
        summary += f"Trend Direction: {trend_direction}\\n"
        summary += f"Recent Average: {recent_avg:.2f}\\n"
        summary += f"Earlier Average: {earlier_avg:.2f}\\n"
        summary += f"Change Magnitude: {trend_magnitude:.2f}\\n"
        
        return summary
    
    def _compare_prompts(self, prompt_a: str, prompt_b: str, focus: str) -> str:
        """Compare two prompts"""
        if not prompt_b:
            return "Second prompt required for comparison"
        
        metrics_a = self._performance_metrics.get(prompt_a, {})
        metrics_b = self._performance_metrics.get(prompt_b, {})
        
        if not metrics_a or not metrics_b:
            return "Insufficient data for comparison"
        
        comparison = f"PROMPT COMPARISON\\n"
        comparison += f"Prompt A: {prompt_a}\\n"
        comparison += f"Prompt B: {prompt_b}\\n\\n"
        
        score_a = metrics_a.get("average_score", 0)
        score_b = metrics_b.get("average_score", 0)
        usage_a = metrics_a.get("total_usage", 0)
        usage_b = metrics_b.get("total_usage", 0)
        
        comparison += f"Performance Scores:\\n"
        comparison += f"  Prompt A: {score_a:.2f}/10\\n"
        comparison += f"  Prompt B: {score_b:.2f}/10\\n"
        comparison += f"  Winner: {'A' if score_a > score_b else 'B' if score_b > score_a else 'Tie'}\\n\\n"
        
        comparison += f"Usage Statistics:\\n"
        comparison += f"  Prompt A: {usage_a} uses\\n"
        comparison += f"  Prompt B: {usage_b} uses\\n"
        comparison += f"  More Popular: {'A' if usage_a > usage_b else 'B' if usage_b > usage_a else 'Tie'}\\n"
        
        return comparison
    
    def _optimization_analysis(self, prompt_id: str, focus: str) -> str:
        """Analyze optimization opportunities"""
        if prompt_id not in self._performance_metrics:
            return f"No data available for optimization analysis of {prompt_id}"
        
        metrics = self._performance_metrics[prompt_id]
        avg_score = metrics.get("average_score", 0)
        
        analysis = f"OPTIMIZATION ANALYSIS: {prompt_id}\\n"
        analysis += f"Current Performance: {avg_score:.2f}/10\\n"
        
        if avg_score < 5.0:
            analysis += f"Priority: HIGH - Significant optimization needed\\n"
        elif avg_score < 7.0:
            analysis += f"Priority: MEDIUM - Room for improvement\\n"
        else:
            analysis += f"Priority: LOW - Already performing well\\n"
        
        # Optimization suggestions based on score
        analysis += f"\\nSuggested Focus Areas:\\n"
        if avg_score < 5.0:
            analysis += f"• Complete prompt restructure\\n"
            analysis += f"• Add quality descriptors\\n"
            analysis += f"• Improve specificity\\n"
        elif avg_score < 7.0:
            analysis += f"• Fine-tune existing elements\\n"
            analysis += f"• A/B test variations\\n"
            analysis += f"• Add context-specific terms\\n"
        else:
            analysis += f"• Minor optimizations only\\n"
            analysis += f"• Monitor for regression\\n"
            analysis += f"• Consider as baseline for other prompts\\n"
        
        return analysis
    
    def _general_analysis(self, prompt_id: str) -> str:
        """General analysis overview"""
        return f"General analysis for {prompt_id} - use specific analysis types for detailed insights"
    
    def _generate_detailed_report(self, prompt_id: str, analysis_type: str, period: str) -> str:
        """Generate detailed analytics report"""
        report = f"DETAILED ANALYTICS REPORT\\n"
        report += f"{'='*50}\\n\\n"
        report += f"Prompt ID: {prompt_id}\\n"
        report += f"Analysis Type: {analysis_type}\\n"
        report += f"Time Period: {period}\\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\\n\\n"
        
        if prompt_id in self._performance_metrics:
            metrics = self._performance_metrics[prompt_id]
            report += f"PERFORMANCE SUMMARY:\\n"
            report += f"• Total Usage: {metrics.get('total_usage', 0)}\\n"
            report += f"• Average Score: {metrics.get('average_score', 0):.2f}/10\\n"
            report += f"• Score Samples: {metrics.get('score_count', 0)}\\n\\n"
        
        if prompt_id in self._usage_analytics:
            usage_data = self._usage_analytics[prompt_id]
            report += f"USAGE PATTERNS:\\n"
            report += f"• Total Sessions: {len(usage_data)}\\n"
            report += f"• Recent Activity: {len(usage_data[-7:])} sessions (last 7 entries)\\n"
            
            # Feedback analysis
            feedback_entries = [d["feedback"] for d in usage_data if d["feedback"]]
            if feedback_entries:
                report += f"• Feedback Entries: {len(feedback_entries)}\\n"
        
        return report
    
    def _generate_recommendations(self, prompt_id: str, analysis_type: str, focus: str) -> str:
        """Generate optimization recommendations"""
        if prompt_id not in self._performance_metrics:
            return "No data available for recommendations"
        
        metrics = self._performance_metrics[prompt_id]
        avg_score = metrics.get("average_score", 0)
        
        recommendations = f"OPTIMIZATION RECOMMENDATIONS\\n"
        recommendations += f"{'='*40}\\n\\n"
        
        if avg_score < 4.0:
            recommendations += f"🔴 CRITICAL OPTIMIZATIONS NEEDED:\\n"
            recommendations += f"• Complete prompt rewrite recommended\\n"
            recommendations += f"• Add specific quality descriptors\\n"
            recommendations += f"• Improve clarity and structure\\n"
            recommendations += f"• Consider using prompt templates\\n\\n"
        
        elif avg_score < 6.0:
            recommendations += f"🟡 MODERATE OPTIMIZATIONS:\\n"
            recommendations += f"• A/B test prompt variations\\n"
            recommendations += f"• Add more specific terms\\n"
            recommendations += f"• Optimize token efficiency\\n"
            recommendations += f"• Remove redundant elements\\n\\n"
        
        elif avg_score < 8.0:
            recommendations += f"🟢 FINE-TUNING OPPORTUNITIES:\\n"
            recommendations += f"• Minor adjustments to word choice\\n"
            recommendations += f"• Experiment with emphasis weights\\n"
            recommendations += f"• Test different quality descriptors\\n"
            recommendations += f"• Monitor performance consistency\\n\\n"
        
        else:
            recommendations += f"✅ EXCELLENT PERFORMANCE:\\n"
            recommendations += f"• Use as template for similar prompts\\n"
            recommendations += f"• Document successful elements\\n"
            recommendations += f"• Monitor for performance regression\\n"
            recommendations += f"• Share as best practice example\\n\\n"
        
        recommendations += f"FOCUS AREA SUGGESTIONS ({focus.upper()}):\\n"
        if focus == "effectiveness":
            recommendations += f"• Measure output quality metrics\\n"
            recommendations += f"• Track user satisfaction scores\\n"
        elif focus == "efficiency":
            recommendations += f"• Optimize token count\\n"
            recommendations += f"• Reduce processing time\\n"
        elif focus == "quality":
            recommendations += f"• Enhance quality descriptors\\n"
            recommendations += f"• Improve technical accuracy\\n"
        else:
            recommendations += f"• Gather more user feedback\\n"
            recommendations += f"• Conduct usability testing\\n"
        
        return recommendations
    
    def _generate_trend_forecast(self, prompt_id: str, period: str) -> str:
        """Generate trend forecast"""
        if prompt_id not in self._usage_analytics:
            return "No trend data available for forecasting"
        
        usage_data = self._usage_analytics[prompt_id]
        scores = [d["score"] for d in usage_data if d["score"] > 0]
        
        if len(scores) < 3:
            return "Insufficient data for trend forecasting"
        
        # Simple trend projection
        recent_trend = scores[-3:]
        trend_avg = sum(recent_trend) / len(recent_trend)
        
        forecast = f"TREND FORECAST\\n"
        forecast += f"{'='*25}\\n\\n"
        forecast += f"Current Trend: {trend_avg:.2f}/10\\n"
        
        if len(scores) >= 5:
            earlier_avg = sum(scores[:3]) / 3
            trend_direction = trend_avg - earlier_avg
            
            if trend_direction > 0.2:
                forecast += f"Forecast: Improving trend (+{trend_direction:.2f})\\n"
                forecast += f"Projection: Continued performance improvement\\n"
            elif trend_direction < -0.2:
                forecast += f"Forecast: Declining trend ({trend_direction:.2f})\\n"
                forecast += f"Projection: Performance optimization needed\\n"
            else:
                forecast += f"Forecast: Stable performance\\n"
                forecast += f"Projection: Maintain current approach\\n"
        
        forecast += f"\\nConfidence: {'High' if len(scores) >= 10 else 'Medium' if len(scores) >= 5 else 'Low'}\\n"
        forecast += f"Recommendation: {'Monitor closely' if len(scores) < 10 else 'Reliable forecast'}\\n"
        
        return forecast


# Node registrations
NODE_CLASS_MAPPINGS = {
    "XDEV_PromptVersionControl": XDEV_PromptVersionControl,
    "XDEV_ABTestManager": XDEV_ABTestManager,
    "XDEV_PromptAnalytics": XDEV_PromptAnalytics,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEV_PromptVersionControl": "Prompt Version Control (XDev)",
    "XDEV_ABTestManager": "A/B Test Manager (XDev)",
    "XDEV_PromptAnalytics": "Prompt Analytics (XDev)",
}