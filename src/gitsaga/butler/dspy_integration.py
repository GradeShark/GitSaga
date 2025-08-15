"""
DSPy integration for enforcing saga structure and quality.
Uses local LLMs (TinyLlama/Ollama) for zero-cost processing.
"""

import dspy
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import json
import subprocess
from pathlib import Path


@dataclass
class SagaStructure:
    """Structure for a complete saga based on user's documentation style"""
    
    # Problem Definition
    symptoms: str
    initial_issue: str
    user_impact: str
    
    # Investigation Timeline
    investigation_timeline: List[str]
    failed_attempts: List[str]
    breakthrough_moment: Optional[str]
    
    # Technical Details
    root_cause: str
    solution_code: str
    configuration_changes: Optional[str]
    
    # Verification & Learning
    verification_steps: List[str]
    lessons_learned: List[str]
    best_practices: List[str]
    
    # Metadata
    trust_impact: Optional[str]
    time_spent: Optional[str]
    complexity_factors: List[str]


class DebuggingSagaSignature(dspy.Signature):
    """DSPy signature for debugging sagas"""
    
    # Inputs
    commit_message = dspy.InputField(desc="Git commit message")
    files_changed = dspy.InputField(desc="List of files modified")
    diff_content = dspy.InputField(desc="Git diff excerpt")
    session_context = dspy.InputField(desc="AI session context if available", default="")
    
    # Outputs - Based on user's documentation patterns
    symptoms = dspy.OutputField(desc="What symptoms/errors were observed? Be specific with error messages.")
    investigation_steps = dspy.OutputField(desc="Timeline of investigation steps taken (Phase 1, Phase 2, etc)")
    failed_attempts = dspy.OutputField(desc="What solutions were tried but didn't work? Include why they failed.")
    root_cause = dspy.OutputField(desc="The actual root cause discovered")
    solution = dspy.OutputField(desc="The solution that fixed the issue")
    verification = dspy.OutputField(desc="How to verify the fix works")
    lessons = dspy.OutputField(desc="Key lessons learned from this debugging session")


class FeatureSagaSignature(dspy.Signature):
    """DSPy signature for feature implementation sagas"""
    
    # Inputs
    commit_message = dspy.InputField(desc="Git commit message")
    files_changed = dspy.InputField(desc="List of files modified")
    diff_content = dspy.InputField(desc="Git diff excerpt")
    
    # Outputs
    feature_description = dspy.OutputField(desc="What feature was implemented?")
    requirements = dspy.OutputField(desc="What were the requirements?")
    implementation_approach = dspy.OutputField(desc="How was it implemented?")
    key_decisions = dspy.OutputField(desc="What architectural decisions were made?")
    testing_approach = dspy.OutputField(desc="How was it tested?")
    future_considerations = dspy.OutputField(desc="What should be considered for future enhancements?")


class CriticalIncidentSignature(dspy.Signature):
    """DSPy signature for critical incident sagas"""
    
    # Inputs
    commit_message = dspy.InputField(desc="Git commit message")
    files_changed = dspy.InputField(desc="List of files modified")
    diff_content = dspy.InputField(desc="Git diff excerpt")
    
    # Outputs
    incident_summary = dspy.OutputField(desc="Executive summary of the incident")
    timeline = dspy.OutputField(desc="Timeline of events (discovery, escalation, resolution)")
    impact = dspy.OutputField(desc="User/system impact assessment")
    root_causes = dspy.OutputField(desc="Primary and secondary root causes")
    immediate_fix = dspy.OutputField(desc="What was done to resolve immediately")
    long_term_fix = dspy.OutputField(desc="Long-term preventive measures")
    postmortem = dspy.OutputField(desc="Key postmortem findings")


