# Technical Requirements Document  
**Project:** MCP Server for Automated Ilograph Diagram Generation  
**Purpose:** Enable AI assistants (JetBrains AI Assistant, GitHub Copilot) to generate Ilograph diagrams from codebases via Model Context Protocol (MCP).

---

## 1. Overview

This document details the technical requirements for designing, developing, deploying, and maintaining an MCP server that analyzes codebases and produces Ilograph diagrams. The server will expose its capabilities to AI assistants via the MCP standard, supporting real-time, automated architecture visualization.

---

## 2. Functional Requirements

- **Codebase Analysis**
  - Parse and analyze supported codebases (e.g., Python, JavaScript/TypeScript, Java) to extract architectural entities and relationships.
  - Support recursive directory traversal and modular analysis.
  - Detect classes, interfaces, modules, services, databases, and their relationships.

- **Ilograph Diagram Generation**
  - Transform the extracted architecture model into valid Ilograph YAML format (.ilograph files).
  - Support multiple diagram perspectives (e.g., microservices, data flow, object-oriented).
  - Generate native .ilograph files for direct use in Ilograph editor.
  - Optionally render diagrams as SVG/PNG/PDF via Ilograph Export API (when API key provided).

- **MCP Protocol Support**
  - Implement MCP tool interfaces for:
    - Codebase analysis
    - Diagram generation
    - Output management (file save, API upload)
  - Support communication over stdio and/or HTTP (JSON-RPC).

- **Integration with AI Assistants**
  - Expose server as a tool to JetBrains AI Assistant and GitHub Copilot via MCP.
  - Accept structured requests and return diagram artifacts or links.

- **Security**
  - Secure handling of API keys, secrets, and user data.
  - Enforce authentication and authorization where applicable.

- **Logging & Monitoring**
  - Log all requests, responses, errors, and performance metrics.
  - Expose health endpoints or logs for monitoring.

---

## 3. Non-Functional Requirements

- **Performance**
  - Handle concurrent requests efficiently (multi-threaded/multi-process).
  - Analyze medium-sized codebases (up to 10,000 files) in under 2 minutes.
  - Render diagrams in under 10 seconds per request.

- **Scalability**
  - Support horizontal scaling via container orchestration (Docker, Kubernetes).
  - Allow for load balancing and auto-scaling in production deployments[1][4].

- **Reliability**
  - Graceful error handling and clear error messages.
  - Automatic recovery from transient failures.

- **Maintainability**
  - Modular, well-documented codebase.
  - Automated tests and CI/CD integration.

- **Portability**
  - Deployable on Linux (Ubuntu 22.04 LTS recommended), with support for Docker containers[1].

---

## 4. System Architecture

- **Client Layer:** IDE plugin (AI assistant) or CLI triggers requests.
- **API Gateway (optional):** Routes, authenticates, and balances requests[4].
- **MCP Server:** Core logic for code analysis and diagram generation.
- **Microservices (optional):** For extensibility, separate analysis, diagramming, and storage.
- **Database Layer (optional):** For caching or storing diagram artifacts.
- **Message Broker (optional):** For asynchronous processing at scale.
- **Monitoring & Logging:** Prometheus, Grafana, ELK stack recommended[4].
- **Security Layer:** Handles authentication, authorization, and encryption.

---

## 5. Software Requirements

- **Programming Language:** Python 3.8+ (preferred for ecosystem and libraries)[2][5].
- **Frameworks/Libraries:**
  - FastMCP (for MCP server scaffolding)[3]
  - AST parsing libraries (e.g., ast, ts-morph, javalang)
  - PyYAML (for .ilograph file generation)
  - Pydantic (for data validation)[5]
  - Requests or httpx (for optional Export API calls)
  - Ilograph Export API (optional, for rendering to SVG/PNG/PDF)
- **Containerization:** Docker (with Docker Compose or Kubernetes for orchestration)[1][4].
- **Reverse Proxy:** Nginx or Traefik for HTTP/SSL termination (production)[1].
- **Monitoring:** Prometheus, Grafana (recommended)[1][4].

---

## 6. Hardware & Network Requirements

- **CPU:** Multi-core (8+ cores recommended)[1].
- **Memory:** 16–32 GB RAM[1].
- **Storage:** 100–200 GB NVMe SSD (for models, temp files, and diagrams)[1].
- **Network:** 1 Gbps interface; low latency for cloud deployments[1].
- **Cloud:** Use instances with dedicated network performance if deploying on AWS/Azure[1].

---

## 7. Security Requirements

- **Authentication:** API key or OAuth for Ilograph API and external integrations.
- **Authorization:** Role-based access if multi-user.
- **Secret Management:** Use environment variables or secret managers for all credentials[1].
- **Data Protection:** Encrypt sensitive data at rest and in transit.

---

## 8. Ilograph API Support

