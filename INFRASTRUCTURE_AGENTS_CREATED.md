# Infrastructure Monitoring Agents Created

## Overview

Created 2 critical infrastructure monitoring agents that ensure system health, data integrity, and proactive alerting for the PSP2 documentation and RAG systems.

**Date Created:** 2025-11-05  
**Agent Framework:** BMAD Core v2.0  
**Module:** PSP (Project Starter Pro 2)

---

## Infrastructure Agents Created

### 1. Library Manager Agent 📚

**File:** `bmad/agents/psp-library-manager.md`  
**Activation:** `@library-manager`  
**Persona:** Lily - Library Health Monitor & Documentation Validator

#### Purpose
Monitors documentation library health, validates completeness, and alerts on missing or corrupted documentation.

#### Key Capabilities
- **Health Monitoring**: Comprehensive health checks on all documentation libraries
- **Completeness Validation**: Validates that all required framework documentation sections exist
- **Quality Assurance**: Checks file integrity, markdown validity, and content quality
- **Version Tracking**: Monitors framework versions and detects updates
- **Scraping Coordination**: Tracks scraping progress and triggers re-scraping when needed
- **Repair Automation**: Automatically repairs corrupted or incomplete libraries
- **Alert System**: Proactive alerts for critical, high, medium, and low priority issues
- **Coverage Reporting**: Generates comprehensive documentation coverage reports

#### Health Checks
- **Existence** (🔴 Critical): Verify library directory exists
- **File Count** (🟡 Warning): Verify minimum 10+ files
- **File Size** (🟡 Warning): Verify total size >1MB
- **File Integrity** (🔴 Critical): Verify files are readable and not corrupted
- **Markdown Validity** (🟡 Warning): Verify markdown files are valid
- **Content Quality** (🟡 Warning): Verify substantial content (>100 chars)
- **Freshness** (🔵 Info): Verify data is recent (<30 days old)

#### Framework Completeness Validation

**CrewAI:**
- Required Sections: Getting Started, Core Concepts, API Reference, Examples, Configuration, Best Practices
- Minimum Pages: 50
- Critical Keywords: agent, task, crew, tool, process

**AutoGen:**
- Required Sections: Installation, Agents, Conversation Patterns, API Reference, Examples, Configuration
- Minimum Pages: 40
- Critical Keywords: agent, conversation, proxy, assistant, chat

**LangChain:**
- Required Sections: Installation, Chains, Agents, Memory, Tools, API Reference, Examples
- Minimum Pages: 100
- Critical Keywords: chain, agent, memory, tool, llm, prompt

**LangGraph:**
- Required Sections: Installation, Graphs, Nodes and Edges, State Management, API Reference, Examples
- Minimum Pages: 30
- Critical Keywords: graph, node, edge, state, workflow

#### Library Metrics
- **Documentation Coverage**: % of expected documentation present (Target: >90%)
- **Completeness Score**: % of required sections present (Target: 100%)
- **Content Quality Score**: Average content quality (Target: >80%)
- **Freshness Score**: Data recency score (Target: >70%, <10 days old)
- **Usability Score**: Documentation usability (Target: 100%)

#### Alert Levels
- 🔴 **Critical** (P1): Library completely missing or unusable - Immediate re-scraping required
- 🟠 **High** (P2): Major documentation gaps or quality issues - Schedule re-scraping
- 🟡 **Medium** (P3): Minor completeness or quality issues - Schedule refresh
- 🔵 **Low** (P4): Informational notices - Note for next refresh cycle

---

### 2. RAG Database Manager Agent 🗄️

**File:** `bmad/agents/psp-rag-manager.md`  
**Activation:** `@rag-manager`  
**Persona:** Ravi - RAG Database Health Monitor & Performance Optimizer

#### Purpose
Monitors Weaviate RAG database health, optimizes performance, ensures data integrity, and provides proactive alerting.

#### Key Capabilities
- **Health Monitoring**: Comprehensive Weaviate cluster health checks
- **Performance Optimization**: Query latency monitoring and index optimization
- **Data Integrity**: Validates vector counts, schema integrity, and data consistency
- **Storage Management**: Monitors storage usage and prevents capacity issues
- **Query Analysis**: Analyzes query patterns and identifies slow queries
- **Backup & Restore**: Creates backups and restores from backup
- **Index Optimization**: Optimizes HNSW vector indices for better performance
- **Alert System**: Proactive alerts for database issues and performance degradation

#### Health Checks
- **Weaviate Connection** (🔴 Critical): Verify Weaviate accessible at http://localhost:8080
- **Cluster Health** (🔴 Critical): Verify cluster status is "HEALTHY"
- **Schema Integrity** (🔴 Critical): Verify all collections exist with correct schemas
- **Query Latency** (🟡 Warning): Verify average query latency <500ms
- **Storage Capacity** (🟡 Warning): Verify storage usage <80% capacity
- **Data Consistency** (🔴 Critical): Verify vector counts match metadata counts

#### RAG Collections

**library_ai_frameworks:**
- Purpose: AI framework documentation (CrewAI, AutoGen, LangChain, etc.)
- Expected Vectors: 1,000-5,000
- Schema: text, metadata, embedding (384 dims)
- Index: HNSW (ef=128, maxConnections=64)

