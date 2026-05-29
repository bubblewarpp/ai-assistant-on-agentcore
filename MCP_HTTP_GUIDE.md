# MCP HTTP/HTTPS Server Configuration Guide

## 📡 MCP Transport Types

MCP (Model Context Protocol) mendukung 2 jenis transport:

### 1. **STDIO** (Default - JSON via stdin/stdout)
```json
{
  "command": "uvx",
  "args": ["mcp-server-name"]
}
```

### 2. **HTTP/HTTPS** (REST API)
```json
{
  "transport": "http",
  "url": "http://localhost:3000/mcp"
}
```

---

## 🔧 HTTP/HTTPS Configuration

### Basic HTTP Server

```json
{
  "mcpServers": {
    "my-http-server": {
      "transport": "http",
      "url": "http://localhost:3000/mcp",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### HTTPS Server with Authentication

```json
{
  "mcpServers": {
    "my-secure-server": {
      "transport": "https",
      "url": "https://api.example.com/mcp",
      "disabled": false,
      "autoApprove": [],
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY",
        "X-Custom-Header": "custom-value"
      }
    }
  }
}
```

### With API Key

```json
{
  "mcpServers": {
    "api-server": {
      "transport": "https",
      "url": "https://api.example.com/v1/mcp",
      "disabled": false,
      "autoApprove": ["tool1", "tool2"],
      "headers": {
        "X-API-Key": "your-api-key-here",
        "Content-Type": "application/json"
      }
    }
  }
}
```

---

## 🌐 Example: Humanizer API

### Local Development

```json
{
  "mcpServers": {
    "humanizer-local": {
      "transport": "http",
      "url": "http://localhost:3000/mcp",
      "disabled": false,
      "autoApprove": ["humanize_text"],
      "headers": {
        "Content-Type": "application/json"
      }
    }
  }
}
```

### Production

```json
{
  "mcpServers": {
    "humanizer-prod": {
      "transport": "https",
      "url": "https://humanizer-api.yourdomain.com/mcp",
      "disabled": false,
      "autoApprove": [],
      "headers": {
        "Authorization": "Bearer prod_api_key_12345",
        "X-Environment": "production"
      }
    }
  }
}
```

---

## 🔐 Authentication Methods

### 1. Bearer Token

```json
{
  "headers": {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 2. API Key

```json
{
  "headers": {
    "X-API-Key": "sk-1234567890abcdef",
    "X-API-Secret": "secret-key-here"
  }
}
```

### 3. Basic Auth

```json
{
  "headers": {
    "Authorization": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="
  }
}
```

### 4. Custom Headers

```json
{
  "headers": {
    "X-Custom-Auth": "custom-token",
    "X-User-ID": "user-123",
    "X-Tenant-ID": "tenant-456"
  }
}
```

---

## 🚀 Common Use Cases

### 1. Internal API

```json
{
  "mcpServers": {
    "internal-api": {
      "transport": "http",
      "url": "http://internal-api.company.local:8080/mcp",
      "disabled": false,
      "autoApprove": [],
      "headers": {
        "X-Internal-Token": "internal-secret"
      }
    }
  }
}
```

### 2. Third-Party Service

```json
{
  "mcpServers": {
    "openai-mcp": {
      "transport": "https",
      "url": "https://api.openai.com/v1/mcp",
      "disabled": false,
      "autoApprove": [],
      "headers": {
        "Authorization": "Bearer sk-...",
        "OpenAI-Organization": "org-..."
      }
    }
  }
}
```

### 3. Microservice

```json
{
  "mcpServers": {
    "data-service": {
      "transport": "https",
      "url": "https://data-service.k8s.cluster/api/mcp",
      "disabled": false,
      "autoApprove": ["get_data", "search_data"],
      "headers": {
        "X-Service-Token": "service-token-123",
        "X-Namespace": "production"
      }
    }
  }
}
```

---

## 📝 Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transport` | string | Yes | "http" or "https" |
| `url` | string | Yes | Full URL to MCP endpoint |
| `disabled` | boolean | No | Enable/disable server (default: false) |
| `autoApprove` | array | No | List of tool names to auto-approve |
| `headers` | object | No | Custom HTTP headers |

---

## 🔍 Debugging

### Enable Logging

Set environment variable:
```bash
export MCP_DEBUG=1
```

### Check Connection

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### Test with Headers

```bash
curl -X POST https://api.example.com/mcp \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

---

## ⚠️ Common Issues

### 1. Connection Refused

**Problem:** `ECONNREFUSED`

**Solution:**
- Check if server is running
- Verify URL and port
- Check firewall rules

### 2. Unauthorized

**Problem:** `401 Unauthorized`

**Solution:**
- Verify API key/token
- Check header format
- Ensure token is not expired

### 3. CORS Error

**Problem:** CORS policy blocking request

**Solution:**
- Configure CORS on server
- Add appropriate headers
- Use proxy if needed

### 4. SSL Certificate Error

**Problem:** `UNABLE_TO_VERIFY_LEAF_SIGNATURE`

**Solution:**
- Use valid SSL certificate
- Add CA certificate if self-signed
- Use `http` for local development

---

## 🏗️ Building Your Own MCP HTTP Server

### Node.js Example

```javascript
const express = require('express');
const app = express();

app.use(express.json());

// MCP endpoint
app.post('/mcp', (req, res) => {
  const { method, params } = req.body;
  
  // Handle MCP methods
  switch(method) {
    case 'tools/list':
      res.json({
        jsonrpc: '2.0',
        result: {
          tools: [
            {
              name: 'humanize_text',
              description: 'Humanize AI-generated text',
              inputSchema: {
                type: 'object',
                properties: {
                  text: { type: 'string' }
                }
              }
            }
          ]
        },
        id: req.body.id
      });
      break;
      
    case 'tools/call':
      // Handle tool execution
      res.json({
        jsonrpc: '2.0',
        result: {
          content: [
            {
              type: 'text',
              text: 'Humanized text result'
            }
          ]
        },
        id: req.body.id
      });
      break;
      
    default:
      res.status(400).json({
        jsonrpc: '2.0',
        error: {
          code: -32601,
          message: 'Method not found'
        },
        id: req.body.id
      });
  }
});

app.listen(3000, () => {
  console.log('MCP server running on http://localhost:3000');
});
```

### Python FastAPI Example

```python
from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI()

class MCPRequest(BaseModel):
    jsonrpc: str
    method: str
    params: dict = {}
    id: int

@app.post("/mcp")
async def mcp_endpoint(
    request: MCPRequest,
    authorization: str = Header(None)
):
    # Verify authorization
    if authorization != "Bearer YOUR_TOKEN":
        return {"error": "Unauthorized"}
    
    if request.method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": [
                    {
                        "name": "humanize_text",
                        "description": "Humanize text",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"}
                            }
                        }
                    }
                ]
            },
            "id": request.id
        }
    
    return {"error": "Method not found"}
