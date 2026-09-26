# DNS Security - Demo Guide

## ⏱️ 5-Minute Pitch Narrative

### 1. Introduction (0:00 - 0:45)
**"Good morning judges, we are team [Team Name]."**
"Today, virtually every cyberattack, from ransomware to data exfiltration, relies on DNS at some stage. Traditional DNS firewalls rely on static blocklists. By the time a malicious domain is added to a list, the damage is already done. We are presenting our Smart DNS Filtering Service—a proactive security solution that combines real-time Threat Intelligence with AI/ML to stop zero-day threats and DNS tunneling before they reach your network."

### 2. The Problem & Our Solution (0:45 - 1:30)
"The problem with static lists is that attackers use Domain Generation Algorithms (DGAs) and DNS tunneling to bypass them effortlessly. 
Our solution intercepts DNS queries at the edge. We use an asynchronous, highly-concurrent architecture. If a domain isn't explicitly blocked by our dynamic Threat Intel feeds, it is passed to our lightweight Machine Learning pipeline. The ML model evaluates lexical features—like Shannon entropy and character distribution—in under 5 milliseconds to detect DGAs and tunneling attempts on the fly."

### 3. Demo Introduction (1:30 - 2:00)
"Let us show you how this works in real time. On the left side of our screen, you see our live React dashboard, which receives WebSocket updates instantly. On the right, we will simulate network traffic."

---

## 💻 Live Demo Execution Steps (2:00 - 4:00)

### Step 1: Start Normal & Malicious Mixed Traffic
*Terminal 1:*
```bash
python scripts/demo_traffic_generator.py --target 127.0.0.1 --port 53 --interval 0.5
```
**Talking Point:** "Here we are generating typical network traffic. You can see benign domains like `google.com` resolving normally. However, when known malicious domains like `malware-test.xyz` are queried, our DNS engine instantly sinkholes them, returning a safe internal IP. You can see these blocks appearing live on our dashboard's real-time chart."

### Step 2: Show The ML Analyzer
*Browser:* Navigate to the "Domain Analysis" tab on the dashboard.
**Talking Point:** "What if an attacker registers a brand new domain today? Let's paste a DGA-looking domain like `x8f93j2k1l0zxm.biz`. Our ML engine extracts features like length and entropy, calculates a risk score, and flags it as malicious—without it ever being on a blocklist."

### Step 3: Simulate a Live DNS Tunneling Attack
*Terminal 2:*
```bash
python scripts/demo_tunnel_attack.py --target 127.0.0.1 --port 53 --count 50
```
**Talking Point:** "Now for the critical test. An attacker has compromised a host and is trying to exfiltrate sensitive data via DNS tunneling using high-entropy subdomains. We launch the attack script. Watch the dashboard!"
*Visual Highlight:* Point to the WebSocket alarms flashing red on the UI.
"Our engine detects the sudden spike in entropy and frequency, instantly cutting off the query stream and alerting the SOC analysts via WebSocket."

---

## 🎯 Conclusion & Future Scope (4:00 - 5:00)
"Our system is built using modern async Python (FastAPI/asyncio) making it highly scalable and capable of handling thousands of requests per second with minimal latency. 
**Future Scope:** We plan to integrate with Active Directory for user-level policies and add eBPF support for kernel-level DNS interception.
Thank you! We are open to questions."
