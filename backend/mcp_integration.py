"""
MCP Client Integration for Backend
Provides connection pooling and management for MCP servers
"""

import json
import os
import sys
import subprocess
import threading
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Add MCP tools to path
sys.path.insert(0, '/dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools')

from mcp_client import MCPClient, MCPServerConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCPServiceConfig:
    """Configuration for MCP service"""
    name: str
    command: List[str]
    cwd: str
    tools: List[str]
    description: str = ""
    enabled: bool = True


class MCPConnectionPool:
    """Manages pool of MCP client connections"""

    def __init__(self, max_connections: int = 5):
        self.max_connections = max_connections
        self.connections: Dict[str, List[MCPClient]] = {}
        self.available: Dict[str, List[MCPClient]] = {}
        self.in_use: Dict[str, List[MCPClient]] = {}
        self.lock = threading.Lock()
        self.configs: Dict[str, MCPServiceConfig] = {}
        self._load_configs()

    def _load_configs(self):
        """Load MCP service configurations"""

        # Protocol Complexity Analyzer
        self.configs['complexity'] = MCPServiceConfig(
            name='protocol-complexity-analyzer',
            command=['python', 'mcp_server.py'],
            cwd='/dcri/sasusers/home/scb2/gitRepos/schedule-assessments-optimizer/services/mcp_ProtocolComplexityAnalyzer',
            tools=['analyze-complexity', 'analyze-visit-burden', 'get-complexity-metrics'],
            description='Protocol complexity analysis service'
        )

        # Compliance Knowledge Base
        self.configs['compliance'] = MCPServiceConfig(
            name='compliance-knowledge-base',
            command=['python', 'mcp_server.py'],
            cwd='/dcri/sasusers/home/scb2/gitRepos/schedule-assessments-optimizer/services/mcp_ComplianceKnowledgeBase',
            tools=['check-compliance', 'get-regulations', 'validate-schedule'],
            description='Regulatory compliance checking service'
        )

        # Main MCP Tools (optional - for additional tools)
        self.configs['tools'] = MCPServiceConfig(
            name='dcri-mcp-tools',
            command=['python', 'mcp_tool_wrapper.py'],
            cwd='/dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools',
            tools=['study_complexity_calculator', 'compliance_knowledge_base', 'sql_reviewer'],
            description='Main DCRI MCP tools service',
            enabled=False  # Disabled by default to avoid duplication
        )

    def get_connection(self, service_name: str) -> Optional[MCPClient]:
        """Get an available connection from the pool"""

        with self.lock:
            # Initialize pool for service if needed
            if service_name not in self.available:
                self._initialize_service_pool(service_name)

            # Get available connection
            if self.available[service_name]:
                client = self.available[service_name].pop()
                if service_name not in self.in_use:
                    self.in_use[service_name] = []
                self.in_use[service_name].append(client)
                return client

            # Create new connection if under limit
            if len(self.connections.get(service_name, [])) < self.max_connections:
                client = self._create_connection(service_name)
                if client:
                    self.connections[service_name].append(client)
                    if service_name not in self.in_use:
                        self.in_use[service_name] = []
                    self.in_use[service_name].append(client)
                    return client

        logger.warning(f"No available connections for service: {service_name}")
        return None

    def release_connection(self, service_name: str, client: MCPClient):
        """Release a connection back to the pool"""

        with self.lock:
            if service_name in self.in_use and client in self.in_use[service_name]:
                self.in_use[service_name].remove(client)
                if service_name not in self.available:
                    self.available[service_name] = []
                self.available[service_name].append(client)

    def _initialize_service_pool(self, service_name: str):
        """Initialize connection pool for a service"""

        if service_name not in self.configs:
            logger.error(f"Unknown service: {service_name}")
            return

        config = self.configs[service_name]
        if not config.enabled:
            logger.info(f"Service {service_name} is disabled")
            return

        self.connections[service_name] = []
        self.available[service_name] = []
        self.in_use[service_name] = []

        # Create initial connection
        client = self._create_connection(service_name)
        if client:
            self.connections[service_name].append(client)
            self.available[service_name].append(client)

    def _create_connection(self, service_name: str) -> Optional[MCPClient]:
        """Create a new MCP client connection"""

        if service_name not in self.configs:
            return None

        config = self.configs[service_name]

        server_config = MCPServerConfig(
            name=config.name,
            command=config.command,
            description=config.description,
            cwd=config.cwd
        )

        client = MCPClient(server_config)

        try:
            if client.start():
                logger.info(f"Started MCP connection to {service_name}")
                return client
            else:
                logger.error(f"Failed to start MCP connection to {service_name}")
                return None
        except Exception as e:
            logger.error(f"Error creating MCP connection: {e}")
            return None

    def close_all(self):
        """Close all connections in the pool"""

        with self.lock:
            for service_name in self.connections:
                for client in self.connections[service_name]:
                    try:
                        client.stop()
                    except:
                        pass

            self.connections.clear()
            self.available.clear()
            self.in_use.clear()


