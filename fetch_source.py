"""Optional exact-byte re-download of the public source (not needed for bundled run)."""
from pathlib import Path
import hashlib,urllib.request
URL='https://raw.githubusercontent.com/aplbrain/seismic/1a789eefc2ca03c1f79e283069e41d20d12ed91f/neuroaiengines/networks/hemibrain_conn_df_both.csv'
SHA='0ef25fab90a598160235b48c30ac7af895289750df19536e30e9047d8833261f'
def main():
 with urllib.request.urlopen(URL,timeout=60) as response:content=response.read()
 if hashlib.sha256(content).hexdigest()!=SHA:raise ValueError('Source checksum mismatch: refusing replacement')
 (Path(__file__).resolve().parent/'data/hemibrain_conn_df_both.csv').write_bytes(content)
 print('Exact source checksum verified.')
if __name__=='__main__':main()