- **Ilograph File Format:**  
  Primary output format is native .ilograph files (YAML-based) that can be opened directly in Ilograph editor.
  - Format: YAML with resources and perspectives sections
  - Resources define architectural entities (classes, services, databases, etc.)
  - Perspectives define relationships and views (dependency, data flow, etc.)
  - Supports colors, icons, subtitles, and labels for visual customization

- **Ilograph Export API (Optional):**  
  When API key is provided, optionally render diagrams to other formats.
  - Endpoint: `https://export.ilograph.com/generate`
  - Auth: Bearer token (API key)
  - Payload: Ilograph YAML/JSON schema
  - Response: Rendered diagram file (HTML/SVG/PNG)
  - [Graceful degradation when API key not available - still generate .ilograph files]

---

## 9. Example Directory Structure

```
/ilograph-mcp-server
  /src
    analysis/
    diagram/
    mcp/
    utils/
  /tests
  Dockerfile
  requirements.txt
  README.md
  .env.example
```

---

## 10. References & Resources

- [FastMCP documentation and examples][3]
- [UML-MCP open-source server for reference implementation][2]
- [Ilograph Export API documentation]
- [AWS, Azure, and cloud provider documentation for networking and scaling][1]
- [General MCP server development guide][4]
- [Python diagrams library as a reference for diagram generation logic][5]

---

## 11. Deployment & Operations

- **CI/CD:** Use GitHub Actions or similar for automated testing and deployment.
- **Container Registry:** Store Docker images in a secure registry.
- **Monitoring:** Set up alerts for CPU, memory, and network usage.
- **Backup:** Regularly back up configuration and diagram artifacts.

---

## 12. Risks & Mitigation

- **API Rate Limiting:** Handle Ilograph API rate limits gracefully.
- **Large Codebases:** Implement incremental or selective analysis to avoid timeouts.
- **Security Breaches:** Regularly rotate keys and audit access logs.

---

## 13. Acceptance Criteria

- Server can analyze a sample codebase and generate a valid .ilograph file.
- Generated .ilograph files can be opened directly in Ilograph editor.
- AI assistants can invoke the server via MCP and receive diagram files.
- Export API integration works when API key is provided (optional).
- All security, performance, and reliability requirements are met.

---

## 14. Current Project Status & Development TODOs

### 🚧 **Phase 1: Core Implementation (In Progress)**

**✅ Completed:**
- Basic project structure with analysis modules (`src/analysis/`)
- Ilograph schema handling and YAML generation (`src/diagram/ilograph.py`)
- Multi-language analyzer support (Python, JavaScript, Java)
- Docker containerization setup
- Basic FastMCP server scaffolding

**🔄 In Progress:**
- MCP tool implementations using FastMCP decorators
- Code analyzer refinements for better entity/relationship extraction
- Ilograph perspective generation logic

---

### 🎯 **Phase 2: MCP Client Integration & Testing (Next Priority)**

**TODO: FastMCP Server Implementation**
- [ ] **Convert to FastMCP v2 patterns:** Refactor current MCP server to use `@mcp.tool()` decorators properly
- [ ] **Implement core MCP tools using FastMCP:**
  ```python
  @mcp.tool()
  def analyze_codebase(project_path: str, language: str = "auto") -> str:
      """Analyze codebase and extract architectural information"""
  
  @mcp.tool() 
  def generate_ilograph(analysis_data: str, perspective: str = "dependencies") -> str:
      """Generate .ilograph file from analysis results"""
  
  @mcp.tool()
  def render_diagram(ilograph_content: str, format: str = "svg") -> str:
      """Render diagram using Ilograph Export API (optional)"""
  ```
- [ ] **Add MCP resources for documentation:** Expose Ilograph examples and templates
- [ ] **Implement MCP prompts:** Create reusable prompts for common diagram generation scenarios

**TODO: GitHub Copilot Integration Testing**
- [ ] **Create GitHub Copilot Chat test scenarios:**
  - "Generate an Ilograph diagram for the authentication service layer"
  - "Show me the dependencies between my React components"
  - "Create a data flow diagram for my FastAPI backend"
- [ ] **Test MCP server discovery and tool invocation** via Copilot Chat
- [ ] **Validate .ilograph file generation** from Copilot conversations
- [ ] **Test error handling** when analysis fails or files are malformed

**TODO: JetBrains AI Assistant Integration**
- [ ] **Configure MCP server in JetBrains settings** (via settings.json or plugin config)
- [ ] **Test real-world user flows:**
  - Right-click on project folder → "Generate architecture diagram"
  - Ask AI Assistant: "What does the service layer architecture look like?"
  - Request specific diagrams: "Show microservice dependencies"
- [ ] **Validate IDE integration** with file output and preview

---

### 🔍 **Phase 3: User Flow Validation & Quality Improvements**