class SagaEnhancer:
    """
    Enhances saga content using DSPy to ensure completeness and quality.
    Uses local LLMs for zero-cost operation.
    """
    
    def __init__(self, model: str = "tinyllama", use_local: bool = True):
        """
        Initialize the SagaEnhancer.
        
        Args:
            model: Model to use (tinyllama, llama2, mistral, etc)
            use_local: Use local Ollama instead of API
        """
        self.model = model
        self.use_local = use_local
        
        if use_local:
            # Configure DSPy to use local Ollama
            self._setup_ollama()
        
        # Create DSPy modules for each saga type
        self.debugging_module = dspy.ChainOfThought(DebuggingSagaSignature)
        self.feature_module = dspy.ChainOfThought(FeatureSagaSignature)
        self.incident_module = dspy.ChainOfThought(CriticalIncidentSignature)
        
        # Compile modules with examples if available
        self._compile_modules()
    
    def _setup_ollama(self):
        """Setup Ollama as the LLM backend"""
        try:
            # Check if Ollama is running
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode != 0:
                print("Warning: Ollama not running. Starting Ollama...")
                subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Pull model if not available
            if self.model not in result.stdout:
                print(f"Pulling {self.model} model...")
                subprocess.run(['ollama', 'pull', self.model], check=True)
            
            # Configure DSPy to use Ollama
            ollama_lm = dspy.OllamaLocal(
                model=self.model,
                temperature=0.7,
                max_tokens=2000
            )
            dspy.settings.configure(lm=ollama_lm)
            
        except FileNotFoundError:
            print("Warning: Ollama not installed. Install from https://ollama.ai")
            print("Falling back to basic saga generation without AI enhancement.")
            self.use_local = False
        except Exception as e:
            print(f"Warning: Could not setup Ollama: {e}")
            self.use_local = False
    
    def _compile_modules(self):
        """Compile DSPy modules with examples from user's documentation"""
        # Load examples from bug-doc-examples if available
        examples_dir = Path.cwd() / 'bug-doc-examples'
        if not examples_dir.exists():
            return
        
        examples = []
        for example_file in examples_dir.glob('*.md'):
            try:
                with open(example_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract key sections from the example
                # This is a simplified extraction - could be enhanced
                example = {
                    'content': content[:1000],  # First 1000 chars as context
                    'has_timeline': 'Timeline' in content or 'Phase' in content,
                    'has_root_cause': 'Root Cause' in content or 'root cause' in content.lower(),
                    'has_lessons': 'Lessons Learned' in content,
                    'has_verification': 'Verification' in content or 'Testing' in content
                }
                examples.append(example)
                
            except Exception as e:
                print(f"Could not load example {example_file}: {e}")
                continue
        
        if examples:
            print(f"Loaded {len(examples)} documentation examples for training")
            # In a real implementation, we'd use these to compile the modules
            # self.debugging_module = dspy.compile(self.debugging_module, examples)
    
    def enhance_saga(self, saga_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance saga content using DSPy to ensure completeness.
        
        Args:
            saga_type: Type of saga (debugging, feature, incident)
            context: Context including commit info, files, diff, etc
            
        Returns:
            Enhanced saga content dictionary
        """
        if not self.use_local:
            return self._basic_enhancement(saga_type, context)
        
        try:
            if saga_type == 'debugging':
                result = self.debugging_module(
                    commit_message=context.get('commit_message', ''),
                    files_changed=str(context.get('files_changed', [])),
                    diff_content=context.get('diff_content', '')[:1000],
                    session_context=context.get('session_context', '')
                )
                
                return {
                    'symptoms': result.symptoms,
                    'investigation_steps': result.investigation_steps,
                    'failed_attempts': result.failed_attempts,
                    'root_cause': result.root_cause,
                    'solution': result.solution,
                    'verification': result.verification,
                    'lessons': result.lessons
                }
                
            elif saga_type == 'feature':
                result = self.feature_module(
                    commit_message=context.get('commit_message', ''),
                    files_changed=str(context.get('files_changed', [])),
                    diff_content=context.get('diff_content', '')[:1000]
                )
                
                return {
                    'feature_description': result.feature_description,
                    'requirements': result.requirements,
                    'implementation_approach': result.implementation_approach,
                    'key_decisions': result.key_decisions,
                    'testing_approach': result.testing_approach,
                    'future_considerations': result.future_considerations
                }
                
            elif saga_type in ['incident', 'critical']:
                result = self.incident_module(
                    commit_message=context.get('commit_message', ''),
                    files_changed=str(context.get('files_changed', [])),
                    diff_content=context.get('diff_content', '')[:1000]
                )
                
                return {
                    'incident_summary': result.incident_summary,
                    'timeline': result.timeline,
                    'impact': result.impact,
                    'root_causes': result.root_causes,
                    'immediate_fix': result.immediate_fix,
                    'long_term_fix': result.long_term_fix,
                    'postmortem': result.postmortem
                }
                
            else:
                return self._basic_enhancement(saga_type, context)
                
        except Exception as e:
            print(f"Error during DSPy enhancement: {e}")
            return self._basic_enhancement(saga_type, context)
    
    def _basic_enhancement(self, saga_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback enhancement without AI"""
        commit_msg = context.get('commit_message', '')
        files = context.get('files_changed', [])
        
        # Extract what we can from the commit message
        enhancement = {
            'generated_without_ai': True,
            'saga_type': saga_type,
            'commit_summary': commit_msg.split('\n')[0] if commit_msg else 'No commit message',
            'files_modified': len(files),
            'primary_files': files[:5] if files else []
        }
        
        # Add type-specific placeholders
        if saga_type == 'debugging':
            enhancement.update({
                'symptoms': '[To be filled: What errors/issues were observed?]',
                'investigation_steps': '[To be filled: How was the issue investigated?]',
                'failed_attempts': '[To be filled: What didn\'t work?]',
                'root_cause': '[To be filled: What was the actual cause?]',
                'solution': commit_msg,
                'verification': '[To be filled: How to verify the fix?]',
                'lessons': '[To be filled: What was learned?]'
            })
        elif saga_type == 'feature':
            enhancement.update({
                'feature_description': commit_msg.split('\n')[0] if commit_msg else '[To be filled]',
                'requirements': '[To be filled: What were the requirements?]',
                'implementation_approach': '[To be filled: Implementation details]',
                'key_decisions': '[To be filled: Architecture decisions]',
                'testing_approach': '[To be filled: How was it tested?]',
                'future_considerations': '[To be filled: Future enhancements]'
            })
        else:
            enhancement.update({
                'content': commit_msg,
                'needs_manual_enhancement': True
            })
        
        return enhancement
    
    def validate_saga_completeness(self, saga_content: str, saga_type: str) -> Dict[str, Any]:
        """
        Validate that a saga has all required sections.
        
        Args:
            saga_content: The saga markdown content
            saga_type: Type of saga
            
        Returns:
            Validation result with missing sections
        """
        required_sections = {
            'debugging': [
                'symptoms', 'investigation', 'root cause', 
                'solution', 'verification', 'lessons'
            ],
            'feature': [
                'requirements', 'implementation', 'testing',
                'documentation'
            ],
            'incident': [
                'timeline', 'impact', 'root cause',
                'resolution', 'postmortem'
            ]
        }
        
        sections_to_check = required_sections.get(saga_type, [])
        content_lower = saga_content.lower()
        
        missing = []
        present = []
        
        for section in sections_to_check:
            if section in content_lower:
                present.append(section)
            else:
                missing.append(section)
        
        completeness_score = len(present) / len(sections_to_check) if sections_to_check else 0
        
        return {
            'is_complete': len(missing) == 0,
            'completeness_score': completeness_score,
            'present_sections': present,
            'missing_sections': missing,
            'recommendations': self._get_recommendations(missing)
        }
    
    def _get_recommendations(self, missing_sections: List[str]) -> List[str]:
        """Get recommendations for missing sections"""
        recommendations = []
        
        section_prompts = {
            'symptoms': "Add a 'Symptoms' section describing what errors or issues were observed",
            'investigation': "Add an 'Investigation' section with the timeline of debugging steps",
            'root cause': "Add a 'Root Cause' section explaining the actual problem",
            'solution': "Add a 'Solution' section with the code changes that fixed the issue",
            'verification': "Add a 'Verification' section explaining how to test the fix",
            'lessons': "Add a 'Lessons Learned' section with key takeaways",
            'requirements': "Add a 'Requirements' section outlining what was needed",
            'implementation': "Add an 'Implementation' section with technical details",
            'testing': "Add a 'Testing' section describing test coverage",
            'timeline': "Add a 'Timeline' section with chronological events",
            'impact': "Add an 'Impact' section assessing user/system effects",
            'postmortem': "Add a 'Postmortem' section with findings and action items"
        }
        
        for section in missing_sections:
            if section in section_prompts:
                recommendations.append(section_prompts[section])
        
        return recommendations
    
    def generate_saga_template(self, saga_type: str) -> str:
        """
        Generate a markdown template for a specific saga type.
        Based on the user's documentation examples.
        """
        templates = {
            'debugging': """# [Bug Title]

**Date**: [Date]
**Issue Type**: Bug Fix
**Severity**: [HIGH/MEDIUM/LOW]
**Status**: FIXED

---

## 📋 The Problem

### Symptoms
- [Error message or behavior observed]
- [User impact]

### Initial Discovery
[How the issue was discovered]

---

## 🔍 Investigation Timeline

### Phase 1: Initial Investigation
[What was checked first]

### Phase 2: Deep Dive
[Detailed debugging steps]

### Phase 3: Breakthrough
[The "aha" moment]

---

## ❌ Failed Attempts

1. **Attempt 1**: [What was tried]
   - Why it failed: [Reason]

2. **Attempt 2**: [What was tried]
   - Why it failed: [Reason]

---

## ✅ Root Cause

[The actual problem discovered]

### Technical Details
```
[Code or configuration that was wrong]
```

---

## 💡 Solution

### Code Changes
```diff
[Show the diff of the fix]
```

### Configuration Changes
[Any config updates needed]

---

## 🧪 Verification

1. [Step to verify fix works]
2. [Another verification step]

### Test Results
[Confirmation that fix works]

---

## 📝 Lessons Learned

1. [Key lesson from this debugging session]
2. [Another important takeaway]

### Best Practices
- [Practice to follow in future]

---

**Time Spent**: [Hours]
**Complexity**: [HIGH/MEDIUM/LOW]
""",

            'feature': """# [Feature Name]

**Date**: [Date]
**Type**: Feature Implementation
**Status**: COMPLETED

---

## 📋 Feature Overview

[Brief description of the feature]

---

## 📝 Requirements

### User Stories
- As a [user type], I want to [action] so that [benefit]

### Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

---

## 🏗️ Implementation

### Architecture Decision
[Key decisions made]

### Technical Approach
[How it was built]

### Code Structure
```
[Key code organization]
```

---

## 🧪 Testing

### Test Coverage
- Unit tests: [Coverage]
- Integration tests: [Coverage]

### Test Cases
1. [Test scenario 1]
2. [Test scenario 2]

---

## 📚 Documentation

### API Changes
[Any API modifications]

### User Guide
[How users interact with feature]

---

## 🚀 Deployment

### Migration Steps
[If any migrations needed]

### Configuration
[Required config changes]

---

## 🔮 Future Enhancements

- [Possible improvement 1]
- [Possible improvement 2]
""",

            'incident': """# [Incident Title]

**Date**: [Date]
**Severity**: CRITICAL
**Status**: RESOLVED

---

## 📊 Executive Summary

[One paragraph summary of incident]

---

## 🕐 Timeline of Events

### [Time] - Discovery
[How incident was discovered]

### [Time] - Initial Response
[First actions taken]

### [Time] - Escalation
[When/why escalated]

### [Time] - Resolution
[When/how resolved]

---

## 💥 Impact Assessment

### User Impact
- [Number of users affected]
- [Duration of impact]

### System Impact
- [Services affected]
- [Data impact if any]

### Business Impact
- [Revenue/reputation impact]

---

## 🔍 Root Cause Analysis

### Primary Cause
[Main reason for incident]

### Contributing Factors
1. [Factor 1]
2. [Factor 2]

---

## 🚨 Immediate Actions

1. [Emergency fix applied]
2. [Mitigation step]

---

## 📋 Long-term Fixes

1. [Permanent solution]
2. [Preventive measure]

---

## 📝 Postmortem

### What Went Well
- [Positive aspect]

### What Went Wrong
- [Failure point]

### Action Items
- [ ] [Action with owner and deadline]
- [ ] [Another action]

---

**Incident Commander**: [Name]
**Duration**: [Total time to resolve]
"""
        }
        
        return templates.get(saga_type, templates['debugging'])