"""
SagaShark MCP Server - Expose SagaShark as an MCP tool for Claude
"""

import json
import asyncio
from typing import Any, Dict, List
from pathlib import Path

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from .search.text_search import TextSearcher
from .capture.auto_chronicler import AutoChronicler
from .capture.significance import SignificanceScorer, CommitContext


class SagaSharkMCPServer:
    """MCP Server exposing SagaShark functionality to Claude"""
    
    def __init__(self):
        self.server = Server("sagashark")
        self.saga_dir = Path.cwd() / '.sagashark'
        self.setup_handlers()
    
    def setup_handlers(self):
        """Register MCP tool handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available SagaShark tools"""
            return [
                types.Tool(
                    name="search_sagas",
                    description="Search for relevant past debugging sessions and solutions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (e.g., 'timeout', 'redis bug')"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Max results to return",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="find_similar_issues",
                    description="Find similar past issues to current problem",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Description of current issue"
                            }
                        },
                        "required": ["description"]
                    }
                ),
                types.Tool(
                    name="capture_context",
                    description="Capture current debugging context as a saga",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title for this debugging session"
                            },
                            "context": {
                                "type": "string",
                                "description": "Debugging context and findings"
                            },
                            "solution": {
                                "type": "string",
                                "description": "Solution found (if any)"
                            }
                        },
                        "required": ["title", "context"]
                    }
                ),
                types.Tool(
                    name="score_commit",
                    description="Check if a commit is significant enough for a saga",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "commit": {
                                "type": "string",
                                "description": "Commit hash or 'HEAD'",
                                "default": "HEAD"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_debugging_template",
                    description="Get a template for documenting debugging sessions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["debugging", "feature", "incident"],
                                "default": "debugging"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str,
            arguments: Dict[str, Any]
        ) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool calls from Claude"""
            
            if name == "search_sagas":
                searcher = TextSearcher(self.saga_dir)
                results = searcher.search(
                    arguments["query"],
                    limit=arguments.get("limit", 5)
                )
                
                if not results:
                    return [types.TextContent(
                        type="text",
                        text="No matching sagas found."
                    )]
                
                response = f"Found {len(results)} relevant sagas:\n\n"
                for i, saga in enumerate(results, 1):
                    response += f"{i}. **{saga.title}** (Score: {saga.score:.1f})\n"
                    response += f"   Type: {saga.saga_type} | Date: {saga.timestamp.strftime('%Y-%m-%d')}\n"
                    response += f"   Preview: {saga.get_preview(max_lines=2)[:150]}...\n\n"
                
                return [types.TextContent(type="text", text=response)]
            
            elif name == "find_similar_issues":
                # This would use vector search when available
                searcher = TextSearcher(self.saga_dir)
                results = searcher.search(
                    arguments["description"],
                    limit=5
                )
                
                if not results:
                    return [types.TextContent(
                        type="text",
                        text="No similar issues found in saga history."
                    )]
                
                response = "Similar past issues:\n\n"
                for i, saga in enumerate(results, 1):
                    response += f"{i}. **{saga.title}**\n"
                    response += f"   {saga.get_preview(max_lines=3)[:200]}...\n\n"
                
                return [types.TextContent(type="text", text=response)]
            
            elif name == "capture_context":
                from .core.saga import Saga
                
                saga = Saga(
                    title=arguments["title"],
                    content=arguments["context"],
                    saga_type="debugging" if "fix" in arguments["title"].lower() else "general"
                )
                
                if "solution" in arguments:
                    saga.content += f"\n\n## Solution\n{arguments['solution']}"
                
                saga_path = saga.save(self.saga_dir / 'sagas')
                
                return [types.TextContent(
                    type="text",
                    text=f"✓ Saga captured: {saga.title}\nSaved to: {saga_path.name}"
                )]
            
            elif name == "score_commit":
                chronicler = AutoChronicler()
                context = chronicler._get_commit_context(arguments.get("commit", "HEAD"))
                
                if not context:
                    return [types.TextContent(
                        type="text",
                        text="Could not analyze commit."
                    )]
                
                scorer = SignificanceScorer()
                result = scorer.calculate_score(context)
                
                response = f"Commit Score: {result['score']:.2f}\n"
                response += f"Significant: {'Yes' if result['is_significant'] else 'No'}\n"
                response += f"Type: {result['suggested_type']}\n"
                response += f"Factors: {', '.join(result['factors'])}"
                
                return [types.TextContent(type="text", text=response)]
            
            elif name == "get_debugging_template":
                from .butler.dspy_integration import SagaEnhancer
                
                enhancer = SagaEnhancer(use_local=False)
                template = enhancer.generate_saga_template(arguments.get("type", "debugging"))
                
                return [types.TextContent(type="text", text=template)]
            
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
    
    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="sagashark",
                    server_version="2.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


def main():
    """Entry point for MCP server"""
    server = SagaSharkMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()