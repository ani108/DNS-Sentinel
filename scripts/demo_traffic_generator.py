import argparse
import time
import random
import socket
import dns.message
import dns.query
import string

BENIGN_DOMAINS = [
    "google.com", "github.com", "wikipedia.org", "amazon.in",
    "microsoft.com", "apple.com", "youtube.com", "linkedin.com"
]

MALICIOUS_DOMAINS = [
    "malware-test.xyz", "paypal-verify-login.tk", "a89f72bxcv.buzz",
    "secure-update-windows.com", "free-crypto-giveaway.info"
]

def generate_tunnel_domain(base_domain="tunnel.attacker.com"):
    # Generate a random high-entropy subdomain
    length = random.randint(15, 30)
    subdomain = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{subdomain}.{base_domain}"

def send_query(domain, target, port):
    try:
        q = dns.message.make_query(domain, dns.rdatatype.A)
        response = dns.query.udp(q, target, port=port, timeout=2.0)
        print(f"[+] Queried: {domain:<35} | Status: {dns.rcode.to_text(response.rcode())}")
    except Exception as e:
        print(f"[-] Failed to query {domain}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Demo Traffic Generator for SIH DNS Security")
    parser.add_argument("--target", type=str, default="127.0.0.1", help="Target DNS server IP")
    parser.add_argument("--port", type=int, default=53, help="Target DNS server port")
    parser.add_argument("--interval", type=float, default=0.5, help="Interval between queries (seconds)")
    args = parser.parse_args()

    print(f"Starting Traffic Generator -> {args.target}:{args.port}")
    print("Press Ctrl+C to stop.")

    counter = 0
    try:
        while True:
            counter += 1
            
            # 70% benign, 20% malicious, 10% tunneling burst
            chance = random.random()
            
            if chance < 0.7:
                # Benign
                domain = random.choice(BENIGN_DOMAINS)
                send_query(domain, args.target, args.port)
            elif chance < 0.9:
                # Malicious / DGA
                domain = random.choice(MALICIOUS_DOMAINS)
                send_query(domain, args.target, args.port)
            else:
                # Tunneling Burst
                print("\n[!] Initiating DNS Tunneling Burst...")
                for _ in range(random.randint(10, 30)):
                    domain = generate_tunnel_domain()
                    send_query(domain, args.target, args.port)
                    time.sleep(0.05)
                print("[!] Tunneling Burst Complete.\n")
            
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\nTraffic Generator stopped.")

if __name__ == "__main__":
    main()
