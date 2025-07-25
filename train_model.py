#!/usr/bin/env python3
"""
Model training script for plant leaf classification.
Trains a TensorFlow/Keras model to classify leaves as healthy or diseased.
"""

import os
import numpy as np
from PIL import Image
import json

# Try to import TensorFlow
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from sklearn.model_selection import train_test_split
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("Warning: TensorFlow not available. Creating mock model for demonstration.")

class PlantLeafClassifier:
    def __init__(self, input_shape=(224, 224, 3), num_classes=2):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = None
        self.class_names = ['healthy', 'diseased']
    
    def create_model(self):
        """Create a simple CNN model for leaf classification."""
        if not TF_AVAILABLE:
            print("TensorFlow not available. Cannot create real model.")
            return None
            
        model = keras.Sequential([
            # Data augmentation
            layers.RandomFlip("horizontal", input_shape=self.input_shape),
            layers.RandomRotation(0.1),
            layers.RandomZoom(0.1),
            
            # Feature extraction
            layers.Rescaling(1./255),
            layers.Conv2D(32, 3, activation='relu'),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, activation='relu'),
            layers.MaxPooling2D(),
            layers.Conv2D(128, 3, activation='relu'),
            layers.MaxPooling2D(),
            
            # Classification
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(128, activation='relu'),
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def load_data(self, dataset_dir):
        """Load and prepare data from dataset directory."""
        processed_dir = os.path.join(dataset_dir, "processed")
        
        if not os.path.exists(processed_dir):
            print("Processed dataset not found. Please run prepare_dataset.py first.")
            return None, None, None, None
        
        images = []
        labels = []
        
        # Load healthy images (label 0)
        healthy_dir = os.path.join(processed_dir, "healthy")
        if os.path.exists(healthy_dir):
            for filename in os.listdir(healthy_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(healthy_dir, filename)
                    try:
                        img = Image.open(img_path)
                        img_array = np.array(img)
                        if img_array.shape == self.input_shape:
                            images.append(img_array)
                            labels.append(0)  # healthy
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
        
        # Load diseased images (label 1)
        diseased_dir = os.path.join(processed_dir, "diseased")
        if os.path.exists(diseased_dir):
            for filename in os.listdir(diseased_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(diseased_dir, filename)
                    try:
                        img = Image.open(img_path)
                        img_array = np.array(img)
                        if img_array.shape == self.input_shape:
                            images.append(img_array)
                            labels.append(1)  # diseased
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
        
        if not images:
            print("No valid images found in dataset!")
            return None, None, None, None
        
        images = np.array(images)
        labels = np.array(labels)
        
        print(f"Loaded {len(images)} images:")
        print(f"- Healthy: {np.sum(labels == 0)}")
        print(f"- Diseased: {np.sum(labels == 1)}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            images, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        return X_train, X_test, y_train, y_test
    
    def create_synthetic_data(self):
        """Create synthetic data for demonstration when real data is limited."""
        print("Creating synthetic training data for demonstration...")
        
        # Generate synthetic images
        X_train = []
        y_train = []
        
        # Generate 50 healthy samples
        for i in range(50):
            # Create green-ish images with random variations
            img = np.random.randint(50, 150, self.input_shape)
            img[:, :, 1] = np.random.randint(100, 200, (self.input_shape[0], self.input_shape[1]))  # More green
            img[:, :, 0] = img[:, :, 0] * 0.8  # Less red
            img[:, :, 2] = img[:, :, 2] * 0.8  # Less blue
            X_train.append(img)
            y_train.append(0)  # healthy
        
        # Generate 50 diseased samples
        for i in range(50):
            # Create brown-ish images with random variations
            img = np.random.randint(80, 180, self.input_shape)
            img[:, :, 0] = np.random.randint(100, 200, (self.input_shape[0], self.input_shape[1]))  # More red
            img[:, :, 1] = img[:, :, 1] * 0.7  # Less green
            img[:, :, 2] = img[:, :, 2] * 0.5  # Much less blue
            X_train.append(img)
            y_train.append(1)  # diseased
        
        X_train = np.array(X_train, dtype=np.float32)
        y_train = np.array(y_train)
        
        # Create test split
        X_test = X_train[-20:]
        y_test = y_train[-20:]
        X_train = X_train[:-20]
        y_train = y_train[:-20]
        
        return X_train, X_test, y_train, y_test
    
    def train(self, dataset_dir=None, epochs=10, batch_size=32):
        """Train the model."""
        if not TF_AVAILABLE:
            print("TensorFlow not available. Creating mock model files...")
            self.create_mock_model()
            return None
            
        if dataset_dir and os.path.exists(dataset_dir):
            # Try to load real data first
            X_train, X_test, y_train, y_test = self.load_data(dataset_dir)
            
            if X_train is None:
                # Fall back to synthetic data
                X_train, X_test, y_train, y_test = self.create_synthetic_data()
        else:
            # Use synthetic data
            X_train, X_test, y_train, y_test = self.create_synthetic_data()
        
        # Create model
        self.create_model()
        
        print(f"\nTraining model on {len(X_train)} samples...")
        print(f"Model architecture:")
        self.model.summary()
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            batch_size=batch_size,
            epochs=epochs,
            validation_data=(X_test, y_test),
            verbose=1
        )
        
        # Evaluate model
        test_loss, test_accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"\nTest accuracy: {test_accuracy:.4f}")
        
        return history
    
    def create_mock_model(self):
        """Create mock model files when TensorFlow is not available."""
        # Create a mock model.h5 file (just a placeholder)
        with open('model.h5', 'w') as f:
            f.write('# Mock model file for demonstration\n')
            f.write('# This would contain the actual TensorFlow model in a real deployment\n')
        
        print("Mock model.h5 created for demonstration")
    
    def save_model(self, filepath="model.h5"):
        """Save the trained model."""
        if not TF_AVAILABLE:
            # Already handled in create_mock_model
            pass
        elif self.model is None:
            print("No model to save. Please train the model first.")
            return
        else:
            self.model.save(filepath)
            print(f"Model saved to {filepath}")
        
        # Save model info
        model_info = {
            'class_names': self.class_names,
            'input_shape': self.input_shape,
            'num_classes': self.num_classes,
            'tensorflow_available': TF_AVAILABLE
        }
        
        with open('model_info.json', 'w') as f:
            json.dump(model_info, f, indent=2)
        print("Model info saved to model_info.json")
    
    def predict(self, image_array):
        """Make prediction on a single image."""
        if self.model is None:
            print("No model loaded. Please train or load a model first.")
            return None
        
        # Ensure image is the right shape
        if len(image_array.shape) == 3:
            image_array = np.expand_dims(image_array, axis=0)
        
        predictions = self.model.predict(image_array, verbose=0)
        predicted_class = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class])
        
        return {
            'class': self.class_names[predicted_class],
            'confidence': confidence,
            'probabilities': {
                self.class_names[i]: float(predictions[0][i]) 
                for i in range(len(self.class_names))
            }
        }

