# 🌐 Phoenix AI HTTP API

This API exposes the Phoenix AI SDK as a RESTful service, allowing integration with any framework or language (Flutter, .NET, Node.js, C++, Rust, etc.).

## 🚀 Running the Server

```bash
# Install requirements
pip install fastapi uvicorn python-multipart

# Start the server
python api/main.py
```

The API will be available at `http://localhost:8000`.

---

## 🛠️ Endpoints

### 1. ChatBot Endpoint (`/chat`)
**POST** `multipart/form-data`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Yes | The message to the bot. |
| `session_id` | string | No | Conversation session ID. |
| `image` | file | No | Optional image for vision tasks. |

#### **Node.js (Axios) Example**
```javascript
const axios = require('axios');
const FormData = require('form-data');

const data = new FormData();
data.append('text', 'What is the secret code?');
data.append('session_id', 'user_99');

axios.post('http://localhost:8000/chat', data, {
    headers: data.getHeaders()
}).then(res => console.log(res.data.response));
```

#### **Flutter (http) Example**
```dart
var request = http.MultipartRequest('POST', Uri.parse('http://localhost:8000/chat'));
request.fields['text'] = 'Hello Bot!';
request.fields['session_id'] = 'flutter_dev';

var response = await request.send();
var responseData = await response.stream.bytesToString();
print(json.decode(responseData)['response']);
```

---

### 2. Autonomous Agent Endpoint (`/agent`)
**POST** `application/json`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `prompt` | string | (Required) | The task for the agent. |
| `mode` | string | `auto` | `auto`, `plan`, or `fast_ans`. |
| `session_id` | string | `default` | Session for tracking. |

#### **C# (.NET) Example**
```csharp
using var client = new HttpClient();
var request = new { 
    prompt = "Create a summary of the project.", 
    mode = "plan" 
};
var response = await client.PostAsJsonAsync("http://localhost:8000/agent", request);
var data = await response.Content.ReadFromJsonAsync<dynamic>();
Console.WriteLine(data.result);
```

#### **Rust (reqwest) Example**
```rust
let client = reqwest::Client::new();
let res = client.post("http://localhost:8000/agent")
    .json(&serde_json::json!({
        "prompt": "Explain the architecture",
        "mode": "fast_ans"
    }))
    .send()
    .await?;
```

---

## 🏥 Health Check
**GET** `/health`

Returns the system status and version.