**TODO: Real-World Testing Scenarios**
- [ ] **Test with actual codebases:**
  - Large Python projects (Django, FastAPI applications)
  - React/Next.js frontend applications  
  - Java Spring Boot microservices
  - Mixed-language monorepos
- [ ] **Measure analysis performance** on codebases of different sizes
- [ ] **Validate diagram accuracy** against manually created architecture docs

**TODO: Ilograph Quality Enhancement**
- [ ] **Improve entity recognition:**
  - Better detection of service boundaries in microservices
  - API endpoint extraction from framework decorators
  - Database schema relationships from ORM models
- [ ] **Enhanced perspective generation:**
  - Service-to-service communication flows
  - Data layer dependencies (models, repositories, APIs)
  - Frontend component hierarchies
  - Authentication/authorization flows
- [ ] **Smart icon and color mapping:**
  - Framework-specific icons (Django, React, Spring Boot)
  - Semantic coloring based on layer patterns
  - Custom icon support for domain-specific entities

**TODO: Advanced Ilograph Features**
- [ ] **Multi-perspective diagrams:** Generate complementary views (logical vs. physical architecture)
- [ ] **Interactive elements:** Add clickable links and detailed subtitles
- [ ] **Hierarchical grouping:** Properly nest related components
- [ ] **Annotation support:** Include comments and documentation references

---

### 🤖 **Phase 4: AI Assistant Optimization**

**TODO: Prompt Engineering for Better Diagrams**
- [ ] **Create context-aware prompts:**
  - "Generate a microservices diagram focusing on inter-service communication"
  - "Show the data flow from frontend to database with authentication layers"
  - "Create a component diagram for the React application structure"
- [ ] **Implement intelligent defaults** based on detected frameworks and patterns
- [ ] **Add diagram validation** to ensure generated .ilograph files are semantically correct

**TODO: MCP Protocol Enhancements**
- [ ] **Implement MCP sampling:** Allow server to request LLM completions for better analysis
- [ ] **Add progress tracking** for long-running analysis operations
- [ ] **Implement cancellation support** for user-interrupted operations
- [ ] **Enhanced error reporting** with actionable suggestions

---

### 🔧 **Phase 5: Production Readiness**

**TODO: Performance & Scalability**
- [ ] **Optimize analysis performance:**
  - Implement incremental analysis for large codebases
  - Add caching for repeated analysis requests
  - Parallel processing for multi-language projects
- [ ] **Load testing** with concurrent MCP client requests
- [ ] **Memory optimization** for large codebase analysis

**TODO: Monitoring & Observability**
- [ ] **Add FastMCP middleware** for request/response logging
- [ ] **Implement health checks** compatible with MCP protocol
- [ ] **Create dashboard** for analysis metrics and success rates
- [ ] **Add alerting** for failed diagram generation

**TODO: Security & Compliance**
- [ ] **Implement secure API key handling** for Ilograph Export API
- [ ] **Add input validation** for all MCP tool parameters
- [ ] **Audit logging** for compliance requirements
- [ ] **Rate limiting** to prevent abuse

---

### 📋 **Immediate Next Steps (Priority Order)**

1. **Convert current server to FastMCP v2 patterns** with proper `@mcp.tool()` decorators
2. **Test basic MCP functionality** with a simple client (MCP Inspector)
3. **Integrate with GitHub Copilot Chat** and validate end-to-end workflow
4. **Test with JetBrains AI Assistant** in real IDE environment
5. **Iterate on diagram quality** based on user feedback
6. **Implement advanced Ilograph features** (perspectives, icons, grouping)

### 🎯 **Success Metrics**

- [ ] **Functional:** MCP tools work reliably with AI assistants
- [ ] **Quality:** Generated diagrams accurately represent codebase architecture  
- [ ] **Performance:** Analysis completes in <2 minutes for medium codebases
- [ ] **Usability:** Developers can generate useful diagrams with simple natural language requests
- [ ] **Integration:** Seamless workflow within existing IDE and AI assistant environments

---

**End of Document**

[1] https://milvus.io/ai-quick-reference/what-are-the-system-requirements-for-deploying-model-context-protocol-mcp-servers
[2] https://github.com/antoinebou12/uml-mcp
[3] https://www.nebula-graph.io/posts/Announcing_the_Open_Source_Release_of_NebulaGraph_MCP_Server
[4] https://www.rapidinnovation.io/post/building-an-mcp-server-a-step-by-step-guide-for-developers
[5] https://community.aws/content/2vPiiPiBSdRalaEax2rVDtshpf3/how-to-generate-aws-architecture-diagrams-using-amazon-q-cli-and-mcp?lang=en
[6] https://modelcontextprotocol.io/quickstart/server
[7] https://www.leanware.co/insights/how-to-build-mcp-server
[8] https://www.byteplus.com/en/blog/guide-to-mcp-servers
[9] https://www.builder.io/blog/mcp-server
[10] https://trelis.substack.com/p/how-to-build-and-publish-an-mcp-server