def main():
    """Main training function."""
    print("=== Plant Leaf Classification Model Training ===")
    
    if not TF_AVAILABLE:
        print("TensorFlow not available. Creating demonstration files...")
        classifier = PlantLeafClassifier()
        classifier.create_mock_model()
        classifier.save_model("model.h5")
        print("\n=== Demo Files Created ===")
        print("Mock model and info files created for demonstration")
        print("The Flask backend will use mock predictions")
        return
    
    # Initialize classifier
    classifier = PlantLeafClassifier()
    
    # Check if dataset exists
    dataset_dir = "dataset"
    if os.path.exists(dataset_dir):
        print(f"Using dataset from {dataset_dir}/")
    else:
        print("No dataset found. Creating synthetic data for demonstration.")
        dataset_dir = None
    
    # Train model
    try:
        history = classifier.train(dataset_dir=dataset_dir, epochs=15)
        
        # Save model
        classifier.save_model("model.h5")
        
        print("\n=== Training Complete ===")
        print("Model saved as 'model.h5'")
        print("Ready to use with Flask backend!")
        
    except Exception as e:
        print(f"Training failed: {e}")
        print("Creating a minimal model for demonstration...")
        
        # Create and save a minimal model for demo
        classifier.create_model()
        classifier.save_model("model.h5")
        print("Demo model saved successfully!")

if __name__ == "__main__":
    main()