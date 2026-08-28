import pandas as pd
import sys
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Add backend directory to sys.path to import extract_features
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from app.ml.features import extract_features

def train():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_dir = os.path.join(script_dir, '../data/raw')
    
    print("Loading data...")
    df_benign = pd.read_csv(os.path.join(raw_data_dir, 'benign.csv'))
    df_malicious = pd.read_csv(os.path.join(raw_data_dir, 'malicious.csv'))
    
    df = pd.concat([df_benign, df_malicious], ignore_index=True)
    
    print("Extracting features (this may take a while)...")
    features = []
    labels = []
    for _, row in df.iterrows():
        try:
            feat_dict = extract_features(row['domain'])
            features.append(feat_dict)
            labels.append(row['label'])
        except Exception as e:
            continue
            
    X = pd.DataFrame(features)
    y = pd.Series(labels)
    
    print("Training RandomForestClassifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    print("Evaluating model...")
    y_pred = model.predict(X)
    print(classification_report(y, y_pred))
    
    model_dir = os.path.abspath(os.path.join(script_dir, '../../backend/app/ml/models'))
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'domain_classifier.joblib')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == '__main__':
    train()
