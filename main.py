from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import os
import json
import re
from dotenv import load_dotenv

load_dotenv() #Reads your .env file and loads GROQ_API_KEY into
# memory so os.environ can access it. Without this line your API key would not be found.



app = FastAPI(title="Network Log Analyzer") #Creates your FastAPI application.
# The title is just a label that appears in the auto-generated docs at /docs

class NetworkLog(BaseModel):  #This defines exactly what JSON the API expects to receive
    src_ip: str
    dst_ip: str
    dst_port: int
    protocol: str
    bytes: int
    duration: int
    country: str
    domain: str

def analyze_log_with_groq(log: NetworkLog) -> dict: #networklog is defined above
    client = Groq(api_key=os.environ["GROQ_API_KEY"]) # reads from the env file

    prompt = f"""
You are a cybersecurity analyst. Analyze this network log and determine
if the connection is MALICIOUS or LEGITIMATE.

Network Log:
- Source IP: {log.src_ip}
- Destination IP: {log.dst_ip}
- Destination Port: {log.dst_port}
- Protocol: {log.protocol}
- Bytes Transferred: {log.bytes}
- Duration (seconds): {log.duration}
- Country: {log.country}
- Domain: {log.domain}

Key things to check:
1. Port 4444 is a well-known malware/backdoor port (Metasploit default)
2. Suspicious domain names (e.g. evil-command.xyz)
3. Connections to high-risk countries with unusual ports
4. Short duration with moderate bytes can indicate C2 beaconing

Respond ONLY in this exact JSON format with no extra text:
{{
    "verdict": "MALICIOUS or LEGITIMATE",
    "confidence": "HIGH or MEDIUM or LOW",
    "reason": "One clear sentence explaining why",
    "indicators": ["list", "of", "suspicious", "indicators"]
}}
"""
    #sends the prompt to the AI and waits for a reply.
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content #The AI replied now we extract the actual text from the response.
    json_match = re.search(r'\{.*\}', text, re.DOTALL) #JSON is just organized text that both humans and computers can read easily.
    if json_match:#The AI sometimes replies with extra text we don't need. This code finds just the { } part,
        # grabs it, and if it can't find it, it throws an error.
        return json.loads(json_match.group())
    raise ValueError(f"Could not parse response: {text}")

@app.post("/analyze") # receives the log, sends it to the AI, and returns the result back to you.
# If something goes wrong it returns an error instead of crashing.
async def analyze_log(log: NetworkLog):
    try:
        result = analyze_log_with_groq(log)
        return {
            "status": "success",
            "input": log.dict(),
            "analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health") #The second part just checks that the server is still running.
async def health():
    return {"status": "healthy"}