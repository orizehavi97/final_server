"""Streamlit user interface for ML model training and predictions."""
import streamlit as st
import pandas as pd
import requests
import json
import os
from typing import Optional

# Configuration
# Use environment variable for Docker, fallback to localhost for local development
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="ML Server - User Interface",
    page_icon="🤖",
    layout="wide"
)

# Session state initialization
if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "token_balance" not in st.session_state:
    st.session_state.token_balance = None


def login(username: str, password: str) -> Optional[str]:
    """Login and get JWT token."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            # Fetch initial token balance after successful login
            balance = get_token_balance(token)
            if balance is not None:
                st.session_state.token_balance = balance
            return token
        else:
            st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None


def signup(username: str, password: str) -> bool:
    """Create a new user account."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/signup",
            json={"username": username, "password": password}
        )
        if response.status_code == 201:
            return True
        else:
            st.error(f"Signup failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return False


def get_token_balance(token: str) -> Optional[int]:
    """Get user's token balance."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/tokens",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()["tokens"]
        return None
    except:
        return None


def add_tokens(token: str, credit_card: str, amount: int) -> bool:
    """Purchase tokens."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/add_tokens",
            headers={"Authorization": f"Bearer {token}"},
            json={"credit_card": credit_card, "amount": amount}
        )
        return response.status_code == 200
    except:
        return False