```

---

## 📚 MCP Protocol Reference

### Required Methods

1. **tools/list** - List available tools
2. **tools/call** - Execute a tool
3. **resources/list** - List available resources (optional)
4. **prompts/list** - List available prompts (optional)

### Request Format

```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": 1
}
```

### Response Format

```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [...]
  },
  "id": 1
}
```

---

## 🎯 Best Practices

1. **Use HTTPS in production** - Always encrypt traffic
2. **Implement authentication** - Protect your endpoints
3. **Rate limiting** - Prevent abuse
4. **Error handling** - Return proper error codes
5. **Logging** - Track requests and errors
6. **Timeouts** - Set reasonable timeouts
7. **Validation** - Validate all inputs
8. **Documentation** - Document your API

---

## 🔗 Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP SDK](https://github.com/modelcontextprotocol/sdk)
- [Example Servers](https://github.com/modelcontextprotocol/servers)

---

## 📋 Current Configuration

Your workspace MCP config is at:
```
.kiro/settings/mcp.json
```

User-level MCP config is at:
```
~/.kiro/settings/mcp.json
```

**Priority:** Workspace config overrides user config.

---

## 🚀 Next Steps

1. **Start your MCP server** (if using HTTP)
2. **Update URL and headers** in mcp.json
3. **Enable the server** (set `disabled: false`)
4. **Restart Kiro** or reconnect MCP servers
5. **Test the connection** in Kiro

---

**Happy MCP-ing!** 🎉
