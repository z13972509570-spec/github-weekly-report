"""Main module"""
import logging
from typing import Dict, List, Any
from dataclasses import dataclass
import json
import re

logger = logging.getLogger(__name__)

@dataclass
class Result:
    status: str
    data: Any
    message: str = ""

class Analyzer:
    """Core analyzer"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logger
    
    def analyze(self, data: Any) -> Result:
        """Analyze data"""
        try:
            processed = self._process(data)
            return Result(status="success", data=processed)
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return Result(status="error", data=None, message=str(e))
    
    def _process(self, data: Any) -> Dict:
        """Process implementation"""
        return {"input": str(data)[:100], "type": type(data).__name__}

class Reporter:
    """Generate reports"""
    
    def generate(self, data: Dict, format: str = "json") -> str:
        """Generate report"""
        if format == "json":
            return json.dumps(data, indent=2, ensure_ascii=False)
        elif format == "markdown":
            lines = ["# Report", ""]
            for k, v in data.items():
                lines.append(f"- **{k}**: {v}")
            return "
".join(lines)
        return str(data)

class CLI:
    """CLI interface"""
    
    def __init__(self):
        self.analyzer = Analyzer()
        self.reporter = Reporter()
    
    def run(self, data: Any, format: str = "json") -> str:
        """Run analysis"""
        result = self.analyzer.analyze(data)
        return self.reporter.generate({"status": result.status, "data": result.data}, format)

if __name__ == "__main__":
    cli = CLI()
    result = cli.run({"test": "data"})
    print(result)