def train_model(token: str, file, model_name: str, model_type: str, features: list, label: str) -> Optional[dict]:
    """Train a model."""
    try:
        files = {"file": file}
        data = {
            "model_name": model_name,
            "model_type": model_type,
            "features": json.dumps(features),
            "label": label
        }
        response = requests.post(
            f"{API_BASE_URL}/train",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
            data=data
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Training failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def make_prediction(token: str, model_name: str, features: dict) -> Optional[float]:
    """Make a prediction."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict/{model_name}",
            headers={"Authorization": f"Bearer {token}"},
            json=features
        )
        if response.status_code == 200:
            return response.json()["prediction"]
        else:
            st.error(f"Prediction failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def get_models(token: str) -> Optional[list]:
    """Get list of trained models."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/models",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()["models"]
        return None
    except:
        return None


def logout():
    """Logout user."""
    st.session_state.jwt_token = None
    st.session_state.username = None


# Main UI
st.title("🤖 ML Server - User Interface")

# Authentication section
if st.session_state.jwt_token is None:
    st.markdown("### 🔐 Please Login or Sign Up")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.markdown("#### Login to your account")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", type="primary"):
            if login_username and login_password:
                token = login(login_username, login_password)
                if token:
                    st.session_state.jwt_token = token
                    st.session_state.username = login_username
                    st.success("✅ Logged in successfully!")
                    st.rerun()
            else:
                st.warning("Please enter username and password")

    with tab2:
        st.markdown("#### Create a new account")
        signup_username = st.text_input("Username", key="signup_user")
        signup_password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Sign Up", type="primary"):
            if signup_username and signup_password:
                if signup(signup_username, signup_password):
                    st.success("✅ Account created! Please login.")
            else:
                st.warning("Please enter username and password")

else:
    # Logged in UI
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"### Welcome, **{st.session_state.username}**! 👋")

    with col2:
        # Display token balance from session state
        if st.session_state.token_balance is not None:
            st.metric("Token Balance", f"{st.session_state.token_balance} 🪙")
        else:
            st.metric("Token Balance", "-- 🪙")

    with col3:
        if st.button("Logout", type="secondary"):
            logout()
            st.rerun()

    st.markdown("---")

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Train Model", "🎯 Make Prediction", "🤖 My Models", "💳 Buy Tokens"])

    with tab1:
        st.markdown("### 📊 Train a New Model")
        st.markdown("Upload a CSV file and train a machine learning model.")

        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

        if uploaded_file is not None:
            # Preview data
            df = pd.read_csv(uploaded_file)
            st.markdown("#### Data Preview")
            st.dataframe(df.head(10), use_container_width=True)

            st.markdown("#### Model Configuration")

            col1, col2 = st.columns(2)

            with col1:
                model_name = st.text_input("Model Name", placeholder="e.g., my_model")
                model_type = st.selectbox(
                    "Model Type",
                    [
                        "linear_regression",
                        "random_forest_regressor",
                        "svr",
                        "logistic_regression",
                        "random_forest_classifier",
                        "svc"
                    ]
                )

            with col2:
                all_columns = df.columns.tolist()
                features = st.multiselect("Select Features", all_columns)
                label = st.selectbox("Select Label (Target)", all_columns)

            if st.button("🚀 Train Model", type="primary"):
                if model_name and features and label:
                    if label in features:
                        st.error("Label cannot be in features!")
                    else:
                        with st.spinner("Training model... This may take a moment."):
                            uploaded_file.seek(0)  # Reset file pointer
                            result = train_model(
                                st.session_state.jwt_token,
                                uploaded_file,
                                model_name,
                                model_type,
                                features,
                                label
                            )
                            if result:
                                st.success(f"✅ Model '{model_name}' trained successfully!")
                                # Update token balance after successful training
                                balance = get_token_balance(st.session_state.jwt_token)
                                if balance is not None:
                                    st.session_state.token_balance = balance
                                st.markdown("#### Evaluation Metrics")
                                metrics = result.get("metrics", {})
                                metric_cols = st.columns(len(metrics))
                                for i, (key, value) in enumerate(metrics.items()):
                                    with metric_cols[i]:
                                        st.metric(key.upper(), f"{value:.4f}")
                                st.json(result)
                else:
                    st.warning("Please fill in all fields")

    with tab2:
        st.markdown("### 🎯 Make a Prediction")
        st.markdown("Use a trained model to make predictions.")

        # Initialize session state
        if "prediction_models" not in st.session_state:
            st.session_state.prediction_models = None

        # Button to explicitly load models
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("📋 Load Models", key="load_predict_models"):
                st.session_state.prediction_models = get_models(st.session_state.jwt_token)
                # Update token balance after loading models
                balance = get_token_balance(st.session_state.jwt_token)
                if balance is not None:
                    st.session_state.token_balance = balance

        models = st.session_state.prediction_models

        if models is None:
            st.info("👆 Click 'Load Models' to see your trained models and make predictions.")
        elif len(models) == 0:
            st.info("No trained models found. Please train a model first!")
        else:
            model_names = [m["model_name"] for m in models]
            selected_model_name = st.selectbox("Select Model", model_names)

            # Find selected model details
            selected_model = next((m for m in models if m["model_name"] == selected_model_name), None)

            if selected_model:
                st.markdown(f"**Model Type**: {selected_model['model_type']}")
                st.markdown(f"**Features**: {', '.join(selected_model['features'])}")
                st.markdown(f"**Label**: {selected_model['label']}")

                if selected_model.get('metrics'):
                    st.markdown("**Metrics**:")
                    metric_cols = st.columns(len(selected_model['metrics']))
                    for i, (key, value) in enumerate(selected_model['metrics'].items()):
                        with metric_cols[i]:
                            st.metric(key.upper(), f"{value:.4f}")

                st.markdown("#### Enter Feature Values")

                feature_values = {}
                cols = st.columns(2)
                for i, feature in enumerate(selected_model['features']):
                    with cols[i % 2]:
                        feature_values[feature] = st.number_input(
                            f"{feature}",
                            value=0.0,
                            key=f"feature_{feature}"
                        )

                if st.button("🎯 Predict", type="primary"):
                    with st.spinner("Making prediction..."):
                        prediction = make_prediction(
                            st.session_state.jwt_token,
                            selected_model_name,
                            feature_values
                        )
                        if prediction is not None:
                            st.success("✅ Prediction complete!")
                            # Update token balance after successful prediction
                            balance = get_token_balance(st.session_state.jwt_token)
                            if balance is not None:
                                st.session_state.token_balance = balance
                            st.markdown(f"### Predicted {selected_model['label']}: **{prediction:.2f}**")

    with tab3:
        st.markdown("### 🤖 My Trained Models")

        # Initialize session state
        if "my_models" not in st.session_state:
            st.session_state.my_models = None

        # Button to load/refresh models
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("📋 Load Models", key="load_my_models"):
                st.session_state.my_models = get_models(st.session_state.jwt_token)
                # Update token balance after loading models
                balance = get_token_balance(st.session_state.jwt_token)
                if balance is not None:
                    st.session_state.token_balance = balance

        models = st.session_state.my_models

        if models is None:
            st.info("👆 Click 'Load Models' to view all your trained models.")
        elif len(models) == 0:
            st.info("No models found. Train your first model!")
        else:
            for model in models:
                with st.expander(f"📦 {model['model_name']} ({model['model_type']})"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"**Type**: {model['model_type']}")
                        st.markdown(f"**Features**: {', '.join(model['features'])}")
                        st.markdown(f"**Label**: {model['label']}")
                        st.markdown(f"**Trained**: {model['trained_at']}")

                    with col2:
                        if model.get('metrics'):
                            st.markdown("**Evaluation Metrics**:")
                            for key, value in model['metrics'].items():
                                st.markdown(f"- **{key.upper()}**: {value:.4f}")

    with tab4:
        st.markdown("### 💳 Purchase Tokens")
        st.markdown("Add tokens to your account to use ML operations.")

        st.info("**Token Costs**: Training = 1 token | Prediction = 5 tokens | View Models/Metrics = 1 token")

        col1, col2 = st.columns(2)

        with col1:
            credit_card = st.text_input("Credit Card Number", placeholder="1234-5678-9999-0000")
            amount = st.number_input("Amount of Tokens", min_value=1, max_value=1000, value=10)

        with col2:
            st.markdown("#### Purchase Summary")
            st.markdown(f"**Tokens to purchase**: {amount}")
            current_balance = st.session_state.token_balance if st.session_state.token_balance is not None else 0
            st.markdown(f"**Current balance**: {current_balance} tokens")
            st.markdown(f"**New balance**: {current_balance + amount} tokens")

        if st.button("💳 Purchase Tokens", type="primary"):
            if credit_card:
                with st.spinner("Processing payment..."):
                    if add_tokens(st.session_state.jwt_token, credit_card, amount):
                        st.success(f"✅ Successfully added {amount} tokens!")
                        # Update token balance after successful purchase
                        balance = get_token_balance(st.session_state.jwt_token)
                        if balance is not None:
                            st.session_state.token_balance = balance
                        st.rerun()
                    else:
                        st.error("Payment failed. Please check your card details.")
            else:
                st.warning("Please enter credit card number")

# Footer
st.markdown("---")
st.markdown("🤖 **ML Server User Interface** | Built with Streamlit")
