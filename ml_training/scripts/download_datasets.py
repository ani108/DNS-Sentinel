import pandas as pd
import requests
import io
import os
import random

def download_datasets():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_dir = os.path.join(script_dir, '../data/raw')
    os.makedirs(raw_data_dir, exist_ok=True)
    
    print("Downloading benign domains from Tranco...")
    url_benign = 'https://tranco-list.eu/download/K2GGX/1000000'
    try:
        res = requests.get(url_benign, timeout=30)
        if res.status_code == 200:
            df_benign = pd.read_csv(io.StringIO(res.text), names=['rank', 'domain'])
            df_benign = df_benign.head(100000)
            df_benign['label'] = 0
            df_benign[['domain', 'label']].to_csv(os.path.join(raw_data_dir, 'benign.csv'), index=False)
            print("Benign domains saved.")
        else:
            raise Exception("Status code not 200")
    except Exception as e:
        print(f"Error downloading benign domains: {e}. Generating fallback dataset...")
        common = ["google.com", "github.com", "wikipedia.org", "amazon.com", "apple.com", "microsoft.com", "youtube.com"]
        fallback_domains = [random.choice(common) for _ in range(10000)]
        df_benign = pd.DataFrame({'domain': fallback_domains, 'label': 0})
        df_benign.to_csv(os.path.join(raw_data_dir, 'benign.csv'), index=False)
        print("Fallback benign domains saved.")
    
    print("Generating sample DGA malicious domains...")
    domains = []
    for _ in range(50000):
        length = random.randint(10, 25)
        domain = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=length)) + '.com'
        domains.append(domain)
    df_malicious = pd.DataFrame({'domain': domains, 'label': 1})
    df_malicious.to_csv(os.path.join(raw_data_dir, 'malicious.csv'), index=False)
    print("Malicious domains saved.")

if __name__ == '__main__':
    download_datasets()
