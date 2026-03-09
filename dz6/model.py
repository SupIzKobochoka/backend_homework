import numpy as np
from sklearn.linear_model import LogisticRegression
import mlflow
from mlflow.sklearn import log_model
from mlflow.exceptions import MlflowException

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("moderation-model")

def train_model() -> LogisticRegression:
    """Обучает простую модель на синтетических данных."""
    np.random.seed(42)
    # Признаки: [is_verified_seller, images_qty, description_length, category]
    X = np.random.rand(1000, 4)
    # Целевая переменная: 1 = нарушение, 0 = нет нарушения
    y = (X[:, 0] < 0.3) & (X[:, 1] < 0.2)
    y = y.astype(int)
    
    model = LogisticRegression()
    model.fit(X, y)
    return model

def save_model(model, model_name='base_model') -> None:
    with mlflow.start_run():
        log_model(model, 'model', registered_model_name=model_name)

def load_model(model_name: str = 'base_model', stage: str = None):
    model_uri = f"models:/{model_name}/{stage}"
    return mlflow.sklearn.load_model(model_uri)

def load_or_train_model(model_name: str = 'base_model', stage: str = None):
    try:
        model =  mlflow.sklearn.load_model(f"models:/{model_name}/{stage}")
    except MlflowException:
        model = train_model()
        save_model(model, model_name=model_name)
    return model

def get_pred(model: LogisticRegression, ad: dict) -> dict:
    '''
    return: {is_violation: int, probability: float}
    '''
    cols = {'is_verified_seller': lambda x: float(x), 
            'images_qty': lambda x: x/10, 
            'description': lambda x: len(x)/1000, 
            'category': lambda x: x/100}
    
    data = [[cols[col](ad[col]) for col in cols]]
    proba = model.predict_proba(data)[0, 1].item()
    target = bool(model.predict(data).item())
    return {'is_violation': target, 'probability': proba}

