# Development Plan: MCP Protocol Implementation

This plan outlines the conversion from REST API services to true MCP (Model Context Protocol) servers using stdio/JSON-RPC communication that can be tested locally and easily migrated to Azure.

---

## Phase 5: MCP Protocol Implementation (NEW - Priority Sprint)

**Objective:** Convert existing REST API services to true MCP protocol servers with stdio/JSON-RPC communication.

### Understanding MCP Architecture

MCP servers communicate via:
- **Transport:** stdio (stdin/stdout) or HTTP with SSE
- **Protocol:** JSON-RPC 2.0
- **Message Types:** Requests, responses, and notifications
- **Lifecycle:** Initialize → Resources/Tools discovery → Execute → Shutdown

### Step 1: MCP Server Foundation

- [ ] **Create MCP Base Server (`/dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools/mcp_server.py`)**
    - [ ] Implement JSON-RPC 2.0 message handler for stdio communication
    - [ ] Create base MCP server class with:
        - `initialize` method (capabilities negotiation)
        - `tools/list` method (list available tools)
        - `tools/call` method (execute specific tool)
        - `resources/list` method (list available resources)
        - `shutdown` method (graceful shutdown)
    - [ ] Implement error handling and logging to stderr (stdout is reserved for JSON-RPC)
    - [ ] Write pytest tests for JSON-RPC message parsing and response formatting

- [ ] **Create MCP Client for Testing (`/dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools/mcp_client.py`)**
    - [ ] Implement stdio client that can spawn MCP server processes
    - [ ] Add methods to send JSON-RPC requests and parse responses
    - [ ] Create interactive CLI for testing MCP servers locally
    - [ ] Write integration tests for client-server communication

### Step 2: Convert Individual Tools to MCP Format

- [ ] **Create Tool Wrapper (`/dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools/mcp_tool_wrapper.py`)**
    - [ ] Create adapter that wraps existing tool modules for MCP
    - [ ] Map tool parameters to MCP tool schema format
    - [ ] Handle tool execution and result formatting
    - [ ] Implement tool discovery from existing `/tools` directory

- [ ] **Update Tool Definitions**
    - [ ] Create MCP tool manifests for each tool with:
        - Tool name and description
        - Input schema (JSON Schema format)
        - Output schema
        - Required resources/permissions
    - [ ] Test each tool through MCP interface

### Step 3: Convert Schedule Optimizer Services to MCP

- [ ] **Convert ProtocolComplexityAnalyzer to MCP (`/services/mcp_ProtocolComplexityAnalyzer/mcp_server.py`)**
    - [ ] Implement MCP server inheriting from base class
    - [ ] Define tools: `analyze-complexity`, `get-complexity-metrics`
    - [ ] Implement resource access for complexity rules database
    - [ ] Create startup script that launches via stdio
    - [ ] Write tests for MCP communication

- [ ] **Convert ComplianceKnowledgeBase to MCP (`/services/mcp_ComplianceKnowledgeBase/mcp_server.py`)**
    - [ ] Implement MCP server inheriting from base class
    - [ ] Define tools: `check-compliance`, `get-regulations`, `validate-schedule`
    - [ ] Implement resource access for compliance database
    - [ ] Create startup script that launches via stdio
    - [ ] Write tests for MCP communication

### Step 4: Create MCP Configuration System

- [ ] **MCP Configuration Files**
    - [ ] Create `mcp_config.json` for each server with:
        ```json
        {
          "name": "dcri-protocol-complexity",
          "version": "1.0.0",
          "description": "Protocol complexity analysis MCP server",
          "command": "python",
          "args": ["mcp_server.py"],
          "env": {},
          "capabilities": {
            "tools": true,
            "resources": true,
            "notifications": false
          }
        }
        ```
    - [ ] Create `.env.mcp` for environment-specific settings
    - [ ] Document configuration options

- [ ] **Service Discovery**
    - [ ] Create MCP registry file listing all available servers
    - [ ] Implement auto-discovery mechanism for local development
    - [ ] Create health check mechanism for each MCP server

### Step 5: Update Backend to Use MCP Servers

