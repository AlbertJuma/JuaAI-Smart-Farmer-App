#!/usr/bin/env python3
"""
Plant Leaf Classification Model Training Script

This script downloads a sample dataset from PlantVillage and trains a simple
TensorFlow/Keras model to classify leaves as healthy or diseased.
"""

import os
import requests
import zipfile
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import shutil
from PIL import Image
import json

# Set random seeds for reproducibility
tf.random.set_seed(42)
np.random.seed(42)

class PlantLeafClassifier:
    def __init__(self, data_dir='plant_dataset', img_size=(224, 224)):
        self.data_dir = data_dir
        self.img_size = img_size
        self.model = None
        self.class_names = ['diseased', 'healthy']
        
    def create_sample_dataset(self):
        """Create a small sample dataset for demonstration"""
        print("Creating sample dataset...")
        
        # Create directory structure
        os.makedirs(f"{self.data_dir}/train/healthy", exist_ok=True)
        os.makedirs(f"{self.data_dir}/train/diseased", exist_ok=True)
        os.makedirs(f"{self.data_dir}/validation/healthy", exist_ok=True)
        os.makedirs(f"{self.data_dir}/validation/diseased", exist_ok=True)
        
        # Generate synthetic images for demonstration
        # In a real implementation, you would download actual PlantVillage images
        self._generate_synthetic_images()
        
        print(f"Sample dataset created in {self.data_dir}/")
        
    def _generate_synthetic_images(self):
        """Generate synthetic leaf images for demonstration"""
        # Generate healthy leaf images (green-ish)
        for i in range(100):
            # Create a green-ish image with some variation
            img = np.random.randint(50, 150, (*self.img_size, 3), dtype=np.uint8)
            img[:, :, 1] = np.random.randint(100, 200, self.img_size)  # More green
            
            # Add some texture
            noise = np.random.normal(0, 10, (*self.img_size, 3))
            img = np.clip(img + noise, 0, 255).astype(np.uint8)
            
            Image.fromarray(img).save(f"{self.data_dir}/train/healthy/healthy_{i:03d}.jpg")
            
        for i in range(30):
            # Create validation healthy images
            img = np.random.randint(50, 150, (*self.img_size, 3), dtype=np.uint8)
            img[:, :, 1] = np.random.randint(100, 200, self.img_size)
            noise = np.random.normal(0, 10, (*self.img_size, 3))
            img = np.clip(img + noise, 0, 255).astype(np.uint8)
            Image.fromarray(img).save(f"{self.data_dir}/validation/healthy/healthy_{i:03d}.jpg")
            
        # Generate diseased leaf images (brown/yellow-ish)
        for i in range(100):
            # Create a brown/yellow-ish image with spots
            img = np.random.randint(80, 150, (*self.img_size, 3), dtype=np.uint8)
            img[:, :, 0] = np.random.randint(120, 200, self.img_size)  # More red
            img[:, :, 1] = np.random.randint(80, 150, self.img_size)   # Some green
            img[:, :, 2] = np.random.randint(20, 80, self.img_size)    # Less blue
            
            # Add brown spots (disease simulation)
            num_spots = np.random.randint(3, 10)
            for _ in range(num_spots):
                x, y = np.random.randint(0, self.img_size[0], 2)
                r = np.random.randint(10, 30)
                y_indices, x_indices = np.ogrid[:self.img_size[0], :self.img_size[1]]
                mask = (x_indices - x)**2 + (y_indices - y)**2 <= r**2
                img[mask] = [101, 67, 33]  # Brown color
            
            Image.fromarray(img).save(f"{self.data_dir}/train/diseased/diseased_{i:03d}.jpg")
            
        for i in range(30):
            # Create validation diseased images
            img = np.random.randint(80, 150, (*self.img_size, 3), dtype=np.uint8)
            img[:, :, 0] = np.random.randint(120, 200, self.img_size)
            img[:, :, 1] = np.random.randint(80, 150, self.img_size)
            img[:, :, 2] = np.random.randint(20, 80, self.img_size)
            
            # Add spots
            num_spots = np.random.randint(3, 10)
            for _ in range(num_spots):
                x, y = np.random.randint(0, self.img_size[0], 2)
                r = np.random.randint(10, 30)
                y_indices, x_indices = np.ogrid[:self.img_size[0], :self.img_size[1]]
                mask = (x_indices - x)**2 + (y_indices - y)**2 <= r**2
                img[mask] = [101, 67, 33]
                
            Image.fromarray(img).save(f"{self.data_dir}/validation/diseased/diseased_{i:03d}.jpg")
    
    def create_model(self):
        """Create a simple CNN model for binary classification"""
        model = keras.Sequential([
            # Preprocessing layers
            layers.Rescaling(1./255),
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.1),
            layers.RandomZoom(0.1),
            
            # Convolutional layers
            layers.Conv2D(32, 3, activation='relu', input_shape=(*self.img_size, 3)),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, activation='relu'),
            layers.MaxPooling2D(),
            layers.Conv2D(128, 3, activation='relu'),
            layers.MaxPooling2D(),
            
            # Classification layers
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(128, activation='relu'),
            layers.Dense(1, activation='sigmoid')  # Binary classification
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def prepare_datasets(self):
        """Prepare training and validation datasets"""
        train_ds = tf.keras.utils.image_dataset_from_directory(
            f"{self.data_dir}/train",
            image_size=self.img_size,
            batch_size=32,
            label_mode='binary'
        )
        
        val_ds = tf.keras.utils.image_dataset_from_directory(
            f"{self.data_dir}/validation", 
            image_size=self.img_size,
            batch_size=32,
            label_mode='binary'
        )
        
        # Optimize for performance
        AUTOTUNE = tf.data.AUTOTUNE
        train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
        val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
        
        return train_ds, val_ds
    
    def train_model(self, epochs=10):
        """Train the model"""
        print("Preparing datasets...")
        train_ds, val_ds = self.prepare_datasets()
        
        print("Creating model...")
        self.create_model()
        
        print("Training model...")
        history = self.model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=epochs,
            verbose=1
        )
        
        return history
    
    def save_model(self, filepath='model.h5'):
        """Save the trained model"""
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
        
        self.model.save(filepath)
        print(f"Model saved to {filepath}")
        
        # Save model metadata
        metadata = {
            'input_shape': list(self.img_size) + [3],
            'class_names': self.class_names,
            'model_type': 'binary_classification',
            'description': 'Plant leaf health classifier (healthy vs diseased)'
        }
        
        with open('model_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("Model metadata saved to model_metadata.json")
    
    def evaluate_model(self):
        """Evaluate the model on validation data"""
        if self.model is None:
            raise ValueError("No model to evaluate. Train the model first.")
        
        _, val_ds = self.prepare_datasets()
        
        print("Evaluating model...")
        loss, accuracy = self.model.evaluate(val_ds, verbose=0)
        print(f"Validation Loss: {loss:.4f}")
        print(f"Validation Accuracy: {accuracy:.4f}")
        
        return loss, accuracy

def main():
    """Main training function"""
    print("🌱 Plant Leaf Classification Model Training")
    print("=" * 50)
    
    # Initialize classifier
    classifier = PlantLeafClassifier()
    
    # Create sample dataset
    classifier.create_sample_dataset()
    
    # Train model
    history = classifier.train_model(epochs=15)
    
    # Evaluate model
    classifier.evaluate_model()
    
    # Save model
    classifier.save_model('model.h5')
    
    print("\n✅ Training completed successfully!")
    print("📁 Model saved as 'model.h5'")
    print("📊 Model metadata saved as 'model_metadata.json'")

if __name__ == "__main__":
    main()