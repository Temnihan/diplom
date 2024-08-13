import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

def get_data_from_db(user_id):
    conn = sqlite3.connect('users1.db')
    query = f"SELECT num1, num2, d1, d2, ones, width, is_correct FROM user_{user_id}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def train_model(data):
    X = data[['num1', 'num2', 'd1', 'd2', 'ones', 'width']]
    y = data['is_correct']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy * 100:.2f}%")
    return model

def update_model_after_answer(user_id):
    data = get_data_from_db(user_id)
    model = train_model(data)
    return model

def predict_category(model, num1, num2, d1, d2, ones, width):
    return model.predict([[num1, num2, d1, d2, ones, width]])[0]
