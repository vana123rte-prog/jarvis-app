from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import requests

app = FastAPI()

SYSTEM_PROMPT = """Ты — Джарвис, продвинутый AI-ассистент и эксперт по программированию.
Отвечай ИСКЛЮЧИТЕЛЬНО на русском языке, без иероглифов.

ПРАВИЛА ПО КОДУ:
- Если пользователь просит код — давай ПОЛНЫЙ, РАБОЧИЙ код, без заглушек и "...".
- Всегда указывай язык программирования после ``` в начале блока.
- Код должен быть готов к запуску: с импортами, обработкой ошибок, комментариями где нужно.
- После кода кратко объясни, что он делает.

ПРАВИЛА ПО ОТВЕТАМ:
- Отвечай структурно: заголовки, списки, выделения.
- Будь конкретным, не лей воду.
- Обращайся на «ты».
- Отказывай только если просьба реально нарушает закон."""

def needs_search(text):
    keywords = ['найди', 'поищи', 'погугли', 'новости', 'последние',
                'сегодня', 'вчера', 'сейчас', 'курс', 'цена', 'погода',
                'что такое', 'кто такой', 'где', 'когда', 'сколько стоит']
    t = text.lower()
    return any(k in t for k in keywords)

def web_search(query, max_results=5):
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return None
        return "\n".join(f"- {r.get('title','')}: {r.get('body','')}" for r in results)
    except Exception:
        return None

class Msg(BaseModel):
    text: str

