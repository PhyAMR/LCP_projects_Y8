# Function to train LightGBM model.
from dacite.generics import orig
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import re

def train_model_lgb(df, features, target, params, stratify=False):
    """
    Train a LightGBM classifier on the given dataframe, features, and target.
    Returns the trained model and test set predictions.
    """
    def clean_name(text):
        # 1. Replace :, /, +, and , with _
        # 2. Remove ( and )
        text2 = re.sub(r'[:/+,]', '_', text)
        text = re.sub(r'[()]', '', text2)
        return text
    orig_df_columns = df.columns.tolist()  # Store original column names.
    # Apply to list of features
    df.columns = [clean_name(col) for col in df.columns]
    features_clean = [clean_name(fea) for fea in features]

    # Apply to target string
    target = clean_name(target)
    X = df[features_clean]
    y = df[target]
    
    # Train/test sets.
    if stratify:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Define LightGBM classifier.
    #params = {'objective': 'binary', # Because our classification is about if it evolves or not.
    #          'boosting_type': 'gbdt', # Gradient Boosting Decision Tree.
    #          'learning_rate': 0.05,
    #          'num_leaves': 31, # We allow up to 31 leaves so the model can capture different combinations of parameters.
    #          'n_estimators': 300, # Improvements (of the previous model).
    #          'verbose': -1}
    
    model = lgb.LGBMClassifier(**params)
    model.fit(X_train, y_train)
    
    # Model acccuracy.
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print("Accuracy:", acc)
    df.columns = orig_df_columns  # Restore original column names.
    
    return model, X_test, y_test, y_pred