class MCPIntegration:
    """High-level MCP integration for backend"""

    def __init__(self, use_mcp: bool = True, fallback_to_rest: bool = True):
        self.use_mcp = use_mcp and os.getenv('USE_MCP', 'true').lower() == 'true'
        self.fallback_to_rest = fallback_to_rest
        self.pool = MCPConnectionPool() if self.use_mcp else None
        self.executor = ThreadPoolExecutor(max_workers=5)

    async def analyze_complexity(self, protocol_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze protocol complexity using MCP service"""

        if not self.use_mcp:
            return await self._rest_fallback('complexity', protocol_data)

        try:
            # Get MCP client from pool
            client = self.pool.get_connection('complexity')
            if not client:
                if self.fallback_to_rest:
                    return await self._rest_fallback('complexity', protocol_data)
                return None

            try:
                # Call MCP tool
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    client.call_tool,
                    'analyze-complexity',
                    protocol_data
                )

                # Parse result
                if result and 'content' in result:
                    content = result['content'][0]
                    if content['type'] == 'text':
                        return json.loads(content['text'])

                return None

            finally:
                # Release connection back to pool
                self.pool.release_connection('complexity', client)

        except Exception as e:
            logger.error(f"Error calling MCP complexity service: {e}")
            if self.fallback_to_rest:
                return await self._rest_fallback('complexity', protocol_data)
            return None

    async def check_compliance(self, schedule_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check compliance using MCP service"""

        if not self.use_mcp:
            return await self._rest_fallback('compliance', schedule_data)

        try:
            # Get MCP client from pool
            client = self.pool.get_connection('compliance')
            if not client:
                if self.fallback_to_rest:
                    return await self._rest_fallback('compliance', schedule_data)
                return None

            try:
                # Call MCP tool
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    client.call_tool,
                    'check-compliance',
                    schedule_data
                )

                # Parse result
                if result and 'content' in result:
                    content = result['content'][0]
                    if content['type'] == 'text':
                        return json.loads(content['text'])

                return None

            finally:
                # Release connection back to pool
                self.pool.release_connection('compliance', client)

        except Exception as e:
            logger.error(f"Error calling MCP compliance service: {e}")
            if self.fallback_to_rest:
                return await self._rest_fallback('compliance', schedule_data)
            return None

    async def _rest_fallback(self, service: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fallback to REST API if MCP is unavailable"""

        import httpx

        try:
            if service == 'complexity':
                # Call REST API for complexity analysis
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "http://localhost:8001/analyze-complexity",
                        json=data,
                        timeout=30.0
                    )
                    if response.status_code == 200:
                        return response.json()

            elif service == 'compliance':
                # Call REST API for compliance check
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "http://localhost:8002/check-compliance",
                        json=data,
                        timeout=30.0
                    )
                    if response.status_code == 200:
                        return response.json()

        except Exception as e:
            logger.error(f"REST fallback failed: {e}")

        return None

    def close(self):
        """Clean up resources"""
        if self.pool:
            self.pool.close_all()
        self.executor.shutdown(wait=True)


# Singleton instance
_mcp_integration: Optional[MCPIntegration] = None


def get_mcp_integration() -> MCPIntegration:
    """Get singleton MCP integration instance"""
    global _mcp_integration
    if _mcp_integration is None:
        _mcp_integration = MCPIntegration()
    return _mcp_integration


async def test_mcp_integration():
    """Test MCP integration"""

    integration = get_mcp_integration()

    # Test complexity analysis
    complexity_data = {
        "protocol_name": "Test Protocol",
        "phase": "2",
        "num_visits": 10,
        "num_procedures": 50,
        "duration_days": 180,
        "num_sites": 5
    }

    print("Testing complexity analysis...")
    result = await integration.analyze_complexity(complexity_data)
    if result:
        print(f"Complexity score: {result.get('complexity_score')}")
        print(f"Complexity level: {result.get('complexity_level')}")
    else:
        print("Complexity analysis failed")

    # Test compliance check
    compliance_data = {
        "schedule_data": {
            "protocol_name": "Test Protocol",
            "phase": "2",
            "visits": [
                {
                    "name": "Screening",
                    "day": 0,
                    "assessments": [
                        {"name": "Informed Consent"},
                        {"name": "Medical History"}
                    ]
                }
            ]
        },
        "region": "US"
    }

    print("\nTesting compliance check...")
    result = await integration.check_compliance(compliance_data)
    if result:
        print(f"Compliance score: {result.get('compliance_score')}")
        print(f"Status: {result.get('status')}")
    else:
        print("Compliance check failed")

    # Clean up
    integration.close()


if __name__ == "__main__":
    # Run test
    asyncio.run(test_mcp_integration())