HTML = """<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<title>Джарвис</title>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<meta name="theme-color" content="#0a0e17">
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;padding:0;height:100%;overflow:hidden}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
background:#0a0e17;color:#e6edf3;display:flex;flex-direction:column}
header{padding:12px 16px;background:#0d1117;border-bottom:1px solid #21262d;
display:flex;align-items:center;gap:12px;flex-shrink:0}
.avatar{width:42px;height:42px;border-radius:50%;
background:linear-gradient(135deg,#1f6feb,#58a6ff);
display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;
box-shadow:0 0 20px rgba(88,166,255,0.3)}
header h1{font-size:17px;margin:0;font-weight:600}
header .status{font-size:12px;color:#3fb950;display:flex;align-items:center;gap:4px}
.dot{width:6px;height:6px;background:#3fb950;border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
#newbtn{margin-left:auto;background:transparent;border:1px solid #30363d;
color:#8b949e;padding:6px 12px;border-radius:8px;font-size:13px;cursor:pointer}
#newbtn:hover{border-color:#1f6feb;color:#58a6ff}
#log{flex:1;overflow-y:auto;padding:18px 14px;display:flex;flex-direction:column;gap:18px}
#log::-webkit-scrollbar{width:4px}
#log::-webkit-scrollbar-thumb{background:#30363d;border-radius:2px}
.row{display:flex;gap:10px;max-width:92%;animation:fade 0.3s ease}
.row.user{align-self:flex-end;flex-direction:row-reverse}
.row.ai{align-self:flex-start}
@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.mini-avatar{width:32px;height:32px;border-radius:50%;flex-shrink:0;
display:flex;align-items:center;justify-content:center;font-size:16px;
box-shadow:0 2px 8px rgba(0,0,0,0.3)}
.user .mini-avatar{background:#1f6feb}
.ai .mini-avatar{background:linear-gradient(135deg,#1f6feb,#58a6ff)}
.bubble{padding:12px 16px;border-radius:18px;font-size:15px;
line-height:1.6;white-space:normal;word-wrap:break-word;overflow-wrap:anywhere;
min-width:0;max-width:100%}
.user .bubble{background:linear-gradient(135deg,#1f6feb,#388bfd);
color:#fff;border-bottom-right-radius:4px;white-space:pre-wrap}
.ai .bubble{background:#161b22;border:1px solid #21262d;
border-bottom-left-radius:4px}
.bubble b{color:#58a6ff}
.bubble code{background:#0d1117;padding:2px 6px;border-radius:4px;
font-family:monospace;font-size:13px;color:#79c0ff}
.code-block{position:relative;margin:12px 0;background:#0d1117;
border:1px solid #21262d;border-radius:10px;overflow:hidden}
.code-head{display:flex;align-items:center;justify-content:space-between;
padding:8px 12px;background:#161b22;border-bottom:1px solid #21262d;
font-size:12px;color:#8b949e;font-family:monospace}
.copy-btn{background:#21262d;border:1px solid #30363d;color:#8b949e;
padding:4px 10px;border-radius:6px;font-size:11px;cursor:pointer;
font-family:-apple-system,sans-serif;transition:all 0.2s}
.copy-btn:active{background:#1f6feb;color:#fff;border-color:#1f6feb}
.copy-btn.copied{background:#238636;color:#fff;border-color:#238636}
.code-block pre{margin:0;padding:14px;overflow-x:auto;font-size:13px;
line-height:1.55;font-family:'SF Mono',Consolas,monospace;color:#e6edf3}
.code-block pre code{background:transparent;padding:0;color:inherit;font-size:inherit}
.typing{display:flex;gap:4px;padding:14px 18px}
.typing span{width:7px;height:7px;background:#58a6ff;border-radius:50%;
animation:blink 1.4s infinite}
.typing span:nth-child(2){animation-delay:.2s}
.typing span:nth-child(3){animation-delay:.4s}
@keyframes blink{0%,60%,100%{opacity:.3;transform:scale(0.85)}
30%{opacity:1;transform:scale(1)}}
footer{padding:12px 16px 20px;background:#0d1117;border-top:1px solid #21262d;flex-shrink:0}
.input-wrap{display:flex;gap:8px;background:#161b22;border:1px solid #30363d;
border-radius:24px;padding:6px 6px 6px 18px;align-items:center;transition:border-color .2s}
.input-wrap:focus-within{border-color:#1f6feb}
#q{flex:1;background:transparent;border:none;outline:none;color:#e6edf3;
font-size:15px;padding:10px 0}
#q::placeholder{color:#6e7681}
#send{width:38px;height:38px;border-radius:50%;border:none;flex-shrink:0;
background:linear-gradient(135deg,#1f6feb,#58a6ff);color:#fff;font-size:16px;
cursor:pointer;display:flex;align-items:center;justify-content:center;transition:opacity .2s}
#send:disabled{opacity:.4}
</style></head><body>
<header>
  <div class="avatar">🤖</div>
  <div>
    <h1>Джарвис</h1>
    <div class="status"><span class="dot"></span> онлайн</div>
  </div>
  <button id="newbtn">Новый чат</button>
</header>
<div id="log"></div>
<footer>
  <div class="input-wrap">
    <input id="q" placeholder="Сообщение..." autocomplete="off">
    <button id="send">➤</button>
  </div>
</footer>
<script>
const log=document.getElementById('log'),q=document.getElementById('q'),
send=document.getElementById('send'),newbtn=document.getElementById('newbtn');

function escapeHtml(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}

function renderMd(text){
 let s=escapeHtml(text);
 // Блоки кода с языком
 s=s.replace(/```(\\w*)\\n?([\\s\\S]*?)```/g,function(m,lang,code){
   const l=lang||'code';
   const id='cb'+Math.random().toString(36).slice(2,9);
   return '<div class="code-block" id="'+id+'">'+
     '<div class="code-head"><span>'+l+'</span>'+
     '<button class="copy-btn" onclick="copyCode(this)">Копировать</button></div>'+
     '<pre><code>'+code.trim()+'</code></pre></div>';
 });
 // Инлайн-код
 s=s.replace(/`([^`\\n]+)`/g,'<code>$1</code>');
 // Жирный
 s=s.replace(/\\*\\*([^*]+)\\*\\*/g,'<b>$1</b>');
 return s;
}

window.copyCode=function(btn){
 const pre=btn.closest('.code-block').querySelector('pre code');
 const txt=pre.innerText;
 const done=()=>{
   btn.textContent='✓ Скопировано';
   btn.classList.add('copied');
   setTimeout(()=>{btn.textContent='Копировать';btn.classList.remove('copied');},1500);
 };
 if(navigator.clipboard&&navigator.clipboard.writeText){
   navigator.clipboard.writeText(txt).then(done).catch(()=>{
     const ta=document.createElement('textarea');ta.value=txt;
     document.body.appendChild(ta);ta.select();
     document.execCommand('copy');ta.remove();done();
   });
 }else{
   const ta=document.createElement('textarea');ta.value=txt;
   document.body.appendChild(ta);ta.select();
   document.execCommand('copy');ta.remove();done();
 }
};

function addRow(cls,text){
 const row=document.createElement('div');
 row.className='row '+cls;
 const av=document.createElement('div');
 av.className='mini-avatar';
 av.textContent=cls==='user'?'👤':'🤖';
 const bubble=document.createElement('div');
 bubble.className='bubble';
 if(cls==='ai'){bubble.innerHTML=renderMd(text);}
 else{bubble.textContent=text;}
 row.appendChild(av);row.appendChild(bubble);
 log.appendChild(row);
 log.scrollTop=log.scrollHeight;
 return bubble;
}

async function submit(){
 const t=q.value.trim();if(!t)return;
 q.value='';send.disabled=true;
 addRow('user',t);
 const b=addRow('ai','');
 b.innerHTML='<div class="typing"><span></span><span></span><span></span></div>';
 try{
  const r=await fetch('/ask',{method:'POST',
   headers:{'Content-Type':'application/json'},
   body:JSON.stringify({text:t})});
  const d=await r.json();
  b.innerHTML=renderMd(d.reply||'Ошибка');
 }catch(e){b.textContent='Ошибка связи';}
 send.disabled=false;q.focus();
}

send.onclick=submit;
q.addEventListener('keydown',e=>{if(e.key==='Enter')submit();});
newbtn.onclick=()=>{log.innerHTML='';q.focus();};
q.focus();
</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.post("/ask")
def ask(m: Msg):
    try:
        now = datetime.now(timezone.utc) + timedelta(hours=3)
        now_str = now.strftime("%d.%m.%Y %H:%M")

        context = f"Текущее время (Минск, UTC+3): {now_str}, год 2026.\n"

        if needs_search(m.text):
            search_data = web_search(m.text)
            if search_data:
                context += f"\nНайденная информация из интернета:\n{search_data}\n"

        full_prompt = (
            f"{context}\n"
            f"Вопрос: {m.text}\n\n"
            f"Ответь на русском языке, структурировано, по делу. "
            f"Если нужен код — дай полный рабочий код в блоке ```язык```."
        )

        r = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "qwen2.5:1.5b",
                "prompt": full_prompt,
                "system": SYSTEM_PROMPT,
                "stream": False,
                "options": {"temperature": 0.6, "num_predict": 1024}
            },
            timeout=300
        )
        return {"reply": r.json().get("response", "Ошибка")}
    except Exception as e:
        return {"reply": f"Ошибка: {e}"}
