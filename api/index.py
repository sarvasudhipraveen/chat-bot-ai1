import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI Chatbot</title>
  <style>
    body { font-family: Arial, sans-serif; background:#f4f6fb; margin:0; }
    .box { max-width: 850px; margin: 35px auto; background:white; border-radius:16px; padding:24px; box-shadow:0 8px 25px rgba(0,0,0,.08); }
    h1 { margin-top:0; color:#222; }
    #chat { min-height:400px; border:1px solid #ddd; border-radius:12px; padding:16px; overflow-y:auto; background:#fafafa; }
    .msg { margin:10px 0; padding:10px 12px; border-radius:10px; line-height:1.5; white-space:pre-wrap; }
    .user { background:#dbeafe; margin-left:20%; }
    .bot { background:#e5e7eb; margin-right:20%; }
    .row { display:flex; gap:10px; margin-top:15px; }
    input { flex:1; padding:14px; border:1px solid #ccc; border-radius:10px; font-size:16px; }
    button { padding:14px 20px; border:0; border-radius:10px; background:#2563eb; color:white; font-size:16px; cursor:pointer; }
    button:disabled { background:#999; }
    .note { color:#666; font-size:14px; }
  </style>
</head>
<body>
  <div class="box">
    <h1>🤖 AI Chatbot</h1>
    <p class="note">Deployed on Vercel using Groq API.</p>
    <div id="chat"></div>
    <div class="row">
      <input id="message" placeholder="Ask anything..." onkeydown="if(event.key==='Enter') sendMessage()" />
      <button id="btn" onclick="sendMessage()">Send</button>
    </div>
  </div>
<script>
const chat = document.getElementById('chat');
const input = document.getElementById('message');
const btn = document.getElementById('btn');
let messages = [];
function addMessage(role, text) {
  const div = document.createElement('div');
  div.className = 'msg ' + (role === 'user' ? 'user' : 'bot');
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}
async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  btn.disabled = true;
  addMessage('user', text);
  messages.push({role: 'user', content: text});
  const thinkingNode = addMessage('assistant', 'Thinking...');
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({messages})
    });
    const raw = await res.text();
    let data;
    try { data = JSON.parse(raw); }
    catch(e) { throw new Error('Server returned HTML/text instead of JSON. Check Vercel Function logs.'); }
    if (!res.ok) throw new Error(data.error || 'Request failed');
    thinkingNode.textContent = data.reply;
    messages.push({role: 'assistant', content: data.reply});
  } catch (err) {
    thinkingNode.textContent = 'Error: ' + err.message;
  }
  btn.disabled = false;
  input.focus();
}
</script>
</body>
</html>
"""

@app.get('/')
def home():
    return render_template_string(HTML)

@app.post('/api/chat')
def chat_api():
    try:
        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            return jsonify({'error': 'GROQ_API_KEY missing in Vercel Environment Variables'}), 500
        data = request.get_json(silent=True) or {}
        messages = data.get('messages') or []
        if not messages:
            return jsonify({'error': 'Message is required'}), 400
        safe_messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
        for m in messages[-12:]:
            role = m.get('role')
            content = m.get('content')
            if role in ('user', 'assistant') and content:
                safe_messages.append({'role': role, 'content': content})
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=os.environ.get('GROQ_MODEL', 'llama-3.1-8b-instant'),
            messages=safe_messages,
            temperature=0.7,
        )
        return jsonify({'reply': completion.choices[0].message.content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.get('/api/health')
def health():
    return jsonify({'ok': True})