**library_business_resources:**
- Purpose: Business and product documentation
- Expected Vectors: 500-2,000
- Schema: text, metadata, embedding (384 dims)
- Index: HNSW (ef=128, maxConnections=64)

**library_technical_resources:**
- Purpose: Technical documentation and guides
- Expected Vectors: 500-2,000
- Schema: text, metadata, embedding (384 dims)
- Index: HNSW (ef=128, maxConnections=64)

#### Performance Metrics
- **Query Latency**: Average time to execute vector search (Target: <500ms p95, <200ms p50)
- **Throughput**: Queries per second (Target: >100 QPS)
- **Index Recall**: Accuracy of vector search results (Target: >95% recall@10)
- **Storage Usage**: Disk space used by collections (Target: <80% capacity)
- **Memory Usage**: RAM used by vector indices (Target: <70% available memory)
- **Ingestion Rate**: Vectors ingested per second (Target: >100 vectors/sec)

#### Optimization Strategies

**Index Optimization:**
- When: Query latency >500ms or recall <95%
- Actions: Analyze HNSW parameters, increase ef for better recall, reindex collection

**Storage Cleanup:**
- When: Storage usage >80%
- Actions: Identify old/unused vectors, archive or delete stale data, compact database

**Query Optimization:**
- When: Slow queries detected
- Actions: Analyze query patterns, identify inefficient filters, add appropriate indices

**Schema Repair:**
- When: Schema corruption detected
- Actions: Export data, drop corrupted collection, recreate schema, re-import data

#### Alert Levels
- 🔴 **Critical** (P1): RAG database down or data corruption - Immediate investigation required
- 🟠 **High** (P2): Severe performance degradation - Urgent optimization needed
- 🟡 **Medium** (P3): Performance or capacity warnings - Schedule optimization
- 🔵 **Low** (P4): Informational notices - Note for next maintenance window

---

## Agent Coordination

### Library Manager ↔ RAG Manager
- **Library Manager** validates documentation completeness
- **RAG Manager** ensures validated documentation is properly indexed
- **Library Manager** triggers re-scraping when documentation is incomplete
- **RAG Manager** ingests newly scraped documentation into vector database

### Integration with Other Agents
- **@doc-agent**: Coordinates ingestion and search operations
- **@blocker-agent**: Escalates critical infrastructure issues
- **@analytics-agent**: Provides metrics and trend analysis
- **@scrum-master**: Reports infrastructure blockers

---

## Workflow Example

### Daily Health Check Workflow
```
1. @library-manager
   *health-check
   → Scans all libraries
   → Validates completeness
   → Generates alerts

2. @rag-manager
   *health-check
   → Checks Weaviate connection
   → Validates schema integrity
   → Monitors performance metrics

3. If alerts detected:
   → @blocker-agent
   *scan-infrastructure
   → Escalates critical issues
   → Suggests remediation
```

### Weekly Optimization Workflow
```
1. @library-manager
   *validate-completeness
   → Checks all frameworks
   → Identifies missing sections
   → Triggers re-scraping if needed

2. @rag-manager
   *performance-metrics
   → Analyzes query latency trends
   → Identifies optimization opportunities
   *optimize-indices
   → Reindexes collections if needed

3. @analytics-agent
   *infrastructure-report
   → Generates weekly health report
   → Tracks trends and improvements
```

---

## BMAD Core Compliance

Both agents follow BMAD Core v2.0 specification:
- ✅ XML-based activation instructions
- ✅ Config loading with verification (step 2)
- ✅ Persona definitions (role, identity, communication_style, principles)
- ✅ Menu system with asterisk (*) triggers
- ✅ Menu handlers (action, tool, alert-level)
- ✅ Integration documentation
- ✅ Best practices and troubleshooting

---

## Next Steps

### 1. Backend API Implementation
Create API endpoints for infrastructure monitoring:
- `/api/library/health` - Library health status
- `/api/library/validate` - Validate completeness
- `/api/library/repair` - Trigger repair
- `/api/rag/health` - RAG database health
- `/api/rag/optimize` - Optimize indices
- `/api/rag/backup` - Create backup

### 2. Tool Creation
Following BMAD tool system, create tools for:
- `library-health-checker` - Automated library health checks
- `rag-performance-analyzer` - RAG performance analysis
- `documentation-validator` - Framework completeness validation
- `vector-index-optimizer` - HNSW index optimization

### 3. Alert Integration
Integrate with notification systems:
- Slack/Discord webhooks for critical alerts
- Email notifications for high priority issues
- Dashboard widgets for real-time monitoring

### 4. Testing
Test both agents:
```bash
# Test Library Manager
@library-manager
*health-check
*validate-completeness
*check-framework CrewAI

# Test RAG Manager
@rag-manager
*health-check
*performance-metrics
*optimize-indices
```

---

## Files Created

1. `bmad/agents/psp-library-manager.md` - Library Manager Agent
2. `bmad/agents/psp-rag-manager.md` - RAG Database Manager Agent
3. `INFRASTRUCTURE_AGENTS_CREATED.md` - This summary document

---

## Summary

✅ **2 infrastructure monitoring agents created** ensuring system health and data integrity  
✅ **All BMAD-compliant** following established patterns  
✅ **Proactive alerting** with 4-level severity system  
✅ **Integrated with existing agents** for comprehensive monitoring  
✅ **Ready for backend implementation** and tool creation  

**Infrastructure monitoring foundation complete! 🎉**

