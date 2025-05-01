from firebase_handler import get_realtime_db
from model_trainer.train_7d_model import train_and_predict_7d

def predict_and_save(symbol, key, category="NIFTY"):
    preds = train_and_predict_7d(symbol, key)
    db_root = get_realtime_db().child("predictions/7days")
    today = __import__('datetime').datetime.now().strftime("%Y-%m-%d")
    path = f"{category}/{symbol}/{today}"
    db_root.child(path).set(list(preds))
    return preds
