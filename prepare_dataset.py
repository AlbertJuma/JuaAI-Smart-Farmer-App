#!/usr/bin/env python3
"""
Dataset preparation script for PlantVillage dataset.
Downloads and preprocesses a small sample dataset for plant leaf classification.
"""

import os
import requests
import zipfile
import numpy as np
from PIL import Image
import shutil

def create_dataset_structure():
    """Create dataset directory structure."""
    dataset_dir = "dataset"
    
    # Create main dataset directory
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
    
    # Create subdirectories for healthy and diseased
    healthy_dir = os.path.join(dataset_dir, "healthy")
    diseased_dir = os.path.join(dataset_dir, "diseased")
    
    for dir_path in [healthy_dir, diseased_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    
    return dataset_dir, healthy_dir, diseased_dir

def download_sample_images():
    """Download sample images for demonstration."""
    dataset_dir, healthy_dir, diseased_dir = create_dataset_structure()
    
    # Sample URLs for demonstration (these would be replaced with actual PlantVillage URLs)
    sample_images = {
        "healthy": [
            "https://via.placeholder.com/256x256/4CAF50/FFFFFF?text=Healthy+Leaf+1",
            "https://via.placeholder.com/256x256/8BC34A/FFFFFF?text=Healthy+Leaf+2",
            "https://via.placeholder.com/256x256/CDDC39/000000?text=Healthy+Leaf+3",
        ],
        "diseased": [
            "https://via.placeholder.com/256x256/FF5722/FFFFFF?text=Diseased+Leaf+1",
            "https://via.placeholder.com/256x256/F44336/FFFFFF?text=Diseased+Leaf+2",
            "https://via.placeholder.com/256x256/E91E63/FFFFFF?text=Diseased+Leaf+3",
        ]
    }
    
    print("Creating sample dataset for demonstration...")
    
    # Create sample images instead of downloading
    create_sample_images(healthy_dir, diseased_dir)
    
    print(f"Sample dataset created in {dataset_dir}/")
    print(f"- Healthy images: {len(os.listdir(healthy_dir))}")
    print(f"- Diseased images: {len(os.listdir(diseased_dir))}")
    
    return dataset_dir

def create_sample_images(healthy_dir, diseased_dir):
    """Create sample images for training demonstration."""
    from PIL import Image, ImageDraw, ImageFont
    
    # Create healthy leaf samples
    for i in range(5):
        img = Image.new('RGB', (256, 256), color=(76, 175, 80))  # Green
        draw = ImageDraw.Draw(img)
        
        # Add some leaf-like patterns
        draw.ellipse([50, 50, 206, 206], fill=(102, 187, 106))
        draw.ellipse([80, 80, 176, 176], fill=(129, 199, 132))
        
        # Add some texture
        for _ in range(20):
            x, y = np.random.randint(60, 196, 2)
            draw.ellipse([x, y, x+10, y+10], fill=(56, 142, 60))
        
        img.save(os.path.join(healthy_dir, f"healthy_{i+1}.jpg"))
    
    # Create diseased leaf samples
    for i in range(5):
        img = Image.new('RGB', (256, 256), color=(139, 69, 19))  # Brown base
        draw = ImageDraw.Draw(img)
        
        # Add diseased patterns
        draw.ellipse([50, 50, 206, 206], fill=(160, 82, 45))
        draw.ellipse([80, 80, 176, 176], fill=(205, 133, 63))
        
        # Add spots and discoloration
        for _ in range(15):
            x, y = np.random.randint(70, 186, 2)
            size = np.random.randint(5, 20)
            draw.ellipse([x, y, x+size, y+size], fill=(101, 67, 33))
        
        img.save(os.path.join(diseased_dir, f"diseased_{i+1}.jpg"))

def preprocess_images(dataset_dir, target_size=(224, 224)):
    """Preprocess images for training."""
    processed_dir = os.path.join(dataset_dir, "processed")
    
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
        os.makedirs(os.path.join(processed_dir, "healthy"))
        os.makedirs(os.path.join(processed_dir, "diseased"))
    
    # Process each category
    for category in ["healthy", "diseased"]:
        source_dir = os.path.join(dataset_dir, category)
        target_dir = os.path.join(processed_dir, category)
        
        if not os.path.exists(source_dir):
            continue
            
        for filename in os.listdir(source_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                source_path = os.path.join(source_dir, filename)
                target_path = os.path.join(target_dir, filename)
                
                try:
                    # Load and resize image
                    with Image.open(source_path) as img:
                        # Convert to RGB if necessary
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Resize to target size
                        img = img.resize(target_size, Image.Resampling.LANCZOS)
                        
                        # Save processed image
                        img.save(target_path, 'JPEG', quality=95)
                        
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
    
    print(f"Images preprocessed and saved to {processed_dir}/")
    return processed_dir

def main():
    """Main function to prepare dataset."""
    print("=== Plant Leaf Dataset Preparation ===")
    
    # Download and create sample dataset
    dataset_dir = download_sample_images()
    
    # Preprocess images
    processed_dir = preprocess_images(dataset_dir)
    
    print("\n=== Dataset Preparation Complete ===")
    print(f"Original dataset: {dataset_dir}/")
    print(f"Processed dataset: {processed_dir}/")
    print("\nNext step: Run train_model.py to train the classification model")

if __name__ == "__main__":
    main()