import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml_engine import train_model

if __name__ == "__main__":
    print("Training ML Model...")
    success = train_model()
    if success:
        print("Training complete. model.pkl saved.")
    else:
        print("Training failed.")