- [ ] **Create MCP Client Integration (`backend/mcp_integration.py`)**
    - [ ] Implement MCP client that can spawn and communicate with MCP servers
    - [ ] Create connection pool for managing multiple MCP server processes
    - [ ] Add retry logic and error handling
    - [ ] Implement caching layer for MCP responses

- [ ] **Update main.py to Use MCP**
    - [ ] Replace HTTP calls to services with MCP client calls
    - [ ] Add configuration to switch between REST and MCP modes
    - [ ] Implement fallback to REST if MCP servers unavailable
    - [ ] Update error handling for MCP-specific errors

### Step 6: Local Development & Testing Setup

- [ ] **Create MCP Development Environment**
    - [ ] Create `start_mcp_servers.sh` script that:
        - Starts all MCP servers in background
        - Monitors server health
        - Provides logs aggregation
        - Handles graceful shutdown
    - [ ] Create `test_mcp_integration.py` for end-to-end testing
    - [ ] Document local setup process

- [ ] **Docker Support for MCP**
    - [ ] Create Dockerfile for MCP servers with:
        - Minimal Python runtime
        - MCP server code
        - Health check endpoint
    - [ ] Update docker-compose.yml to support both REST and MCP modes
    - [ ] Add MCP server containers with proper stdio handling

### Step 7: Azure Migration Preparation

- [ ] **Azure-Ready MCP Configuration**
    - [ ] Create Azure Container Instance configurations for MCP servers
    - [ ] Implement Azure Service Bus integration for MCP communication (alternative to stdio)
    - [ ] Create Key Vault integration for MCP server secrets
    - [ ] Document Azure deployment process

- [ ] **Monitoring & Logging**
    - [ ] Implement Application Insights integration for MCP servers
    - [ ] Create custom metrics for MCP performance
    - [ ] Set up alerts for MCP server failures
    - [ ] Create dashboard for MCP server monitoring

### Step 8: Testing & Validation

- [ ] **Comprehensive Testing Suite**
    - [ ] Unit tests for each MCP server component
    - [ ] Integration tests for client-server communication
    - [ ] Load tests for MCP server performance
    - [ ] Chaos engineering tests (server crashes, network issues)

- [ ] **Documentation**
    - [ ] Create MCP Server Developer Guide
    - [ ] Document MCP tool creation process
    - [ ] Create troubleshooting guide
    - [ ] Write migration guide from REST to MCP

### Step 9: Gradual Migration Strategy

- [ ] **Feature Flags Implementation**
    - [ ] Add feature flags to switch between REST and MCP per service
    - [ ] Implement A/B testing capability
    - [ ] Create metrics to compare REST vs MCP performance
    - [ ] Document rollback procedures

- [ ] **Phased Rollout Plan**
    - [ ] Phase 1: Deploy MCP servers alongside REST (shadow mode)
    - [ ] Phase 2: Route 10% traffic to MCP servers
    - [ ] Phase 3: Route 50% traffic to MCP servers
    - [ ] Phase 4: Full migration to MCP servers
    - [ ] Create rollback plan for each phase

---

## Benefits of This Approach

1. **Local Development:** MCP servers run as separate processes, easy to debug
2. **Azure Ready:** Can be containerized and deployed to Azure Container Instances
3. **Protocol Compliant:** True JSON-RPC 2.0 over stdio, compatible with any MCP client
4. **Gradual Migration:** Can run REST and MCP side-by-side during transition
5. **Tool Reuse:** Existing tool code can be wrapped without rewriting

---

## Quick Start Commands (Once Implemented)

```bash
# Start all MCP servers locally
./start_mcp_servers.sh

# Test MCP server communication
python mcp_client.py test protocol-complexity

# Run with Docker
docker-compose -f docker-compose.mcp.yml up

# Run integration tests
pytest tests/test_mcp_integration.py -v
```

---

## Next Steps

1. Start with Step 1: Create the base MCP server implementation
2. Test with a simple tool (e.g., echo tool)
3. Gradually migrate complex tools
4. Keep REST API as fallback during transition

---

## Resources

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

---

## Archive Note

Completed tasks from Phases 1-4 have been moved to `archive/development_checklist_archive.md`