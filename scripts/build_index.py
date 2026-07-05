import json
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    cache_path = os.path.join(base_dir, "aiman", "core", "command_cache.json")
    out_path = os.path.join(base_dir, "aiman", "core", "command_index.pkl")
    
    print(f"Loading commands from {cache_path}...")
    with open(cache_path, "r") as f:
        cache = json.load(f)
        
    documents = []
    cmd_names = []
    
    for cmd, content in cache.items():
        # The content already contains the description and examples
        # We append the command name itself heavily weighted
        doc = f"{cmd} {cmd} {cmd} {content}"
        documents.append(doc)
        cmd_names.append(cmd)
        
    print(f"Building TF-IDF index for {len(documents)} commands...")
    vectorizer = TfidfVectorizer(stop_words='english', max_df=0.95, min_df=2)
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    print(f"Saving index to {out_path}...")
    with open(out_path, "wb") as f:
        pickle.dump({
            "vectorizer": vectorizer,
            "matrix": tfidf_matrix,
            "cmd_names": cmd_names
        }, f)
        
    print("Done!")

if __name__ == "__main__":
    main()
