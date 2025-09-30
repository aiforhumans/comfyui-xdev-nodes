"""
Advanced Data Analytics and Intelligence Nodes
High-performance data analysis, pattern recognition, and statistical modeling
"""

from __future__ import annotations
from typing import Dict, Tuple, Any, List, Optional, Union, TYPE_CHECKING
import json
import time
import math
import statistics
from ..performance import performance_monitor, cached_operation, intern_string
from ..mixins import ValidationMixin
from ..categories import NodeCategories

if TYPE_CHECKING:
    import numpy as np

# Graceful imports for data science libraries
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    pd = None
    HAS_PANDAS = False


class XDEV_DataPatternAnalyzer(ValidationMixin):
    """
    Advanced pattern recognition and data analysis system.
    
    Performs sophisticated statistical analysis, trend detection,
    and pattern recognition on various data types.
    """
    
    DISPLAY_NAME = "Data Pattern Analyzer (XDev)"
    
    _ANALYSIS_MODES = (
        intern_string("trend_analysis"),
        intern_string("statistical_profiling"), 
        intern_string("pattern_recognition"),
        intern_string("anomaly_detection"),
        intern_string("correlation_analysis"),
        intern_string("time_series_analysis"),
        intern_string("clustering_analysis")
    )
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "data_input": ("STRING", {
                    "multiline": True,
                    "default": '{"values": [1, 2, 3, 4, 5, 4, 3, 2, 1, 2, 3, 4, 5]}',
                    "tooltip": "JSON data for analysis (numbers, arrays, or structured data)"
                }),
                "analysis_mode": (cls._ANALYSIS_MODES, {
                    "default": "statistical_profiling",
                    "tooltip": "Type of analysis to perform"
                })
            },
            "optional": {
                "confidence_level": ("FLOAT", {
                    "default": 0.95,
                    "min": 0.5,
                    "max": 0.999,
                    "step": 0.01,
                    "tooltip": "Statistical confidence level"
                }),
                "window_size": ("INT", {
                    "default": 5,
                    "min": 2,
                    "max": 100,
                    "tooltip": "Analysis window size for time series"
                }),
                "enable_advanced_stats": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Include advanced statistical measures"
                }),
                "output_format": (["summary", "detailed", "research_data"], {
                    "default": "detailed",
                    "tooltip": "Output detail level"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "FLOAT")
    RETURN_NAMES = ("analysis_report", "pattern_summary", "statistical_data", "confidence_score")
    FUNCTION = "analyze_patterns"
    CATEGORY = "XDev/Data/Analytics"
    DESCRIPTION = "Advanced pattern recognition and statistical analysis of data"
    
    @performance_monitor("data_pattern_analysis")
    @cached_operation(ttl=600)
    def analyze_patterns(self, data_input: str, analysis_mode: str,
                        confidence_level: float = 0.95, window_size: int = 5,
                        enable_advanced_stats: bool = True, output_format: str = "detailed"):
        """
        Perform comprehensive data pattern analysis
        """
        try:
            # Parse input data
            data = json.loads(data_input)
            
            # Extract numerical data
            if isinstance(data, dict):
                if "values" in data:
                    values = data["values"]
                elif "data" in data:
                    values = data["data"]
                else:
                    values = list(data.values())[0] if data else []
            elif isinstance(data, list):
                values = data
            else:
                values = [data]
            
            # Ensure we have numerical data
            numerical_values = []
            for v in values:
                try:
                    numerical_values.append(float(v))
                except (ValueError, TypeError):
                    continue
            
            if not numerical_values:
                return ("Error: No numerical data found", "No patterns detected", "{}", 0.0)
            
            # Perform analysis based on mode
            if analysis_mode == "trend_analysis":
                result = self._analyze_trends(numerical_values, confidence_level, window_size)
            elif analysis_mode == "statistical_profiling":
                result = self._statistical_profiling(numerical_values, enable_advanced_stats)
            elif analysis_mode == "pattern_recognition":
                result = self._recognize_patterns(numerical_values, window_size)
            elif analysis_mode == "anomaly_detection":
                result = self._detect_anomalies(numerical_values, confidence_level)
            elif analysis_mode == "correlation_analysis":
                result = self._correlation_analysis(numerical_values, window_size)
            elif analysis_mode == "time_series_analysis":
                result = self._time_series_analysis(numerical_values, window_size)
            elif analysis_mode == "clustering_analysis":
                result = self._clustering_analysis(numerical_values, window_size)
            else:
                result = self._statistical_profiling(numerical_values, enable_advanced_stats)
            
            # Format output based on requested format
            if output_format == "summary":
                report = self._format_summary_report(result, analysis_mode)
            elif output_format == "research_data":
                report = json.dumps(result, indent=2)
            else:
                report = self._format_detailed_report(result, analysis_mode)
            
            pattern_summary = self._extract_pattern_summary(result)
            statistical_data = json.dumps(result.get("statistics", {}), indent=2)
            confidence_score = result.get("confidence", 0.0)
            
            return (report, pattern_summary, statistical_data, confidence_score)
            
        except Exception as e:
            error_msg = f"Pattern analysis failed: {str(e)}"
            return (error_msg, "Analysis failed", "{}", 0.0)
    
    def _analyze_trends(self, values: List[float], confidence: float, window: int) -> dict:
        """Analyze data trends and directions"""
        if len(values) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        # Calculate trend metrics
        n = len(values)
        x = list(range(n))
        
        # Simple linear regression
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(xi * yi for xi, yi in zip(x, values))
        sum_x2 = sum(xi * xi for xi in x)
        
        # Calculate slope (trend direction)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Calculate correlation coefficient
        mean_x = sum_x / n
        mean_y = sum_y / n
        
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, values))
        sum_sq_x = sum((xi - mean_x) ** 2 for xi in x)
        sum_sq_y = sum((yi - mean_y) ** 2 for yi in values)
        
        correlation = numerator / (math.sqrt(sum_sq_x * sum_sq_y)) if sum_sq_x > 0 and sum_sq_y > 0 else 0
        
        # Trend classification
        if abs(slope) < 0.01:
            trend_type = "stable"
        elif slope > 0:
            trend_type = "increasing"
        else:
            trend_type = "decreasing"
        
        # Moving averages for trend smoothing
        moving_averages = []
        for i in range(window - 1, len(values)):
            avg = sum(values[i - window + 1:i + 1]) / window
            moving_averages.append(avg)
        
        return {
            "trend_type": trend_type,
            "slope": slope,
            "intercept": intercept,
            "correlation": correlation,
            "confidence": min(abs(correlation), 0.99),
            "moving_averages": moving_averages,
            "statistics": {
                "linear_trend": slope,
                "r_squared": correlation ** 2,
                "trend_strength": abs(correlation)
            }
        }
    
    def _statistical_profiling(self, values: List[float], advanced: bool) -> dict:
        """Comprehensive statistical profiling"""
        n = len(values)
        if n == 0:
            return {"error": "No data to analyze"}
        
        # Basic statistics
        mean_val = statistics.mean(values)
        median_val = statistics.median(values)
        
        if n > 1:
            std_dev = statistics.stdev(values)
            variance = statistics.variance(values)
        else:
            std_dev = 0.0
            variance = 0.0
        
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val
        
        # Percentiles
        sorted_vals = sorted(values)
        q1 = self._percentile(sorted_vals, 25)
        q3 = self._percentile(sorted_vals, 75)
        iqr = q3 - q1
        
        result = {
            "basic_stats": {
                "count": n,
                "mean": mean_val,
                "median": median_val,
                "std_dev": std_dev,
                "variance": variance,
                "min": min_val,
                "max": max_val,
                "range": range_val
            },
            "quartiles": {
                "q1": q1,
                "q2": median_val,
                "q3": q3,
                "iqr": iqr
            },
            "confidence": 0.95,
            "statistics": {
                "coefficient_of_variation": (std_dev / mean_val) if mean_val != 0 else 0,
                "skewness_indicator": (mean_val - median_val) / std_dev if std_dev > 0 else 0
            }
        }
        
        if advanced:
            # Advanced statistics
            result["advanced_stats"] = self._calculate_advanced_stats(values, mean_val, std_dev)
        
        return result
    
    def _recognize_patterns(self, values: List[float], window: int) -> dict:
        """Recognize common patterns in data"""
        patterns = {
            "seasonality": self._detect_seasonality(values, window),
            "cycles": self._detect_cycles(values),
            "outliers": self._find_outliers(values),
            "monotonic": self._check_monotonic(values)
        }
        
        # Pattern confidence based on detected features
        confidence = 0.0
        if patterns["seasonality"]["detected"]:
            confidence += 0.3
        if patterns["cycles"]["detected"]:
            confidence += 0.2
        if patterns["monotonic"]["detected"]:
            confidence += 0.25
        
        return {
            "patterns": patterns,
            "confidence": min(confidence, 0.95),
            "statistics": {
                "pattern_count": sum(1 for p in patterns.values() if p.get("detected", False)),
                "complexity": len([p for p in patterns.values() if p.get("strength", 0) > 0.5])
            }
        }
    
    def _detect_anomalies(self, values: List[float], confidence: float) -> dict:
        """Detect statistical anomalies"""
        if len(values) < 3:
            return {"error": "Insufficient data for anomaly detection"}
        
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        # Z-score based anomaly detection
        z_threshold = 2.0  # Standard threshold for outliers
        anomalies = []
        
        for i, value in enumerate(values):
            if std_dev > 0:
                z_score = abs(value - mean_val) / std_dev
                if z_score > z_threshold:
                    anomalies.append({
                        "index": i,
                        "value": value,
                        "z_score": z_score,
                        "severity": "high" if z_score > 3.0 else "moderate"
                    })
        
        # IQR-based outlier detection
        sorted_vals = sorted(values)
        q1 = self._percentile(sorted_vals, 25)
        q3 = self._percentile(sorted_vals, 75)
        iqr = q3 - q1
        
        iqr_anomalies = []
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        for i, value in enumerate(values):
            if value < lower_bound or value > upper_bound:
                iqr_anomalies.append({"index": i, "value": value})
        
        return {
            "z_score_anomalies": anomalies,
            "iqr_anomalies": iqr_anomalies,
            "anomaly_rate": len(anomalies) / len(values),
            "confidence": confidence,
            "statistics": {
                "total_anomalies": len(anomalies),
                "anomaly_percentage": (len(anomalies) / len(values)) * 100,
                "z_threshold": z_threshold
            }
        }
    
    def _correlation_analysis(self, values: List[float], window: int) -> dict:
        """Analyze correlations with shifted versions"""
        if len(values) < window * 2:
            return {"error": "Insufficient data for correlation analysis"}
        
        autocorrelations = []
        
        # Calculate autocorrelations for different lags
        for lag in range(1, min(window, len(values) // 2)):
            original = values[:-lag]
            shifted = values[lag:]
            
            if len(original) > 1 and len(shifted) > 1:
                corr = self._calculate_correlation(original, shifted)
                autocorrelations.append({"lag": lag, "correlation": corr})
        
        # Find strongest correlation
        max_corr = max(autocorrelations, key=lambda x: abs(x["correlation"])) if autocorrelations else {"correlation": 0}
        
        return {
            "autocorrelations": autocorrelations,
            "strongest_correlation": max_corr,
            "confidence": min(abs(max_corr["correlation"]), 0.95),
            "statistics": {
                "max_correlation": max_corr["correlation"],
                "correlation_count": len(autocorrelations)
            }
        }
    
    def _time_series_analysis(self, values: List[float], window: int) -> dict:
        """Time series specific analysis"""
        if len(values) < window:
            return {"error": "Insufficient data for time series analysis"}
        
        # Calculate differences (first derivative)
        differences = [values[i] - values[i-1] for i in range(1, len(values))]
        
        # Calculate second differences (acceleration)
        second_diff = [differences[i] - differences[i-1] for i in range(1, len(differences))]
        
        # Volatility analysis
        volatility = statistics.stdev(differences) if len(differences) > 1 else 0
        
        # Trend analysis
        trend_direction = "stable"
        if differences:
            avg_change = statistics.mean(differences)
            if avg_change > volatility * 0.1:
                trend_direction = "increasing"
            elif avg_change < -volatility * 0.1:
                trend_direction = "decreasing"
        
        return {
            "trend_direction": trend_direction,
            "volatility": volatility,
            "differences": differences[-10:],  # Last 10 changes
            "average_change": statistics.mean(differences) if differences else 0,
            "confidence": 0.8,
            "statistics": {
                "volatility_coefficient": volatility / statistics.mean(values) if statistics.mean(values) != 0 else 0,
                "trend_strength": abs(statistics.mean(differences)) / volatility if volatility > 0 else 0
            }
        }
    
    def _clustering_analysis(self, values: List[float], window: int) -> dict:
        """Simple clustering analysis"""
        if len(values) < window:
            return {"error": "Insufficient data for clustering analysis"}
        
        # Simple k-means-like clustering into 3 groups
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        
        # Define cluster boundaries
        low_threshold = sorted_vals[n // 3]
        high_threshold = sorted_vals[2 * n // 3]
        
        clusters = {"low": [], "medium": [], "high": []}
        
        for i, value in enumerate(values):
            if value <= low_threshold:
                clusters["low"].append({"index": i, "value": value})
            elif value <= high_threshold:
                clusters["medium"].append({"index": i, "value": value})
            else:
                clusters["high"].append({"index": i, "value": value})
        
        # Calculate cluster statistics
        cluster_stats = {}
        for cluster_name, cluster_data in clusters.items():
            if cluster_data:
                cluster_values = [item["value"] for item in cluster_data]
                cluster_stats[cluster_name] = {
                    "count": len(cluster_values),
                    "mean": statistics.mean(cluster_values),
                    "percentage": len(cluster_values) / len(values) * 100
                }
        
        return {
            "clusters": clusters,
            "cluster_statistics": cluster_stats,
            "confidence": 0.7,
            "statistics": {
                "cluster_count": len([c for c in clusters.values() if c]),
                "largest_cluster": max(cluster_stats.keys(), key=lambda k: cluster_stats[k]["count"]) if cluster_stats else None
            }
        }
    
    # Helper methods
    def _percentile(self, sorted_data: List[float], percentile: float) -> float:
        """Calculate percentile value"""
        if not sorted_data:
            return 0.0
        
        index = (percentile / 100.0) * (len(sorted_data) - 1)
        lower = int(index)
        upper = min(lower + 1, len(sorted_data) - 1)
        
        if lower == upper:
            return sorted_data[lower]
        
        weight = index - lower
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _calculate_advanced_stats(self, values: List[float], mean: float, std_dev: float) -> dict:
        """Calculate advanced statistical measures"""
        n = len(values)
        
        # Skewness
        if std_dev > 0:
            skewness = sum((x - mean) ** 3 for x in values) / (n * std_dev ** 3)
        else:
            skewness = 0.0
        
        # Kurtosis
        if std_dev > 0:
            kurtosis = sum((x - mean) ** 4 for x in values) / (n * std_dev ** 4) - 3
        else:
            kurtosis = 0.0
        
        return {
            "skewness": skewness,
            "kurtosis": kurtosis,
            "normality_indicator": abs(skewness) < 1.0 and abs(kurtosis) < 1.0
        }
    
    def _detect_seasonality(self, values: List[float], window: int) -> dict:
        """Detect seasonal patterns"""
        if len(values) < window * 2:
            return {"detected": False, "reason": "insufficient_data"}
        
        # Simple seasonality detection using autocorrelation
        autocorr = self._calculate_correlation(values[:-window], values[window:])
        
        return {
            "detected": abs(autocorr) > 0.3,
            "strength": abs(autocorr),
            "period": window,
            "correlation": autocorr
        }
    
    def _detect_cycles(self, values: List[float]) -> dict:
        """Detect cyclical patterns"""
        if len(values) < 6:
            return {"detected": False, "reason": "insufficient_data"}
        
        # Look for turning points
        turning_points = 0
        for i in range(1, len(values) - 1):
            if (values[i] > values[i-1] and values[i] > values[i+1]) or \
               (values[i] < values[i-1] and values[i] < values[i+1]):
                turning_points += 1
        
        cycle_strength = turning_points / len(values)
        
        return {
            "detected": cycle_strength > 0.1,
            "strength": cycle_strength,
            "turning_points": turning_points
        }
    
    def _find_outliers(self, values: List[float]) -> dict:
        """Find statistical outliers"""
        if len(values) < 3:
            return {"detected": False, "count": 0}
        
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        outliers = []
        for i, value in enumerate(values):
            if std_dev > 0 and abs(value - mean_val) > 2 * std_dev:
                outliers.append(i)
        
        return {
            "detected": len(outliers) > 0,
            "count": len(outliers),
            "indices": outliers,
            "percentage": len(outliers) / len(values) * 100
        }
    
    def _check_monotonic(self, values: List[float]) -> dict:
        """Check for monotonic patterns"""
        if len(values) < 2:
            return {"detected": False, "type": "none"}
        
        increasing = all(values[i] <= values[i+1] for i in range(len(values)-1))
        decreasing = all(values[i] >= values[i+1] for i in range(len(values)-1))
        
        if increasing:
            return {"detected": True, "type": "increasing", "strength": 1.0}
        elif decreasing:
            return {"detected": True, "type": "decreasing", "strength": 1.0}
        else:
            return {"detected": False, "type": "none", "strength": 0.0}
    
    def _format_detailed_report(self, result: dict, mode: str) -> str:
        """Format detailed analysis report"""
        report = [f"📊 DATA PATTERN ANALYSIS - {mode.upper()}", "=" * 50, ""]
        
        if "error" in result:
            report.append(f"❌ Error: {result['error']}")
            return "\n".join(report)
        
        # Mode-specific reporting
        if mode == "trend_analysis":
            report.extend([
                f"📈 TREND ANALYSIS:",
                f"  • Trend Type: {result.get('trend_type', 'unknown').title()}",
                f"  • Slope: {result.get('slope', 0):.4f}",
                f"  • Correlation: {result.get('correlation', 0):.3f}",
                f"  • R²: {result.get('statistics', {}).get('r_squared', 0):.3f}"
            ])
        
        elif mode == "statistical_profiling":
            stats = result.get("basic_stats", {})
            report.extend([
                f"📊 STATISTICAL PROFILE:",
                f"  • Count: {stats.get('count', 0)}",
                f"  • Mean: {stats.get('mean', 0):.3f}",
                f"  • Median: {stats.get('median', 0):.3f}",
                f"  • Std Dev: {stats.get('std_dev', 0):.3f}",
                f"  • Range: {stats.get('range', 0):.3f}"
            ])
        
        elif mode == "pattern_recognition":
            patterns = result.get("patterns", {})
            report.append("🔍 DETECTED PATTERNS:")
            for pattern_name, pattern_data in patterns.items():
                if pattern_data.get("detected", False):
                    report.append(f"  ✓ {pattern_name.title()}: {pattern_data.get('type', 'detected')}")
                else:
                    report.append(f"  ✗ {pattern_name.title()}: not detected")
        
        elif mode == "anomaly_detection":
            anomalies = result.get("z_score_anomalies", [])
            report.extend([
                f"🚨 ANOMALY DETECTION:",
                f"  • Total Anomalies: {len(anomalies)}",
                f"  • Anomaly Rate: {result.get('anomaly_rate', 0):.2%}",
                f"  • Detection Method: Z-Score + IQR"
            ])
        
        # Add confidence score
        report.extend([
            "",
            f"🎯 Confidence Score: {result.get('confidence', 0):.1%}"
        ])
        
        return "\n".join(report)
    
    def _format_summary_report(self, result: dict, mode: str) -> str:
        """Format summary report"""
        if "error" in result:
            return f"Error: {result['error']}"
        
        confidence = result.get("confidence", 0)
        
        if mode == "trend_analysis":
            trend = result.get("trend_type", "unknown")
            correlation = result.get("correlation", 0)
            return f"Trend: {trend} (r={correlation:.3f}) | Confidence: {confidence:.1%}"
        
        elif mode == "statistical_profiling":
            stats = result.get("basic_stats", {})
            mean = stats.get("mean", 0)
            std = stats.get("std_dev", 0)
            return f"Mean: {mean:.3f} ± {std:.3f} | Confidence: {confidence:.1%}"
        
        elif mode == "anomaly_detection":
            anomalies = len(result.get("z_score_anomalies", []))
            rate = result.get("anomaly_rate", 0)
            return f"Anomalies: {anomalies} ({rate:.1%}) | Confidence: {confidence:.1%}"
        
        else:
            return f"{mode.replace('_', ' ').title()} | Confidence: {confidence:.1%}"
    
    def _extract_pattern_summary(self, result: dict) -> str:
        """Extract key pattern insights"""
        if "error" in result:
            return "No patterns detected due to error"
        
        summaries = []
        
        if "trend_type" in result:
            summaries.append(f"Trend: {result['trend_type']}")
        
        if "patterns" in result:
            detected = [name for name, data in result["patterns"].items() if data.get("detected")]
            if detected:
                summaries.append(f"Patterns: {', '.join(detected)}")
        
        if "anomaly_rate" in result:
            rate = result["anomaly_rate"]
            if rate > 0.05:  # More than 5% anomalies
                summaries.append(f"High anomaly rate: {rate:.1%}")
        
        if "cluster_statistics" in result:
            clusters = len(result["cluster_statistics"])
            summaries.append(f"Clusters: {clusters}")
        
        return " | ".join(summaries) if summaries else "Basic statistical analysis completed"


class XDEV_PerformanceBenchmark(ValidationMixin):
    """
    Advanced performance benchmarking and optimization analysis.
    
    Provides comprehensive performance testing, bottleneck identification,
    and optimization recommendations for various computational tasks.
    """
    
    DISPLAY_NAME = "Performance Benchmark (XDev)"
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "benchmark_type": (["cpu_intensive", "memory_test", "io_operations", "mixed_workload"], {
                    "default": "mixed_workload",
                    "tooltip": "Type of performance benchmark to run"
                }),
                "test_duration": ("INT", {
                    "default": 10,
                    "min": 1,
                    "max": 60,
                    "tooltip": "Benchmark duration in seconds"
                })
            },
            "optional": {
                "data_size": ("INT", {
                    "default": 1000,
                    "min": 100,
                    "max": 100000,
                    "tooltip": "Size of test data for benchmarking"
                }),
                "iterations": ("INT", {
                    "default": 100,
                    "min": 10,
                    "max": 10000,
                    "tooltip": "Number of benchmark iterations"
                }),
                "include_system_info": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Include system information in results"
                }),
                "optimize_for": (["speed", "memory", "balanced"], {
                    "default": "balanced",
                    "tooltip": "Optimization target for recommendations"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "FLOAT", "STRING")
    RETURN_NAMES = ("benchmark_report", "optimization_recommendations", "performance_score", "system_info")
    FUNCTION = "run_benchmark"
    CATEGORY = "XDev/Performance/Benchmark"
    DESCRIPTION = "Advanced performance benchmarking with optimization recommendations"
    
    @performance_monitor("performance_benchmark")
    def run_benchmark(self, benchmark_type: str, test_duration: int,
                     data_size: int = 1000, iterations: int = 100,
                     include_system_info: bool = True, optimize_for: str = "balanced"):
        """
        Run comprehensive performance benchmark
        """
        try:
            start_time = time.time()
            
            # Initialize benchmark results
            results = {
                "benchmark_type": benchmark_type,
                "test_duration": test_duration,
                "data_size": data_size,
                "iterations": iterations,
                "start_time": start_time,
                "metrics": {}
            }
            
            # Run specific benchmark
            if benchmark_type == "cpu_intensive":
                metrics = self._cpu_benchmark(data_size, iterations, test_duration)
            elif benchmark_type == "memory_test":
                metrics = self._memory_benchmark(data_size, iterations, test_duration)
            elif benchmark_type == "io_operations":
                metrics = self._io_benchmark(data_size, iterations, test_duration)
            elif benchmark_type == "mixed_workload":
                metrics = self._mixed_benchmark(data_size, iterations, test_duration)
            else:
                metrics = {"error": f"Unknown benchmark type: {benchmark_type}"}
            
            results["metrics"] = metrics
            results["total_time"] = time.time() - start_time
            
            # Calculate performance score
            performance_score = self._calculate_performance_score(results, optimize_for)
            
            # Generate optimization recommendations
            recommendations = self._generate_recommendations(results, optimize_for)
            
            # Format reports
            benchmark_report = self._format_benchmark_report(results)
            
            # System information
            system_info = self._get_system_info() if include_system_info else "System info disabled"
            
            return (benchmark_report, recommendations, performance_score, system_info)
            
        except Exception as e:
            error_msg = f"Benchmark failed: {str(e)}"
            return (error_msg, "No recommendations available", 0.0, "System info unavailable")
    
    def _cpu_benchmark(self, data_size: int, iterations: int, duration: int) -> dict:
        """CPU-intensive benchmark"""
        results = {"operations": [], "total_ops": 0}
        start_time = time.time()
        
        ops_count = 0
        while time.time() - start_time < duration:
            # Mathematical operations
            for _ in range(min(iterations, 1000)):
                # Prime number calculation (CPU intensive)
                n = data_size
                primes = []
                for i in range(2, min(n, 1000)):
                    is_prime = True
                    for j in range(2, int(i ** 0.5) + 1):
                        if i % j == 0:
                            is_prime = False
                            break
                    if is_prime:
                        primes.append(i)
                
                ops_count += 1
                
                if time.time() - start_time >= duration:
                    break
        
        total_time = time.time() - start_time
        
        return {
            "operations_per_second": ops_count / total_time,
            "total_operations": ops_count,
            "avg_operation_time": total_time / ops_count if ops_count > 0 else 0,
            "cpu_efficiency": min(ops_count / (duration * 100), 1.0)  # Normalized score
        }
    
    def _memory_benchmark(self, data_size: int, iterations: int, duration: int) -> dict:
        """Memory allocation and access benchmark"""
        results = {"allocations": [], "access_times": []}
        start_time = time.time()
        
        allocation_count = 0
        access_count = 0
        
        while time.time() - start_time < duration:
            # Memory allocation test
            for _ in range(min(iterations, 100)):
                # Allocate and manipulate data
                test_data = list(range(data_size))
                
                # Memory access patterns
                for i in range(0, len(test_data), max(1, len(test_data) // 100)):
                    test_data[i] = test_data[i] * 2
                    access_count += 1
                
                allocation_count += 1
                
                if time.time() - start_time >= duration:
                    break
            
            if time.time() - start_time >= duration:
                break
        
        total_time = time.time() - start_time
        
        return {
            "allocations_per_second": allocation_count / total_time,
            "memory_accesses_per_second": access_count / total_time,
            "total_allocations": allocation_count,
            "memory_efficiency": min(allocation_count / (duration * 10), 1.0)
        }
    
    def _io_benchmark(self, data_size: int, iterations: int, duration: int) -> dict:
        """I/O operations benchmark"""
        results = {"read_ops": 0, "write_ops": 0}
        start_time = time.time()
        
        read_count = 0
        write_count = 0
        
        # Simulate I/O operations
        test_data = "x" * min(data_size, 10000)  # Limit string size
        
        while time.time() - start_time < duration:
            for _ in range(min(iterations, 1000)):
                # Simulate write operation
                temp_data = test_data * 2
                write_count += 1
                
                # Simulate read operation
                data_length = len(temp_data)
                read_count += 1
                
                if time.time() - start_time >= duration:
                    break
            
            if time.time() - start_time >= duration:
                break
        
        total_time = time.time() - start_time
        
        return {
            "reads_per_second": read_count / total_time,
            "writes_per_second": write_count / total_time,
            "total_reads": read_count,
            "total_writes": write_count,
            "io_efficiency": min((read_count + write_count) / (duration * 1000), 1.0)
        }
    
    def _mixed_benchmark(self, data_size: int, iterations: int, duration: int) -> dict:
        """Mixed workload benchmark"""
        # Run shorter versions of each benchmark
        sub_duration = duration // 3
        
        cpu_results = self._cpu_benchmark(data_size, iterations // 3, sub_duration)
        memory_results = self._memory_benchmark(data_size, iterations // 3, sub_duration)
        io_results = self._io_benchmark(data_size, iterations // 3, sub_duration)
        
        return {
            "cpu_performance": cpu_results,
            "memory_performance": memory_results,
            "io_performance": io_results,
            "overall_efficiency": (
                cpu_results.get("cpu_efficiency", 0) +
                memory_results.get("memory_efficiency", 0) +
                io_results.get("io_efficiency", 0)
            ) / 3
        }
    
    def _calculate_performance_score(self, results: dict, optimize_for: str) -> float:
        """Calculate overall performance score (0-100)"""
        metrics = results.get("metrics", {})
        
        if "error" in metrics:
            return 0.0
        
        if results["benchmark_type"] == "mixed_workload":
            # Calculate weighted score based on optimization target
            cpu_eff = metrics.get("cpu_performance", {}).get("cpu_efficiency", 0)
            mem_eff = metrics.get("memory_performance", {}).get("memory_efficiency", 0)
            io_eff = metrics.get("io_performance", {}).get("io_efficiency", 0)
            
            if optimize_for == "speed":
                score = cpu_eff * 0.6 + io_eff * 0.3 + mem_eff * 0.1
            elif optimize_for == "memory":
                score = mem_eff * 0.6 + cpu_eff * 0.3 + io_eff * 0.1
            else:  # balanced
                score = (cpu_eff + mem_eff + io_eff) / 3
        else:
            # Single benchmark type
            if "cpu_efficiency" in metrics:
                score = metrics["cpu_efficiency"]
            elif "memory_efficiency" in metrics:
                score = metrics["memory_efficiency"]
            elif "io_efficiency" in metrics:
                score = metrics["io_efficiency"]
            else:
                score = 0.5  # Default
        
        return score * 100  # Convert to 0-100 scale
    
    def _generate_recommendations(self, results: dict, optimize_for: str) -> str:
        """Generate optimization recommendations"""
        recommendations = ["🚀 PERFORMANCE OPTIMIZATION RECOMMENDATIONS", "=" * 50]
        
        metrics = results.get("metrics", {})
        
        if "error" in metrics:
            recommendations.append("❌ Unable to generate recommendations due to benchmark error")
            return "\n".join(recommendations)
        
        benchmark_type = results["benchmark_type"]
        
        # Type-specific recommendations
        if benchmark_type == "cpu_intensive":
            ops_per_sec = metrics.get("operations_per_second", 0)
            if ops_per_sec < 10:
                recommendations.append("🔧 CPU Performance: Consider optimizing algorithms or upgrading CPU")
            else:
                recommendations.append("✅ CPU Performance: Good computational throughput")
        
        elif benchmark_type == "memory_test":
            mem_eff = metrics.get("memory_efficiency", 0)
            if mem_eff < 0.5:
                recommendations.append("🔧 Memory: Optimize memory allocation patterns")
                recommendations.append("💡 Consider: Object pooling, memory-mapped files, or streaming")
            else:
                recommendations.append("✅ Memory: Efficient memory usage patterns")
        
        elif benchmark_type == "io_operations":
            io_eff = metrics.get("io_efficiency", 0)
            if io_eff < 0.5:
                recommendations.append("🔧 I/O: Optimize data access patterns")
                recommendations.append("💡 Consider: Caching, batching, or async operations")
            else:
                recommendations.append("✅ I/O: Good data access performance")
        
        elif benchmark_type == "mixed_workload":
            # Mixed workload specific recommendations
            cpu_perf = metrics.get("cpu_performance", {})
            mem_perf = metrics.get("memory_performance", {})
            io_perf = metrics.get("io_performance", {})
            
            # Identify bottlenecks
            cpu_eff = cpu_perf.get("cpu_efficiency", 0)
            mem_eff = mem_perf.get("memory_efficiency", 0)
            io_eff = io_perf.get("io_efficiency", 0)
            
            min_eff = min(cpu_eff, mem_eff, io_eff)
            
            if cpu_eff == min_eff:
                recommendations.append("🔧 Primary Bottleneck: CPU performance")
                recommendations.append("💡 Focus on: Algorithm optimization, parallel processing")
            elif mem_eff == min_eff:
                recommendations.append("🔧 Primary Bottleneck: Memory efficiency")
                recommendations.append("💡 Focus on: Memory management, data structures")
            elif io_eff == min_eff:
                recommendations.append("🔧 Primary Bottleneck: I/O operations")
                recommendations.append("💡 Focus on: Data access optimization, caching")
        
        # Optimization target specific recommendations
        recommendations.append(f"\n🎯 Optimization Target: {optimize_for}")
        
        if optimize_for == "speed":
            recommendations.extend([
                "⚡ Speed Optimizations:",
                "  • Use compiled libraries (NumPy, PyTorch)",
                "  • Implement parallel processing",
                "  • Cache frequently accessed data"
            ])
        elif optimize_for == "memory":
            recommendations.extend([
                "💾 Memory Optimizations:",
                "  • Use generators instead of lists",
                "  • Implement object pooling",
                "  • Profile memory usage patterns"
            ])
        else:  # balanced
            recommendations.extend([
                "⚖️ Balanced Optimizations:",
                "  • Profile to identify bottlenecks",
                "  • Optimize the slowest component first",
                "  • Monitor resource usage during execution"
            ])
        
        return "\n".join(recommendations)
    
    def _format_benchmark_report(self, results: dict) -> str:
        """Format detailed benchmark report"""
        report = [
            "📊 PERFORMANCE BENCHMARK REPORT",
            "=" * 40,
            f"Benchmark Type: {results['benchmark_type']}",
            f"Test Duration: {results['test_duration']}s",
            f"Data Size: {results['data_size']}",
            f"Iterations: {results['iterations']}",
            f"Total Execution Time: {results.get('total_time', 0):.3f}s",
            ""
        ]
        
        metrics = results.get("metrics", {})
        
        if "error" in metrics:
            report.append(f"❌ Error: {metrics['error']}")
            return "\n".join(report)
        
        # Add type-specific metrics
        if results["benchmark_type"] == "mixed_workload":
            report.append("📈 MIXED WORKLOAD RESULTS:")
            
            cpu_perf = metrics.get("cpu_performance", {})
            if cpu_perf:
                report.append(f"  🔲 CPU: {cpu_perf.get('operations_per_second', 0):.1f} ops/sec")
            
            mem_perf = metrics.get("memory_performance", {})
            if mem_perf:
                report.append(f"  🔲 Memory: {mem_perf.get('allocations_per_second', 0):.1f} allocs/sec")
            
            io_perf = metrics.get("io_performance", {})
            if io_perf:
                report.append(f"  🔲 I/O: {io_perf.get('reads_per_second', 0):.1f} reads/sec")
            
            overall = metrics.get("overall_efficiency", 0)
            report.append(f"  🔲 Overall Efficiency: {overall:.1%}")
        
        else:
            # Single benchmark metrics
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    if "per_second" in key:
                        report.append(f"  • {key.replace('_', ' ').title()}: {value:.1f}")
                    elif "efficiency" in key:
                        report.append(f"  • {key.replace('_', ' ').title()}: {value:.1%}")
                    else:
                        report.append(f"  • {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(report)
    
    def _get_system_info(self) -> str:
        """Get basic system information"""
        import platform
        import sys
        
        info = [
            "💻 SYSTEM INFORMATION",
            "=" * 25,
            f"Platform: {platform.system()} {platform.release()}",
            f"Architecture: {platform.machine()}",
            f"Python Version: {sys.version.split()[0]}",
            f"Python Implementation: {platform.python_implementation()}"
        ]
        
        # Try to get CPU info
        try:
            import psutil
            info.append(f"CPU Cores: {psutil.cpu_count()}")
            info.append(f"Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        except ImportError:
            info.append("CPU/Memory info: Not available (psutil not installed)")
        
        return "\n".join(info)