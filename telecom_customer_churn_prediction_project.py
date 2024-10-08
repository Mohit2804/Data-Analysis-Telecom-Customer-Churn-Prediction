pip install shap

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_curve, roc_curve, auc
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.inspection import permutation_importance
from xgboost import XGBClassifier
import shap
from wordcloud import WordCloud
import datetime
import warnings
warnings.filterwarnings("ignore")

# Load the dataset
df = pd.read_csv("/content/sample_data/telecom_customer_churn.csv")

# Display basic information about the dataset
print("Dataset Information:")
df.info()
print("\nFirst 5 Rows:")
df.head()

# Check for missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Drop duplicates
df = df.drop_duplicates()

# Fill missing values
df = df.fillna(0)

# Drop unnecessary columns
columns_to_drop = ['Customer ID', 'City', 'Zip Code', 'Latitude', 'Longitude',
                   'Churn Category']
df = df.drop(columns=columns_to_drop)

df.info()

# Exploratory Data Analysis (EDA)

# Summary statistics
print("\nSummary Statistics:")
df.describe()

# Distribution of Customer Status (Churn)
plt.figure(figsize=(8, 6))
sns.countplot(x='Customer Status', data=df)
plt.title('Distribution of Customer Status')
plt.show()

import matplotlib.pyplot as plt
import seaborn as sns

# Calculate total revenue per customer status
revenue_per_status = df.groupby('Customer Status')['Total Revenue'].sum().reset_index()

# Create the plot
plt.figure(figsize=(8, 6))
sns.barplot(x='Customer Status', y='Total Revenue', data=revenue_per_status)

# Adding the title and labels
plt.title('Total Revenue by Customer Status')
plt.xlabel('Customer Status')
plt.ylabel('Total Revenue')

# bars with the total revenue values
for index, row in revenue_per_status.iterrows():
    plt.text(index, row['Total Revenue'] + row['Total Revenue']*0.02, f"${row['Total Revenue']:.2f}",
             color='black', ha="center", fontsize=12)

# Show the plot
plt.show()

# Monthly Charge vs Churn
plt.figure(figsize=(8, 6))
sns.boxplot(x='Customer Status', y='Monthly Charge', data=df)
plt.title('Monthly Charge vs Churn')
plt.show()

# Word Cloud for Churn Reasons
plt.figure(figsize=(10, 5))
text = ' '.join(df['Churn Reason'].dropna().astype(str))
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud of Churn Reasons')
plt.show()

# Data Preparation for Modeling

# Prepare features (X) and target (y)
X = df.drop('Customer Status', axis=1)
y = df['Customer Status']

# One-Hot Encoding for categorical variables
X = pd.get_dummies(X, drop_first=True)

# Label Encoding for the target variable
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

# Ensure all features are numeric
X = X.apply(pd.to_numeric, errors='coerce')

# Handle missing values (if any were coerced to NaN)
X = X.fillna(X.mean())

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Model Training: XGBoost Classifier
model = XGBClassifier()
model.fit(X_train, y_train)

# Model Evaluation

# Predictions
y_pred = model.predict(X_test)

# Classification Report
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Confusion Matrix
conf_matrix = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()

# ROC Curve and AUC
y_prob = model.predict_proba(X_test)
fpr, tpr, _ = roc_curve(y_test, y_prob[:, 1], pos_label=1)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.show()

# SHAP Values for Model Interpretation
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Plot SHAP values for the each class
for i in range(shap_values.shape[2]):  # Loop through each class
    print(f"SHAP Summary Plot for Class {i}")
    shap.summary_plot(shap_values[:, :, i], X_test)

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Convert 'Customer Status' to binary for easier analysis: 1 for 'Churned', 0 for others
df['Churn'] = df['Customer Status'].apply(lambda x: 1 if x == 'Churned' else 0)

# Function to plot churn percentage by a categorical feature
def plot_churn_percentage_by_category(df, category, title):
    # Calculate the churn percentage by category
    churn_percentage = df.groupby(category)['Churn'].mean() * 100

    # Create the bar plot
    sns.barplot(x=churn_percentage.index, y=churn_percentage.values)
    plt.title(f'Churn Percentage by {title}')
    plt.ylabel('Churn Percentage (%)')
    plt.xlabel(category)
    plt.xticks(rotation=45)
    plt.show()

# Churn percentage by Gender
plot_churn_percentage_by_category(df, 'Gender', 'Gender')

# Churn percentage by Internet Type
plot_churn_percentage_by_category(df, 'Internet Type', 'Internet Type')

# Churn percentage by Contract Type
plot_churn_percentage_by_category(df, 'Contract', 'Contract Type')

# Churn percentage by Married
plot_churn_percentage_by_category(df, 'Married', 'Married')

# Churn percentage by Number of Dependents
plot_churn_percentage_by_category(df, 'Number of Dependents', 'Number of Dependents')

# Churn percentage by Offer
plot_churn_percentage_by_category(df, 'Offer', 'Offer')

# Additional Analysis: Customer Segmentation using K-Means Clustering

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# K-Means Clustering
kmeans = KMeans(n_clusters=5, random_state=42)
clusters = kmeans.fit_predict(X_scaled)
df['Cluster'] = clusters

# Visualize clusters
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Monthly Charge', y='Total Charges', hue='Cluster', data=df, palette='viridis')
plt.title('Customer Segmentation by Monthly Charge and Total Charges')
plt.show()

# Hyperparameter Tuning using GridSearchCV (Additional, just used to optimize the model to achieve the best possible performance)
param_grid = {
    'n_estimators': [100, 200],
    'learning_rate': [0.01, 0.1],
    'max_depth': [3, 5],
    'min_child_weight': [1, 3]
}

grid_search = GridSearchCV(XGBClassifier(), param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)
best_params = grid_search.best_params_

print("Best Parameters from GridSearchCV:", best_params)

# Re-train the model with the best parameters
model = XGBClassifier(**best_params)
model.fit(X_train, y_train)

from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt
import seaborn as sns

# Predict on the test set
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)

# Classification report
report = classification_report(y_test, y_pred)
print("Classification Report:")
print(report)

# Confusion matrix
conf_matrix = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(conf_matrix)

# Plot confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()

# ROC Curve and AUC
fpr, tpr, _ = roc_curve(y_test, y_prob[:, 1], pos_label=1)
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.show()

import shap

# Explain model predictions using SHAP
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Determine if the problem is multiclass or binary
if isinstance(shap_values, list):
    # Multiclass case: shap_values is a list where each element corresponds to a class
  for i in range(shap_values.shape[2]):  # Loop through each class
    print(f"SHAP Summary Plot for Class {i}")
    shap.summary_plot(shap_values[:, :, i], X_test)
else:
    # Binary case: shap_values is a single array
    shap.summary_plot(shap_values, X_test)
